import requests
import json
import os
import subprocess
from typing import Optional, Dict, Any
from backend.services.settings_manager import ConfigManager

class VoiceMakerAPI:
    """Cliente para API oficial do VoiceMaker"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        # Atualiza para a URL correta da API oficial
        self.base_url = self.config.get_voicemaker_config("base_url") or "https://developer.voicemaker.in/voice/api"
        self.api_key = self.config.get_voicemaker_config("api_key")
        
        print(f"[OK] Configuracao carregada:")
        print(f"   Base URL: {self.base_url}")
        print(f"   API Key: {'[OK] Configurada' if self.api_key and self.api_key != 'YOUR_API_KEY_HERE' else '[ERRO] Nao configurada'}")
        
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            print("[AVISO] API Key do VoiceMaker nao configurada. Configure em config.json")
    
    def generate_tts(self, text: str, voice_id: str, output_path: str, **kwargs) -> bool:
        """
        Gera áudio TTS usando a API oficial do VoiceMaker
        
        Args:
            text: Texto para converter em áudio
            voice_id: ID da voz a ser usada
            output_path: Caminho onde salvar o áudio
            **kwargs: Parâmetros adicionais (Engine, LanguageCode, etc.)
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            print("[ERRO] API Key nao configurada")
            return False
        
        try:
            # Endpoint para geração de TTS
            url = f"{self.base_url}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # CORREÇÃO: Limita tamanho do texto para evitar erro 012
            # Documentação: até 10.000 caracteres, mas acima de 3.000 pode demorar mais
            max_text_length = 3000  # Reduzido para evitar problemas
            if len(text) > max_text_length:
                print(f"[AVISO] Texto muito longo ({len(text)} caracteres), truncando para {max_text_length}...")
                text = text[:max_text_length]
            
            # CORREÇÃO: Remove caracteres problemáticos que podem causar Error 012
            import re
            # Remove caracteres de controle e normaliza espaços
            text_original = text
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)  # Remove caracteres de controle
            text = re.sub(r'\s+', ' ', text)  # Normaliza espaços múltiplos
            text = text.strip()
            if text != text_original:
                print(f"[AVISO] Texto limpo de caracteres problemáticos")
            
            # Parâmetros padrão baseados na documentação e configuração
            payload = {
                "Engine": kwargs.get("Engine", "neural"),
                "VoiceId": voice_id,
                "LanguageCode": kwargs.get("LanguageCode", "en-US"),
                "Text": text,
                "OutputFormat": kwargs.get("OutputFormat", "mp3"),
                "SampleRate": kwargs.get("SampleRate", "48000"),
                "Effect": kwargs.get("Effect", "default"),
                "MasterVolume": kwargs.get("MasterVolume", "0"),
                "MasterSpeed": kwargs.get("MasterSpeed", "0"),
                "MasterPitch": kwargs.get("MasterPitch", "0"),
                "ResponseType": kwargs.get("ResponseType", "file"),
                "FileStore": kwargs.get("FileStore", "1")
            }

            print(f"[INFO] Gerando TTS para voz: {voice_id}")
            print(f"[INFO] Texto: {text[:100]}...")
            print(f"[INFO] Fazendo requisicao para: {url}")
            print(f"[INFO] Engine: {payload['Engine']}, Language: {payload['LanguageCode']}")
            print(f"[DEBUG] Payload completo: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            # CORREÇÃO: Retry para erros temporários da API (Error 012)
            import time
            max_api_retries = 5  # Aumentado para 5 tentativas
            base_retry_delay = 5  # Aumentado delay base para 5 segundos
            
            for api_tentativa in range(1, max_api_retries + 1):
                if api_tentativa > 1:
                    # Delay progressivo: 5s, 10s, 15s, 20s
                    delay = base_retry_delay * api_tentativa
                    print(f"[AVISO] Tentativa {api_tentativa}/{max_api_retries} para gerar TTS...")
                    print(f"[INFO] Aguardando {delay}s antes de tentar novamente...")
                    time.sleep(delay)
                
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                
                print(f"[INFO] Status da resposta: {response.status_code}")
                
                # CORREÇÃO: Mostra resposta completa para debug
                if response.status_code != 200:
                    print(f"[ERRO] Erro na API: {response.status_code}")
                    print(f"[DEBUG] Resposta completa: {response.text}")
                    try:
                        error_data = response.json()
                        print(f"[DEBUG] Dados do erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                    except:
                        pass
                    
                    if api_tentativa < max_api_retries:
                        print(f"[AVISO] Tentando novamente em {delay}s...")
                        continue
                    else:
                        return False
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                    except json.JSONDecodeError as e:
                        print(f"[ERRO] Erro ao decodificar JSON da resposta: {e}")
                        print(f"[DEBUG] Resposta recebida: {response.text[:500]}")
                        if api_tentativa < max_api_retries:
                            print(f"[AVISO] Tentando novamente em {delay}s...")
                            continue
                        else:
                            return False
                    
                    # CORREÇÃO: Mostra resposta completa para debug
                    print(f"[DEBUG] Resposta da API: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                    
                    if response_data.get("success"):
                        # Download do arquivo de áudio
                        audio_url = response_data.get("path")
                        if audio_url:
                            print(f"[INFO] Baixando audio de: {audio_url}")
                            
                            # CORREÇÃO: Retry com delay quando arquivo vem vazio
                            import time
                            max_retries = 3
                            retry_delay = 2  # segundos
                            
                            for tentativa in range(1, max_retries + 1):
                                audio_response = requests.get(audio_url, timeout=60)
                                
                                if audio_response.status_code == 200:
                                    # CORREÇÃO: Valida conteúdo antes de salvar
                                    audio_content = audio_response.content
                                    
                                    if not audio_content or len(audio_content) == 0:
                                        if tentativa < max_retries:
                                            print(f"[AVISO] Arquivo vazio na tentativa {tentativa}, tentando novamente em {retry_delay}s...")
                                            time.sleep(retry_delay)
                                            continue
                                        else:
                                            print(f"[ERRO] Conteudo de audio vazio recebido da API apos {max_retries} tentativas")
                                            return False
                                    
                                    # Verifica se é um arquivo MP3 válido (começa com ID3 ou sync frame)
                                    is_valid_mp3 = (
                                        audio_content[:3] == b'ID3' or  # ID3 tag
                                        audio_content[:2] == b'\xff\xfb' or  # MPEG-1 Layer 3 sync
                                        audio_content[:2] == b'\xff\xf3' or  # MPEG-1 Layer 3 sync
                                        audio_content[:2] == b'\xff\xf2' or  # MPEG-1 Layer 3 sync
                                        audio_content[:2] == b'\xff\xfa'     # MPEG-1 Layer 3 sync
                                    )
                                    
                                    if not is_valid_mp3 and len(audio_content) > 100:
                                        print(f"[AVISO] Arquivo pode nao ser MP3 valido, mas continuando...")
                                    
                                    # Salva o áudio gerado
                                    with open(output_path, 'wb') as f:
                                        f.write(audio_content)
                                    
                                    # CORREÇÃO: Valida arquivo salvo
                                    if os.path.exists(output_path):
                                        saved_size = os.path.getsize(output_path)
                                        if saved_size == 0:
                                            if tentativa < max_retries:
                                                print(f"[AVISO] Arquivo salvo vazio na tentativa {tentativa}, tentando novamente...")
                                                time.sleep(retry_delay)
                                                continue
                                            else:
                                                print(f"[ERRO] Arquivo salvo esta vazio apos {max_retries} tentativas")
                                                return False
                                        if saved_size != len(audio_content):
                                            print(f"[AVISO] Tamanho do arquivo salvo ({saved_size}) diferente do recebido ({len(audio_content)})")
                                    
                                    print(f"[OK] Audio TTS gerado com sucesso: {output_path}")
                                    print(f"[INFO] Tamanho do arquivo: {len(audio_content)} bytes")
                                    return True
                                else:
                                    if tentativa < max_retries:
                                        print(f"[AVISO] Erro ao baixar audio (Status {audio_response.status_code}) na tentativa {tentativa}, tentando novamente...")
                                        time.sleep(retry_delay)
                                        continue
                                    else:
                                        print(f"[ERRO] Erro ao baixar audio apos {max_retries} tentativas: {audio_response.status_code}")
                                        print(f"[DEBUG] Resposta do download: {audio_response.text[:200]}")
                                        return False
                        else:
                            print(f"[ERRO] URL do audio nao encontrada na resposta")
                            return False
                else:
                    error_message = response_data.get('message', 'Erro desconhecido')
                    print(f"[ERRO] API retornou erro: {error_message}")
                    print(f"[DEBUG] Resposta completa: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                    
                    # CORREÇÃO: Retry para erros temporários (Error 012)
                    if "Error 012" in error_message or "try again" in error_message.lower():
                        if api_tentativa < max_api_retries:
                            delay = base_retry_delay * (api_tentativa + 1)
                            print(f"[AVISO] Erro temporário detectado (Error 012)")
                            print(f"[INFO] Tentando novamente em {delay}s... (tentativa {api_tentativa + 1}/{max_api_retries})")
                            
                            # CORREÇÃO: Se highres falhar, tenta turbo como fallback
                            if api_tentativa >= 2 and voice_id.startswith("proplus-"):
                                current_proengine = payload.get("ProEngine", "highres")
                                if current_proengine == "highres":
                                    print(f"[INFO] ProEngine='highres' falhou, tentando 'turbo' como fallback (mais rápido)")
                                    payload["ProEngine"] = "turbo"
                                # Se já tentou turbo e ainda falhou, volta para highres na última tentativa
                                elif current_proengine == "turbo" and api_tentativa == max_api_retries - 1:
                                    print(f"[INFO] Última tentativa: voltando para ProEngine='highres' (melhor qualidade)")
                                    payload["ProEngine"] = "highres"
                            
                            continue
                        else:
                            print(f"[ERRO] Falha após {max_api_retries} tentativas com Error 012")
                            print(f"[AVISO] Error 012 pode indicar:")
                            print(f"   1. Problema temporário no servidor da API VoiceMaker")
                            print(f"   2. Limite de requisições excedido na sua conta")
                            print(f"   3. Problema com a API Key ou conta")
                            print(f"   4. Servidor sobrecarregado (aguarde alguns minutos)")
                            print(f"[INFO] Sugestões:")
                            print(f"   - Verifique sua conta VoiceMaker no painel")
                            print(f"   - Aguarde 5-10 minutos antes de tentar novamente")
                            print(f"   - Verifique se há limites de requisições na sua conta")
                            return False
                    else:
                        # Erro permanente, não tenta novamente
                        print(f"[ERRO] Erro permanente da API: {error_message}")
                        return False
                
        except requests.exceptions.RequestException as e:
            print(f"[ERRO] Erro de conexao: {e}")
            import traceback
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"[ERRO] Erro inesperado: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_available_voices(self, language: str = "en-US") -> Optional[Dict[str, Any]]:
        """Obtém lista de vozes disponíveis usando a API oficial"""
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            return None
        
        try:
            # Corrige o endpoint baseado na documentação
            url = "https://developer.voicemaker.in/voice/list"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            payload = {"language": language}
            
            print(f"🌐 Fazendo requisição para: {url}")
            print(f"🌍 Idioma solicitado: {language}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            print(f"[INFO] Status da resposta: {response.status_code}")
            
            if response.status_code == 200:
                voices_data = response.json()
                print(f"📊 Resposta recebida: {len(str(voices_data))} caracteres")
                return voices_data
            else:
                print(f"❌ Erro ao obter vozes: {response.status_code}")
                print(f"📄 Resposta: {response.text[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao obter vozes: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Testa conexão com a API oficial"""
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            print("❌ API Key não configurada para teste de conexão")
            return False
        
        try:
            print(f"🔍 Testando conexão com: {self.base_url}")
            voices = self.get_available_voices("en-US")
            return voices is not None
        except Exception as e:
            print(f"❌ Erro no teste de conexão: {e}")
            return False

    def test_effects(self, voice_id: str = "ai3-Aria") -> bool:
        """Testa diferentes efeitos para identificar problemas de qualidade"""
        print(f"\n🎭 Testando diferentes efeitos para voz: {voice_id}")
        
        effects_to_test = [
            ("default", "Efeito padrão"),
            ("news", "Efeito notícias"),
            ("conversational", "Efeito conversacional"),
            ("assistant", "Efeito assistente"),
            ("happy", "Efeito feliz")
        ]
        
        test_text = "This is a test of different voice effects to check audio quality."
        
        for effect, description in effects_to_test:
            print(f"\n🎤 Testando: {description} ({effect})")
            output_file = f"teste_efeito_{effect}.mp3"
            
            try:
                success = self.generate_tts(
                    test_text, 
                    voice_id, 
                    output_file,
                    Engine="neural",
                    LanguageCode="en-US",
                    Effect=effect,
                    SampleRate="48000"
                )
                
                if success:
                    if os.path.exists(output_file):
                        file_size = os.path.getsize(output_file)
                        print(f"✅ {description} criado: {file_size:,} bytes")
                    else:
                        print(f"❌ Arquivo não foi criado")
                else:
                    print(f"❌ Falha na geração")
                    
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        return True

# Função de simulação para quando a API não estiver disponível
def simulate_tts(text: str, voice_id: str, output_path: str) -> bool:
    """
    Simula geração de TTS criando um arquivo de áudio com tom de teste
    Útil para testes quando a API não estiver disponível
    """
    try:
        
        # Calcula duração aproximada baseada no número de palavras
        words = len(text.split())
        duration = max(1, words / 2.5)  # ~2.5 palavras por segundo
        
        print(f"🎭 Criando simulação TTS:")
        print(f"   📝 Palavras: {words}")
        print(f"   ⏱️  Duração calculada: {duration:.1f}s")
        
        # Tenta criar áudio com múltiplos tons primeiro
        if _create_multi_tone_audio(duration, output_path):
            return True
        else:
            print("🔄 Tentando método alternativo...")
            
            # Método alternativo: gera um beep simples
            return _create_simple_beep(duration, output_path)
            
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        print("🔄 Tentando método alternativo...")
        return _create_simple_beep(duration, output_path)

def _create_simple_beep(duration: float, output_path: str) -> bool:
    """Cria um beep simples como fallback"""
    try:
        # Comando mais simples para gerar um beep
        cmd = [
            'ffmpeg', '-f', 'lavfi',
            '-i', f'sine=frequency=800:duration={duration}',
            '-acodec', 'libmp3lame',
            output_path, '-y'
        ]
        
        print(f"🔧 Comando FFmpeg alternativo: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Beep de teste criado: {output_path}")
            print(f"🎵 Frequência: 800Hz")
            return True
        else:
            print(f"❌ Falha no método alternativo: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no método alternativo: {e}")
        return False

def _create_multi_tone_audio(duration: float, output_path: str) -> bool:
    """Cria áudio com múltiplos tons para ser mais interessante"""
    try:
        # Cria uma sequência de tons diferentes para simular fala
        # Divide a duração em 4 partes com tons diferentes
        segment_duration = duration / 4
        
        # Comando para criar áudio com múltiplos tons usando sintaxe correta
        cmd = [
            'ffmpeg', '-f', 'lavfi',
            '-i', f'sine=frequency=440:duration={duration}',
            '-af', f'afade=t=in:st=0:d=0.1,afade=t=out:st={duration-0.1}:d=0.1',
            '-acodec', 'libmp3lame', '-ab', '128k',
            output_path, '-y'
        ]
        
        print(f"🔧 Comando FFmpeg multi-tom: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Áudio multi-tom criado: {output_path}")
            print(f"🎵 Tom: 440Hz (Lá musical) com fade in/out")
            return True
        else:
            print(f"❌ Falha no método multi-tom: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no método multi-tom: {e}")
        return False

def main():
    """Função principal para teste da API"""
    print("🎤 Testando VoiceMaker API Oficial")
    print("=" * 50)
    
    try:
        # Inicializa o gerenciador de configuração
        print("🔧 Inicializando gerenciador de configuração...")
        config_manager = ConfigManager()
        
        # Cria instância da API
        print("🚀 Criando instância da API...")
        api = VoiceMakerAPI(config_manager)
        
        # Testa conexão
        print("\n🔍 Testando conexão com a API...")
        if api.test_connection():
            print("✅ Conexão com a API estabelecida com sucesso!")
            
            # Obtém vozes disponíveis
            print("\n🎵 Obtendo vozes disponíveis...")
            voices = api.get_available_voices("en-US")
            if voices:
                voices_list = voices.get("data", {}).get("voices_list", [])
                print(f"✅ Encontradas {len(voices_list)} vozes")
                # Mostra algumas vozes como exemplo
                for i, voice in enumerate(voices_list[:5]):
                    print(f"  {i+1}. {voice.get('VoiceWebname', 'N/A')} (ID: {voice.get('VoiceId', 'N/A')}) - {voice.get('LanguageName', 'N/A')}")
            else:
                print("❌ Não foi possível obter as vozes")
        else:
            print("❌ Falha na conexão com a API")
            print("💡 Verifique se a API key está configurada corretamente")
            print("💡 Verifique sua conexão com a internet")
            print("💡 Verifique se o domínio developer.voicemaker.in está acessível")
        
        # Teste de geração TTS
        print("\n🎭 Testando geração de TTS...")
        test_text = "Hello! This is a test of the official VoiceMaker API. How are you doing today?"
        test_voice = "ai3-Jony"  # Voz oficial da documentação
        test_output = "teste_tts_oficial.mp3"
        
        print(f"📝 Texto de teste: {test_text}")
        print(f"🎤 Voz: {test_voice}")
        print(f"💾 Arquivo de saída: {test_output}")
        
        # Tenta gerar TTS real primeiro
        if api.generate_tts(test_text, test_voice, test_output, 
                           Engine="neural", LanguageCode="en-US", Effect="news"):
            print("✅ TTS gerado com sucesso usando a API oficial!")
        else:
            print("⚠️  Falha na API oficial, tentando simulação...")
            # Se falhar, tenta simulação
            if simulate_tts(test_text, test_voice, test_output):
                print("✅ Simulação TTS criada com sucesso!")
            else:
                print("❌ Falha na simulação também")
        
        # Teste de diferentes efeitos para identificar problemas
        print("\n🎭 Testando diferentes efeitos de voz...")
        api.test_effects("ai3-Aria")
        
        print("\n" + "=" * 50)
        print("🏁 Teste concluído!")
        
        # Informações finais
        if os.path.exists(test_output):
            print(f"📁 Arquivo de teste criado: {os.path.abspath(test_output)}")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        print("💡 Verifique se todos os arquivos de configuração estão presentes")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

