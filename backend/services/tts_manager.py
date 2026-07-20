from typing import Dict, Any, Optional
import os
import threading
_RVC_LOCK = threading.Lock()
_SELENIUM_LOCK = threading.Lock()

from voicemaker_api import VoiceMakerAPI
from gemini_tts_api import GeminiTTSProvider

# OpenAIFMProvider requer selenium — import opcional para não quebrar o sistema se não instalado
try:
    from openaifm_api import OpenAIFMProvider
    OPENAIFM_AVAILABLE = True
except Exception as _e:
    OPENAIFM_AVAILABLE = False
    print(f"⚠️ [TTS Manager] OpenAIFM não disponível (Selenium não instalado?): {_e}")

class TTSManager:
    """Gerenciador Unificado de TTS (Modelos 1, 2, 3, 4)"""
    def __init__(self, config_manager):
        self.config = config_manager
        self.voicemaker = VoiceMakerAPI(self.config)
        self.gemini_tts = GeminiTTSProvider(self.config)
        self.openaifm_tts = OpenAIFMProvider(self.config) if OPENAIFM_AVAILABLE else None
        # Estado de bloqueio do OpenAI.fm (limite de IP)
        self._openaifm_bloqueado = False
        self._openaifm_bloqueado_ate = None   # datetime de expiração do bloqueio
        self._openaifm_ip_bloqueado = None    # IP que estava ativo quando o bloqueio ocorreu

    def _obter_ip_externo(self) -> str:
        """Retorna o IP externo atual. Usado para detectar troca de VPN."""
        try:
            import requests as _req
            return _req.get("https://api.ipify.org", timeout=5).text.strip()
        except Exception:
            try:
                import requests as _req
                return _req.get("https://ifconfig.me/ip", timeout=5).text.strip()
            except Exception:
                return ""

    def resetar_bloqueio_openaifm(self):
        """Libera manualmente o bloqueio do OpenAI.fm (ex: após reconectar VPN)."""
        self._openaifm_bloqueado = False
        self._openaifm_bloqueado_ate = None
        self._openaifm_ip_bloqueado = None
        if self.openaifm_tts:
            self.openaifm_tts._usando_vpn = False  # reseta estado do proxy também
        print("✅ [Modo 4] Bloqueio OpenAI.fm resetado manualmente.")
    
    def generate_audio(self, character_name: str, text: str, output_path: str, **kwargs) -> bool:
        """Wrapper que gera o aúdio e aplica o Hook de Polimento IA se configurado e necessário."""
        success = self._generate_audio_internal(character_name, text, output_path, **kwargs)
        
        if success and os.path.exists(output_path):
            modelo_tts = int(kwargs.get("_modelo_override", None) or self.config.get("global_tts_model", 1))
            audio_cfg = self.config.get("tratamento_audio", {})
            usar_filtro = audio_cfg.get("usar_filtro_estudio", False)
            
            if usar_filtro:
                try:
                    from audio_processor import AudioProcessor
                    if not hasattr(self, 'audio_processor'):
                        self.audio_processor = AudioProcessor()
                    print(f"\n🔄 [HOOK IA] Aplicando Masterização e Des-robotização no áudio finalizado...")
                    self.audio_processor.run_pipeline(output_path, output_path, config=audio_cfg)
                except Exception as e:
                    print(f"❌ [HOOK Erro] Falha ao tentar masterizar o áudio gerado: {e}")
                    import traceback; traceback.print_exc()

        return success

    def _generate_audio_internal(self, character_name: str, text: str, output_path: str, **kwargs) -> bool:
        """Determina o modelo do personagem e roteia a geração de áudio (Interno)."""
        
        personagem = self.config.get_personagem(character_name)
        if not personagem:
            print(f"❌ Personagem '{character_name}' não encontrado no config.json")
            return False
            
        # O modelo de TTS agora é GLOBAL para todo o aplicativo!
        # Modelo 1 = VoiceMaker, Modelo 2 = Moss TTS, Modelo 3 = Google TTS+RVC, Modelo 4 = OpenAI.fm+RVC
        # _modelo_override permite forar um modelo diferente (usado no fallback)
        modelo_tts = int(kwargs.pop("_modelo_override", None) or self.config.get("global_tts_model", 1))
        
        if modelo_tts == 1:
            print(f"🎧 Roteando para VoiceMaker (Modelo 1) para o personagem {character_name}")
            voice_id = personagem.get("vozes_voicemaker", "ai3-Aria")
            
            # Se não vieram nos kwargs, pega do personagem
            if "Engine" not in kwargs:
                kwargs["Engine"] = personagem.get("engine", "neural")
            if "LanguageCode" not in kwargs:
                kwargs["LanguageCode"] = personagem.get("idioma_padrao", "pt-BR")
            if "Effect" not in kwargs:
                kwargs["Effect"] = personagem.get("efeito_padrao", "default")
            
            return self.voicemaker.generate_tts(text, voice_id, output_path, **kwargs)
        elif modelo_tts == 2:
            print(f"🎧 Roteando para Moss TTS (Modelo 2) para o personagem {character_name}")
            
            # Recuera a Emoção/Vídeo intencionada pela Aba 3
            emocao_adicional = kwargs.get("Effect", "").strip().lower()
            
            # Áudio Base/Normal
            audio_ref = personagem.get("audio_ref_moss", "")
            
            # Sistema de Alternância Dinâmica de Clonagem (Baseado no estado Emocional)
            if emocao_adicional:
                chave_emocao = f"audio_ref_moss_{emocao_adicional}"
                audio_emocional = personagem.get(chave_emocao, "")
                if audio_emocional and os.path.exists(audio_emocional):
                    audio_ref = audio_emocional
                    print(f"🎭 [MOSS TTS] Roteamento Inteligente ativado: Usando o arquivo .wav da Emoção '{emocao_adicional}'!")
                else:
                    print(f"ℹ️ [Aviso] Áudio de referência avançado '{chave_emocao}' não cadastrado. Usando voz base do Moss.")
            
            if not audio_ref or not os.path.exists(audio_ref):
                print(f"❌ Áudio de referência do Moss TTS principal não encontrado: {audio_ref}")
                return False
                
            moss_config = self.config.get("vps_config", {}).get("moss_tts", {})
            url = moss_config.get("url", "").rstrip('/')
            
            if not url:
                print("❌ URL do Moss TTS não configurada no painel VPS")
                return False
                
            print(f"🚀 Enviando requisição para Moss TTS ({url})...")
            
            # Nota sobre Emoção no Moss TTS: Diferente do Google TTS, 
            # as emoções não são passadas por texto. Elas são definidas estritamente pelo arquivo de áudio .wav de referência.
            texto_final_moss = text
                
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    from gradio_client import Client, handle_file
                    import time
                    client = Client(url, ssl_verify=False)
                    
                    print(f"📡 [Tentativa {attempt+1}/{max_retries}] Conectando à API Gradio em: {url}")
                    start_time = time.time()
                    
                    # O comando submit retorna imediatamente um tracker/job em vez de bloquear
                    job = client.submit(
                        text=texto_final_moss,
                        reference_audio=handle_file(audio_ref),
                        mode_with_reference="Clone",
                        duration_control_enabled=False,
                        duration_tokens=1.0,
                        temperature=1.7,
                        top_p=0.8,
                        top_k=25.0,
                        repetition_penalty=1.0,
                        max_new_tokens=4096.0,
                        api_name="/lambda"
                    )
                    
                    print("⏳ Enviado para a GPU Remota. Aguardando servidor...")
                    
                    # Loop de pooling para rastrear o tempo e o progresso remotamente
                    while not job.done():
                        status = job.status()
                        elapsed = time.time() - start_time
                        
                        # Tentar extrair mensagens detalhadas se o endpoint usar gr.Progress
                        eta_info = ""
                        if getattr(status, 'progress_data', None) and len(status.progress_data) > 0:
                            last_progress = status.progress_data[-1]
                            desc = getattr(last_progress, 'desc', '')
                            pct = getattr(last_progress, 'progress', None)
                            if desc:
                                eta_info = f" | {desc}"
                            if pct is not None:
                                eta_info += f" ({pct*100:.1f}%)"
                                
                        status_name = str(status.code).split('.')[-1]
                        print(f"\r⏳ [MOSS TTS] [{status_name}] Tempo: {elapsed:.1f}s{eta_info} ", end="", flush=True)
                        time.sleep(0.5)
                    
                    print()  # Quebra de final de loading
                    
                    total_time = time.time() - start_time
                    result = job.result()
                    
                    output_audio_path = result[0]
                    status_msg = result[1]
                    
                    print(f"✅ Moss TTS executado em {total_time:.1f}s! Status: {status_msg}")
                    
                    if output_audio_path and os.path.exists(output_audio_path):
                        import subprocess
                        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                        
                        # CRÍTICO: Moss TTS retorna WAV bruto (pcm_s16le 24000Hz).
                        # Deve ser convertido para MP3 real, caso contrário o FFmpeg
                        # falha ao concatenar pois o arquivo tem extensão .mp3 mas é WAV.
                        print(f"🔄 Convertendo WAV→MP3 (libmp3lame 192kbps)...")
                        cmd_convert = [
                            'ffmpeg', '-y',
                            '-i', output_audio_path,
                            '-c:a', 'libmp3lame', '-b:a', '192k',
                            '-ar', '44100', '-ac', '1',
                            output_path
                        ]
                        conv_result = subprocess.run(cmd_convert, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                        
                        if conv_result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                            print(f"✅ Áudio Moss TTS convertido e salvo com sucesso: {output_path}")
                            return True
                        else:
                            err = conv_result.stderr.decode('utf-8', errors='replace')[-300:]
                            print(f"❌ Falha na conversão WAV→MP3: {err}")
                            # Tentativa de fallback: cópia bruta
                            import shutil
                            shutil.copy(output_audio_path, output_path)
                            print(f"⚠️ Fallback: arquivo copiado sem conversão (pode causar erros de codec)")
                            return True
                    else:
                        print(f"❌ Caminho de áudio devolvido pela API grad-ui é inválido: {output_audio_path}")
                        return False
                        
                except ImportError:
                    print("❌ A biblioteca 'gradio_client' não está instalada no ambiente local.")
                    print("🪄 Rode instalar: pip install gradio_client")
                    return False
                except Exception as e:
                    print(f"❌ Erro de conexão com API Moss TTS (Gradio) na Tentativa {attempt+1}: {e}")
                    if attempt < max_retries - 1:
                        print("⏳ Instabilidade na rede detectada. Aguardando 3 segundos para tentar reconectar...")
                        import time
                        time.sleep(3)
                    else:
                        print("❌ Número máximo de tentativas atingido.")
                        import traceback
                        traceback.print_exc()
                        return False
            
        elif modelo_tts == 3:
            print(f"🎧 Roteando para Google TTS + Applio RVC (Modelo 3) para o personagem {character_name}")
            
            # Puxa o prompt base cadastrado
            instrucao_base = personagem.get("instrucao_base_tts", personagem.get("instrucao_base_google", "")).strip()
            
            # A emoção/instrução do script muitas vezes vem mapeada no campo "Effect" do kwargs via gerador_podcast
            emocao_effect = kwargs.get("Effect", "")
            # A instrução adicional preenchida textualmente na UI da Aba de Geração Solta
            emocao_adicional = kwargs.get("emocao_adicional", "")
            
            # Emoção PRIMEIRO (maior peso no início do prompt), personalidade DEPOIS
            partes_prompt = []
            if emocao_adicional:
                partes_prompt.append(f"[ESTADO EMOCIONAL PRIORITÁRIO: {emocao_adicional}]")
            if emocao_effect and emocao_effect != "default":
                partes_prompt.append(f"[Tom da Cena: {emocao_effect}]")
            if instrucao_base:
                partes_prompt.append(instrucao_base)
            prompt_final = " ".join(partes_prompt)
                
            gemini_voice_id = personagem.get("voz_google_tts", "Puck")
            if not gemini_voice_id:
                gemini_voice_id = "Puck"
                
            temperature = float(personagem.get("gemini_temperature", 1.0))
            
            # Define o caminho do áudio temporário como .wav (qualidade bruta sem compressão que o Google entrega nativamente)
            base_audio_path = output_path.replace(".mp3", f"_{character_name.replace(' ', '_').lower()}_base.wav")
            
            # Gera direto em .wav com Gemini para manter maior SampleRate pra pipeline do RVC
            success_base = self.gemini_tts.generate_tts(
                text, 
                gemini_voice_id, 
                base_audio_path,
                instruction_prompt=prompt_final,
                temperature=temperature
            )
            
            if not success_base:
                print("❌ Falha na geração do áudio base pelo Google.")
                return False
                
            # 2. Envia para o Applio RVC processar via Gradio Client (Local ou VPS)
            rvc_model = personagem.get("modelo_rvc", "")
            pitch_rvc = float(personagem.get("pitch_rvc", 0))
            index_rvc = personagem.get("index_rvc", "")
            embedder_rvc = personagem.get("embedder_rvc", "contentvec")
            index_rate = float(personagem.get("index_rate_rvc", 0.75))
            
            vps_config = self.config.get("vps_config", {})
            rvc_mode = vps_config.get("rvc_mode", "local")
            
            if rvc_mode == "local":
                applio_config = vps_config.get("applio_rvc_local", {})
                print(f"📡 Roteamento RVC: Usando Servidor Local (Pinokio)")
            else:
                applio_config = vps_config.get("applio_rvc", {})
                print(f"📡 Roteamento RVC: Usando Servidor Nuvem (VPS)")
                
            applio_url = applio_config.get("url", "").rstrip('/')
            
            if not rvc_model or not applio_url:
                print("⚠️  Modelo Applio ou URL não configurados. Retornando apenas a voz base do Google TTS.")
                if os.path.exists(output_path): os.remove(output_path)
                os.rename(base_audio_path, output_path)
                return True
                
            print(f"🚀 Conectando ao Applio RVC via Gradio Client em {applio_url}")
            print(f"   Modelo: {rvc_model} | Index: {index_rvc} | Pitch: {pitch_rvc} | Embedder: {embedder_rvc} | Index Rate: {index_rate}")
            try:
                from gradio_client import Client, handle_file
                
                client = Client(applio_url)
                
                # Passo 1: Faz upload do áudio base para a pasta assets/audios do Applio
                print("📤 Fazendo upload do áudio base para o Applio...")
                upload_result = client.predict(
                    upload_audio=handle_file(base_audio_path),
                    api_name="/save_to_wav2"
                )
                # upload_result retorna (audio_path_no_server, output_path_str)
                audio_path_on_server = upload_result[0]  # Caminho relativo no servidor ex: "assets/audios/xxx.wav"
                output_path_on_server = upload_result[1]  # Caminho de saída ex: "assets/audios/xxx_output.wav"
                print(f"✅ Áudio carregado no servidor: {audio_path_on_server}")
                
                # Passo 2: Chama a inferência RVC via enforce_terms
                print(f"🎙️ Iniciando conversão de voz com modelo {rvc_model} usando embedder {embedder_rvc}...")
                
                # O Pinokio (v3 - Dez/2025) removeu o hop_length, transladando as chaves. 
                # A VPS (v2 - Mar/2025) manteve a ordem antiga com o param_5 = 128.0 (hop_length)
                # Applio v3 precisa que o param_8 e param_9 sejam os strings *exatos* da dropdown, e eles usam caminhos relativos.
                if rvc_mode == "local":
                    # Converte "Model.pth" para "logs/weights/Model.pth"
                    rvc_model_path = f"logs\\weights\\{rvc_model}" if not rvc_model.startswith("logs") else rvc_model
                    
                    # Converte o path absoluto do index "C:/pinokio.../logs/Folder/file.index" para "logs\\Folder\\file.index"
                    index_rvc_path = ""
                    if index_rvc:
                        try:
                            # Tenta extrair a parte relativa apos "logs"
                            parts = index_rvc.replace("\\", "/").split("/logs/")
                            if len(parts) > 1:
                                index_rvc_path = "logs\\" + parts[1].replace("/", "\\")
                            else:
                                index_rvc_path = index_rvc
                        except:
                            index_rvc_path = index_rvc

                    infer_kwargs = {
                        "terms_accepted": True, "param_1": pitch_rvc, "param_2": index_rate, "param_3": 1.0, "param_4": 0.33,
                        "param_5": "rmvpe", "param_6": audio_path_on_server, "param_7": output_path_on_server,
                        "param_8": rvc_model_path, "param_9": index_rvc_path, "param_10": False,
                        "param_11": False, "param_12": 1.0, "param_13": False, "param_14": 155.0, "param_15": False,
                        "param_16": 0.5, "param_17": "WAV", "param_18": embedder_rvc, "param_19": None, "param_20": False,
                        "param_21": 1.0, "param_22": 1.0, "param_23": False, "param_24": False, "param_25": False, "param_26": False,
                        "param_27": False, "param_28": False, "param_29": False, "param_30": False, "param_31": False, 
                        "param_32": False, "param_33": False, "param_34": 0.5, "param_35": 0.5, "param_36": 0.33, "param_37": 0.4, 
                        "param_38": 1.0, "param_39": 0.0, "param_40": 0.0, "param_41": -6.0, "param_42": 0.05, 
                        "param_43": 0.0, "param_44": 25.0, "param_45": 1.0, "param_46": 0.25, "param_47": 7.0, 
                        "param_48": 0.0, "param_49": 0.5, "param_50": 8.0, "param_51": -6.0, "param_52": 0.0, 
                        "param_53": 1.0, "param_54": 1.0, "param_55": 100.0, "param_56": 0.5, "param_57": 0.0, 
                        "param_58": 0.5, "param_59": 0, "api_name": "/enforce_terms"
                    }
                else:
                    infer_kwargs = {
                        "terms_accepted": True, "param_1": pitch_rvc, "param_2": index_rate, "param_3": 1.0, "param_4": 0.33,
                        "param_5": 128.0, "param_6": "rmvpe", "param_7": audio_path_on_server, "param_8": output_path_on_server,
                        "param_9": rvc_model, "param_10": index_rvc if index_rvc else "", "param_11": False,
                        "param_12": False, "param_13": 1.0, "param_14": False, "param_15": 0.5, "param_16": "WAV",
                        "param_17": None, "param_18": embedder_rvc, "param_19": None, "param_20": False, "param_21": 1.0,
                        "param_22": 1.0, "param_23": False, "param_24": False, "param_25": False, "param_26": False, "param_27": False,
                        "param_28": False, "param_29": False, "param_30": False, "param_31": False, "param_32": False, "param_33": False,
                        "param_34": 0.5, "param_35": 0.5, "param_36": 0.33, "param_37": 0.4, "param_38": 1.0, "param_39": 0.0, "param_40": 0.0, "param_41": -6.0,
                        "param_50": 8.0, "param_51": -6.0, "param_52": 0.0, "param_53": 1.0, "param_54": 1.0, "param_55": 100.0, "param_56": 0.5, "param_57": 0.0,
                        "param_58": 0.5, "param_59": 0, "api_name": "/enforce_terms"
                    }
                    
                try:
                    print('⏳ [Modo 3] Aguardando liberação da Trava RVC...')
                    with _RVC_LOCK:
                        print('🔓 [Modo 3] Trava RVC liberada! Iniciando inferência...')
                        infer_result = client.predict(**infer_kwargs)
                    
                    # infer_result retorna (info_text, audio_file)
                    info_text = infer_result[0]
                    audio_file = infer_result[1]
                    
                    print(f"✅ Conversão concluída! Info: {str(info_text)[:80]}")
                    
                    # Salva o áudio convertido no output_path final
                    if audio_file and hasattr(audio_file, 'name'):
                        import shutil
                        shutil.copy2(audio_file.name, output_path)
                    elif isinstance(audio_file, str) and os.path.exists(audio_file):
                        import shutil
                        shutil.copy2(audio_file, output_path)
                    else:
                        print("❌ Erro: Formato de retorno de áudio desconhecido na API do Applio.")
                        return False
                        
                except Exception as e:
                    # O Applio v3 (Pinokio) gera o áudio mas o Gradio Server bloqueia o download local pelo client via HTTP (403).
                    # Como estamos rodando na mesma máquina, o arquivo JÁ FOI GERADO fisicamente e temos o caminho absoluto dele!
                    if "403 Forbidden" in str(e) and output_path_on_server and os.path.exists(output_path_on_server):
                        print(f"⚠️ Applio gerou 403 no download HTTP, recarregando direto do caminho local!")
                        import shutil
                        shutil.copy2(output_path_on_server, output_path)
                        print(f"✅ Conversão de áudio da VPS/Local resgatada com sucesso!")
                    else:
                        raise e
                
                if os.path.exists(base_audio_path): os.remove(base_audio_path)
                print("🎉 Áudio RVC clonado com sucesso!")
                return True
                
            except Exception as e:
                print(f"❌ Erro ao conectar/processar no Applio RVC: {e}")
                import traceback; traceback.print_exc()
                print("🔄 Fallback: devolvendo voz base sem clonagem RVC")
                if os.path.exists(output_path): os.remove(output_path)
                if os.path.exists(base_audio_path):
                    os.rename(base_audio_path, output_path)
                return True

        elif modelo_tts == 4:
            import datetime
            
            # ── Verificar se o OpenAI.fm está em período de bloqueio ──────────────────
            if self._openaifm_bloqueado and self._openaifm_bloqueado_ate:
                agora = datetime.datetime.now()
                
                # Verificar se o IP mudou (usuário trocou servidor de VPN)
                ip_atual = self._obter_ip_externo()
                if ip_atual and self._openaifm_ip_bloqueado and ip_atual != self._openaifm_ip_bloqueado:
                    print(f"🌐 [Modo 4] IP mudou! ({self._openaifm_ip_bloqueado} → {ip_atual})")
                    print("✅ [Modo 4] VPN trocada detectada — limpando bloqueio e tentando OpenAI.fm!")
                    self.resetar_bloqueio_openaifm()
                    # Continua normalmente abaixo
                elif agora < self._openaifm_bloqueado_ate:
                    minutos_restantes = int((self._openaifm_bloqueado_ate - agora).total_seconds() / 60)
                    print(f"⏳ [Modo 4] OpenAI.fm ainda em cooldown (IP: {ip_atual}). Restam ~{minutos_restantes} min.")
                    print(f"   📱 Dica: troque o servidor da sua VPN agora para resetar este limite!")
                    # Removido o fallback para modelo 3 a pedido do usuário
                    # return self.generate_audio(character_name, text, output_path, _modelo_override=3, **kwargs)
                else:
                    self.resetar_bloqueio_openaifm()
            # ─────────────────────────────────────────────────────────────────────────
            
            print(f"🎧 Roteando para OpenAI.fm Automático (Modelo 4) para o personagem {character_name}")
            
            if self.openaifm_tts is None:
                print("❌ Modo 4 (OpenAI.fm) não está disponível. Instale o Selenium: pip install selenium webdriver-manager")
                return False
            
            # Puxa o prompt base
            instrucao_base = personagem.get("instrucao_base_tts", personagem.get("instrucao_base_google", "")).strip()
            
            # A emoção do script via gerador_podcast é lida em Effect
            emocao_effect = kwargs.get("Effect", "")
            # A instrução adicional preenchida textualmente na UI da Aba de Geração Solta
            emocao_adicional = kwargs.get("emocao_adicional", "")
            
            # Emoção PRIMEIRO (maior peso no início do prompt), personalidade DEPOIS
            partes_prompt = []
            if emocao_adicional:
                partes_prompt.append(f"[ESTADO EMOCIONAL PRIORITÁRIO: {emocao_adicional}]")
            if emocao_effect and emocao_effect != "default":
                partes_prompt.append(f"[Tom da Cena: {emocao_effect}]")
            if instrucao_base:
                partes_prompt.append(instrucao_base)
            prompt_final = " ".join(partes_prompt)
                
            voz_openaifm = personagem.get("voz_openaifm", "")
            if not voz_openaifm:
                print(f"❌ Nenhuma voz do OpenAI.fm foi cadastrada para o personagem '{character_name}'.")
                return False
            
            # PASSO 1: definir o caminho do áudio BASE no diretório temp (intermediário, será deletado após RVC)
            temp_dir = self.config.get_path("temp_dir") if self.config else "temp"
            safe_name = character_name.replace(" ", "_").lower()
            base_audio_path = os.path.join(os.path.abspath(temp_dir), f"openai_base_{safe_name}.wav")
            
            print(f"🧠 Enviando para Selenium OpenAI.fm com Vibe: '{prompt_final[:100]}...'")
            print('⏳ [Modo 4] Aguardando liberação da Trava Web (Selenium)...')
            with _SELENIUM_LOCK:
                print('🔓 [Modo 4] Trava Web liberada! Abrindo navegador...')
                success_base = self.openaifm_tts.generate_tts(
                    text=text,
                    voice_name=voz_openaifm,
                    vibe_text=prompt_final,
                    output_path=base_audio_path  # Salva no TEMP, não no destino final
                )
            
            if not success_base or not os.path.exists(base_audio_path):
                import datetime
                ip_atual = self._obter_ip_externo()
                print(f"❌ [Modo 4] Falha total na geração OpenAI.fm (IP: {ip_atual}).")
                # Registra o bloqueio para detecção de mudança de VPN
                self._openaifm_bloqueado = True
                self._openaifm_bloqueado_ate = datetime.datetime.now() + datetime.timedelta(hours=8)
                self._openaifm_ip_bloqueado = ip_atual
                print(f"⏳ [Modo 4] IP marcado como bloqueado: {ip_atual}. Troque o servidor da VPN e tente gerar novamente.")
                return False
            
            # PASSO 2: Encaminhar para Applio RVC (idêntico ao Modelo 3)
            rvc_model = personagem.get("modelo_rvc", "")
            pitch_rvc = float(personagem.get("pitch_rvc", 0))
            index_rvc = personagem.get("index_rvc", "")
            embedder_rvc = personagem.get("embedder_rvc", "contentvec")
            index_rate = float(personagem.get("index_rate_rvc", 0.75))
            
            vps_config = self.config.get("vps_config", {})
            rvc_mode = vps_config.get("rvc_mode", "local")
            
            if rvc_mode == "local":
                applio_config = vps_config.get("applio_rvc_local", {})
                print(f"📡 [Modo 4] Roteamento RVC: Usando Servidor Local (Pinokio)")
            else:
                applio_config = vps_config.get("applio_rvc", {})
                print(f"📡 [Modo 4] Roteamento RVC: Usando Servidor Nuvem (VPS)")
                
            applio_url = applio_config.get("url", "").rstrip('/')
            
            if not rvc_model or not applio_url:
                print("⚠️  Modelo Applio ou URL não configurados. Retornando apenas a voz base do OpenAI.fm.")
                import shutil
                if os.path.exists(output_path): os.remove(output_path)
                shutil.move(base_audio_path, output_path)
                return True
                
            print(f"🚀 [Modo 4] Conectando ao Applio RVC via Gradio Client em {applio_url}")
            print(f"   Modelo: {rvc_model} | Index: {index_rvc} | Pitch: {pitch_rvc} | Embedder: {embedder_rvc} | Index Rate: {index_rate}")
            try:
                from gradio_client import Client, handle_file
                
                client = Client(applio_url)
                
                print("📤 [Modo 4] Fazendo upload do áudio base para o Applio...")
                upload_result = client.predict(
                    upload_audio=handle_file(base_audio_path),
                    api_name="/save_to_wav2"
                )
                audio_path_on_server = upload_result[0]
                output_path_on_server = upload_result[1]
                print(f"✅ [Modo 4] Áudio carregado no servidor: {audio_path_on_server}")
                
                print(f"🎙️ [Modo 4] Iniciando conversão de voz com modelo {rvc_model} usando embedder {embedder_rvc}...")
                
                if rvc_mode == "local":
                    rvc_model_path = f"logs\\weights\\{rvc_model}" if not rvc_model.startswith("logs") else rvc_model
                    index_rvc_path = ""
                    if index_rvc:
                        try:
                            parts = index_rvc.replace("\\", "/").split("/logs/")
                            if len(parts) > 1:
                                index_rvc_path = "logs\\" + parts[1].replace("/", "\\")
                            else:
                                index_rvc_path = index_rvc
                        except:
                            index_rvc_path = index_rvc

                    infer_kwargs = {
                        "terms_accepted": True, "param_1": pitch_rvc, "param_2": index_rate, "param_3": 1.0, "param_4": 0.33,
                        "param_5": "rmvpe", "param_6": audio_path_on_server, "param_7": output_path_on_server,
                        "param_8": rvc_model_path, "param_9": index_rvc_path, "param_10": False,
                        "param_11": False, "param_12": 1.0, "param_13": False, "param_14": 155.0, "param_15": False,
                        "param_16": 0.5, "param_17": "WAV", "param_18": embedder_rvc, "param_19": None, "param_20": False,
                        "param_21": 1.0, "param_22": 1.0, "param_23": False, "param_24": False, "param_25": False, "param_26": False,
                        "param_27": False, "param_28": False, "param_29": False, "param_30": False, "param_31": False,
                        "param_32": False, "param_33": False, "param_34": 0.5, "param_35": 0.5, "param_36": 0.33, "param_37": 0.4,
                        "param_38": 1.0, "param_39": 0.0, "param_40": 0.0, "param_41": -6.0, "param_42": 0.05,
                        "param_43": 0.0, "param_44": 25.0, "param_45": 1.0, "param_46": 0.25, "param_47": 7.0,
                        "param_48": 0.0, "param_49": 0.5, "param_50": 8.0, "param_51": -6.0, "param_52": 0.0,
                        "param_53": 1.0, "param_54": 1.0, "param_55": 100.0, "param_56": 0.5, "param_57": 0.0,
                        "param_58": 0.5, "param_59": 0, "api_name": "/enforce_terms"
                    }
                else:
                    infer_kwargs = {
                        "terms_accepted": True, "param_1": pitch_rvc, "param_2": index_rate, "param_3": 1.0, "param_4": 0.33,
                        "param_5": 128.0, "param_6": "rmvpe", "param_7": audio_path_on_server, "param_8": output_path_on_server,
                        "param_9": rvc_model, "param_10": index_rvc if index_rvc else "", "param_11": False,
                        "param_12": False, "param_13": 1.0, "param_14": False, "param_15": 0.5, "param_16": "WAV",
                        "param_17": None, "param_18": embedder_rvc, "param_19": None, "param_20": False, "param_21": 1.0,
                        "param_22": 1.0, "param_23": False, "param_24": False, "param_25": False, "param_26": False, "param_27": False,
                        "param_28": False, "param_29": False, "param_30": False, "param_31": False, "param_32": False, "param_33": False,
                        "param_34": 0.5, "param_35": 0.5, "param_36": 0.33, "param_37": 0.4, "param_38": 1.0, "param_39": 0.0, "param_40": 0.0, "param_41": -6.0,
                        "param_50": 8.0, "param_51": -6.0, "param_52": 0.0, "param_53": 1.0, "param_54": 1.0, "param_55": 100.0, "param_56": 0.5, "param_57": 0.0,
                        "param_58": 0.5, "param_59": 0, "api_name": "/enforce_terms"
                    }
                    
                try:
                    print('⏳ [Modo 4] Aguardando liberação da Trava RVC...')
                    with _RVC_LOCK:
                        print('🔓 [Modo 4] Trava RVC liberada! Iniciando inferência...')
                        infer_result = client.predict(**infer_kwargs)
                    info_text = infer_result[0]
                    audio_file = infer_result[1]
                    print(f"✅ [Modo 4] Conversão RVC concluída! Info: {str(info_text)[:80]}")
                    
                    if audio_file and hasattr(audio_file, 'name'):
                        import shutil
                        shutil.copy2(audio_file.name, output_path)
                    elif isinstance(audio_file, str) and os.path.exists(audio_file):
                        import shutil
                        shutil.copy2(audio_file, output_path)
                    else:
                        print("❌ [Modo 4] Formato de retorno de áudio desconhecido na API do Applio.")
                        return False
                        
                except Exception as e:
                    if "403 Forbidden" in str(e) and output_path_on_server and os.path.exists(output_path_on_server):
                        print(f"⚠️ [Modo 4] Applio gerou 403, recarregando direto do caminho local!")
                        import shutil
                        shutil.copy2(output_path_on_server, output_path)
                        print(f"✅ [Modo 4] Conversão resgatada com sucesso!")
                    else:
                        raise e
                
                # Apaga o arquivo base temporário após inferência bem-sucedida
                if os.path.exists(base_audio_path): os.remove(base_audio_path)
                print("🎉 [Modo 4] Áudio OpenAI.fm + RVC clonado com sucesso!")
                return True
                
            except Exception as e:
                print(f"❌ [Modo 4] Erro ao conectar/processar no Applio RVC: {e}")
                import traceback; traceback.print_exc()
                print("🔄 [Modo 4] Fallback: devolvendo voz base sem clonagem RVC")
                if os.path.exists(output_path): os.remove(output_path)
                if os.path.exists(base_audio_path):
                    os.rename(base_audio_path, output_path)
                return True

        else:
            print(f"❌ Modelo TTS roteado desconhecido ou inválido: {modelo_tts}")
            return False
