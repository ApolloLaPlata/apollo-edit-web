import os
import re
import json
import time
import subprocess
import concurrent.futures
import random
from typing import List, Dict, Optional, Tuple

# Adiciona diretório atual ao path para importar módulos locais
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from backend.services.settings_manager import ConfigManager
# VoiceMakerAPI opcional - nao utilizado neste software
try:
    from voicemaker_api import VoiceMakerAPI
except ImportError:
    VoiceMakerAPI = None
from backend.services.tts_manager import TTSManager

class PodcastGenerator:
    """
    Gerador de Podcast avançado integrado ao Descarga News.
    Suporta:
    - Vozes do VoiceMaker (config.json)
    - Múltiplos formatos de saída (Áudio, Vídeo, Tags)
    - Roteiros com emoções: [Personagem] (Emoção): Texto
    """
    def __init__(self, config_file: str = "config.json"):
        self.config_manager = ConfigManager(config_file)
        self.tts_manager = TTSManager(self.config_manager)
        self.output_dir = os.path.join(current_dir, "output_podcast")
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def parse_script(self, script_path: str) -> List[Dict[str, str]]:
        """
        Lê roteiro. Suporta formatos:
        1. [Nome] (Emoção): Texto
        2. Bloco X - Personagem: Y - Estado emocional do video - Z - Emoção TTS - (...) - TTS - "Texto"
        Fallback: Nome: Texto (assume Normal)
        """
        dialogues = []
        if not os.path.exists(script_path):
            print(f"[ERRO] Roteiro não encontrado: {script_path}")
            return dialogues

        with open(script_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Regex 1: Formato "Bloco" detalhado
                # Ex: Bloco 1 - Personagem: Rafael Descarga - Estado emocional do video - Feliz - Emoção TTS - (...) - TTS - "Texto"
                match_block = re.search(
                    r'Bloco\s+\d+.*?Personagem:\s*(.*?)\s*-\s*Estado emocional do video\s*-\s*(.*?)\s*-.*?TTS\s*-\s*"(.*)"', 
                    line, 
                    re.IGNORECASE
                )

                # Regex 2: Formato com Instrução TTS Emocional Explicita em '< >'
                # Ex: [Nome] (Emoção): <Instrução TTS> Texto OU [Nome] <Instrução TTS> Texto
                match_tts_emotion = re.match(r'\[([^\]]+)\](?:\s*\((.*?)\))?\s*:?\s*<(.*?)>\s*:?\s*(.*)', line)

                # Regex 3: Formato curto [Nome] (Emoção): Texto OU [Nome]: Texto
                match_short = re.match(r'\[([^\]]+)\](?:\s*\((.*?)\))?\s*:\s*(.*)', line)
                
                tts_emotion_text = ""

                if match_block:
                    char_name = match_block.group(1).strip()
                    emotion = match_block.group(2).strip().lower() if match_block.group(2) else "normal"
                    text = match_block.group(3).strip()
                elif match_tts_emotion:
                    char_name = match_tts_emotion.group(1).strip()
                    emotion = match_tts_emotion.group(2).strip().lower() if match_tts_emotion.group(2) else "normal"
                    tts_emotion_text = match_tts_emotion.group(3).strip()
                    text = match_tts_emotion.group(4).strip()
                elif match_short:
                    char_name = match_short.group(1).strip()
                    emotion = match_short.group(2).strip().lower() if match_short.group(2) else "normal"
                    text = match_short.group(3).strip()
                else:
                    # Tenta formato simples: Nome: Texto
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        char_name = parts[0].strip()
                        char_name = char_name.replace('[', '').replace(']', '')
                        text = parts[1].strip()
                        if text.startswith('"') and text.endswith('"'):
                            text = text[1:-1]
                        emotion = "normal"
                    else:
                        print(f"[AVISO] Linha ignorada (formato inválido): {line}")
                        continue
                
                dialogues.append({
                    "character": char_name,
                    "emotion": emotion,
                    "tts_emotion": tts_emotion_text,
                    "text": text
                })
        
        print(f"[INFO] Roteiro processado: {len(dialogues)} falas.")
        return dialogues

    def _get_audio_duration(self, file_path: str) -> float:
        """Obtém duração do áudio usando ffprobe"""
        try:
            cmd = [
                'ffprobe', 
                '-v', 'error', 
                '-show_entries', 'format=duration', 
                '-of', 'default=noprint_wrappers=1:nokey=1', 
                file_path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return float(result.stdout.strip())
        except Exception as e:
            print(f"[ERRO] Falha ao obter duração de {file_path}: {e}")
            return 5.0 # Fallback

    def find_tag_path(self, character_name: str) -> Optional[str]:
        """
        Encontra o arquivo de Tag (Logo) para o personagem.
        Tenta diferentes variações de nome (singular/plural).
        """
        tags_dir = os.path.join(current_dir, "..", "Midias", "Tags")
        if not os.path.exists(tags_dir):
            return None
        
        # Normaliza nome para busca (maiúsculo)
        name_upper = character_name.upper()
        
        # Variações para tentar
        variations = [
            f"LOGO {name_upper}.png",
            f"LOGO {name_upper}S.png", # Tenta plural
            f"LOGO {name_upper.rstrip('S')}.png" # Tenta singular se tiver S
        ]
        
        for filename in variations:
            path = os.path.join(tags_dir, filename)
            if os.path.exists(path):
                return path
        
        return None

    def generate_video_segment(self, audio_path: str, video_source: str, output_video: str):
        """
        Gera um segmento de vídeo loopando o source para cobrir o áudio.
        """
        duration = self._get_audio_duration(audio_path)
        
        import hardware_detector
        encoder = hardware_detector.detect_h264_encoder()
        
        cmd = [
            'ffmpeg', '-y', '-threads', '0', '-hwaccel', 'auto',
            '-stream_loop', '-1', '-i', video_source,
            '-i', audio_path,
            '-map', '0:v:0', '-map', '1:a:0',
            '-t', str(duration)
        ]
        
        if encoder == 'libx264':
            cmd.extend(['-c:v', 'libx264', '-preset', 'fast'])
        else:
            cmd.extend(['-c:v', encoder, '-b:v', '4M'])
            
        cmd.extend([
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            output_video
        ])
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def generate_tag_segment(self, audio_path: str, tag_image_path: str, output_video: str):
        """
        Gera um segmento de vídeo com a Tag (imagem) estática + áudio.
        Mantém transparência usando codec ProRes 4444 (MOV).
        """
        duration = self._get_audio_duration(audio_path)
        
        # Comando para imagem estática + áudio com transparência
        # -c:v prores_ks -profile:v 4444: Codec ProRes com Alpha
        # -pix_fmt yuva444p10le: Formato de pixel com Alpha
        cmd = [
            'ffmpeg', '-y', '-threads', '0', '-hwaccel', 'auto',
            '-loop', '1', '-i', tag_image_path,
            '-i', audio_path,
            '-c:v', 'prores_ks', '-profile:v', '4444', 
            '-pix_fmt', 'yuva444p10le',
            '-t', str(duration),
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            output_video
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def apply_smart_pacing(self, input_path: str, output_path: str):
        """
        Remove silêncios excessivos e padroniza gaps.
        Usa o filtro silenceremove do FFmpeg.
        """
        print("   ✂️ Aplicando Smart Pacing (Trimming)...")
        # silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-40dB
        # Remove silêncio do final se maior que 0.5s
        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-af', 'silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-40dB',
            '-c:a', 'libmp3lame', '-b:a', '192k',
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def apply_compressor(self, input_path: str, output_path: str):
        """
        Aplica compressor de áudio para estilo 'Radio Voice'.
        """
        print("   📻 Aplicando Compressor...")
        # acompressor: attack=5, release=50, threshold=-12dB, ratio=4:1, makeup=auto
        # Isso dá um som mais "cheio" e consistente
        intensity = self.config_manager.get("compressor_intensity", 50.0) / 100.0
        # Ajusta ratio baseado na intensidade (1.0 a 20.0)
        ratio = 1.0 + (intensity * 10.0) 
        
        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-af', f'acompressor=threshold=-12dB:ratio={ratio}:attack=5:release=50',
            '-c:a', 'libmp3lame', '-b:a', '192k',
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def apply_audio_normalization(self, input_path: str, output_path: str):
        """
        Aplica normalização de áudio (Loudness Normalization) usando ffmpeg loudnorm.
        Alvo: Configurado no config.json (Padrão: -14 LUFS).
        """
        # Obtém alvo de LUFS do config
        target_lufs = self.config_manager.get("target_lufs", -10.0)
        
        # Filtro loudnorm:
        # I=target: Integrated loudness target
        # TP=-1.5: True Peak limit
        # LRA=11: Loudness Range target
        print(f"   🔊 Aplicando normalização: {target_lufs} LUFS")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-af', f'loudnorm=I={target_lufs}:TP=-1.5:LRA=11',
            '-c:a', 'libmp3lame', '-b:a', '192k',
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def generate_podcast(self, script_path: str, modes: List[str] = ["audio"], normalize_audio: bool = True, gerar_mapa_cores: bool = False, log_callback=None):
        """
        Gera o podcast.
        modes: lista contendo 'audio', 'video', 'tags'
        normalize_audio: se True, aplica normalização (LUFS configurado) no final
        gerar_mapa_cores: se True, exporta mapa_temas_podcast.json junto ao áudio final
        log_callback: função para receber logs em tempo real
        """
        def log(msg):
            print(msg)
            if log_callback:
                log_callback(msg)

        dialogues = self.parse_script(script_path)
        
        # Listas para concatenação
        segments_audio = []
        segments_video = []
        segments_tags = []
        # MAPA DE TEMAS: [(char_name, tema, dur)] para gerar JSON ao final
        _mapa_temas_falas = []

        # Recarregar as configurações do disco para capturar o Motor Global (VoiceMaker, Moss, etc) escolhido agora
        self.config_manager.config = self.config_manager._load_config()

        log(f"[INFO] Iniciando geração. Modos: {modes} | Normalizar: {normalize_audio}")


        # --- ARQUITETURA DE FILA INTELIGENTE (Fase 5) ---
        # Graças aos locks globais no tts_manager.py, podemos disparar 
        # TODAS as falas simultaneamente. O TTS Base baixa em paralelo,
        # mas o RVC e o OpenAI aguardam na fila interna com segurança.
        
        def process_dial(t_data):
            i, dial = t_data
            char_name = dial['character']
            emotion = dial['emotion']
            tts_emotion_text = dial.get('tts_emotion', '')
            text = dial['text']
            
            # 1. Obter configuração do personagem
            char_config = self.config_manager.get_personagem(char_name)
            if not char_config:
                log(f"[AVISO] Personagem '{char_name}' não encontrado no config.json. Pulando.")
                return None

            # 2. Determinar Voz e Estilo
            emotion_config = char_config.get("estados_emocionais", {}).get(emotion, {})
            voice_id = char_config.get("vozes_voicemaker")
            effect = emotion_config.get("efeito_padrao", char_config.get("efeito_padrao", "default"))
            engine = char_config.get("engine", "neural")
            lang = char_config.get("idioma_padrao", "pt-BR")
            master_volume = char_config.get("volume_ajuste", 0.0)

            # 3. Gerar Áudio
            safe_char_name = re.sub(r'[<>:"/\\|?*]', '_', char_name)
            filename_base = f"{i+1:03d}_{safe_char_name}_{emotion}"
            audio_path = os.path.join(self.output_dir, f"{filename_base}.mp3")
            
            log(f"--- Fala {i+1}: {char_name} ({emotion}) [Vol: {master_volume}dB] ---")
            if tts_emotion_text: log(f"🧠 Instrução de Emoção TTS: {tts_emotion_text[:50]}...")
            
            if not os.path.exists(audio_path):
                audio_kwargs = {
                    "Engine": engine,
                    "LanguageCode": lang,
                    "Effect": effect,
                    "MasterVolume": str(master_volume)
                }
                if tts_emotion_text: audio_kwargs["emocao_adicional"] = tts_emotion_text

                # GERAÇÃO PARALELA (Baseada em rede) -> TRAVA DE INFERÊNCIA RVC INTERNA
                success = self.tts_manager.generate_audio(
                    character_name=char_name,
                    text=text,
                    output_path=audio_path,
                    **audio_kwargs
                )
                if not success:
                    log(f"[ERRO] Falha no TTS para {char_name}")
                    return None
            
            # Smart Pacing
            if self.config_manager.get("use_smart_pacing", False):
                audio_paced_path = audio_path.replace(".mp3", "_paced.mp3")
                self.apply_smart_pacing(audio_path, audio_paced_path)
                if os.path.exists(audio_paced_path) and os.path.getsize(audio_paced_path) > 0:
                    import shutil
                    os.remove(audio_path)
                    shutil.move(audio_paced_path, audio_path)
            
            _dur_fala = self._get_audio_duration(audio_path)
            _perfil_fala = char_config.get("perfil_legenda", "")
            
            result_data = {
                'index': i,
                'audio': audio_path,
                'mapa': {
                    "personagem": char_name,
                    "perfil_legenda": _perfil_fala,
                    "duracao": _dur_fala
                },
                'video': None,
                'tag': None
            }

            # 4. Gerar Vídeo (GPU)
            if "video" in modes:
                video_source = emotion_config.get("video_source", char_config.get("video_source"))
                if video_source and video_source.startswith(".."):
                    video_source = os.path.abspath(os.path.join(current_dir, video_source))
                
                if video_source and os.path.exists(video_source):
                    video_out = os.path.join(self.output_dir, f"{filename_base}.mp4")
                    if not os.path.exists(video_out):
                        self.generate_video_segment(audio_path, video_source, video_out)
                    result_data['video'] = video_out
            
            # 5. Gerar Tags (GPU)
            if "tags" in modes:
                tag_path = self.find_tag_path(char_name)
                if tag_path:
                    tag_out = os.path.join(self.output_dir, f"{filename_base}_tag.mov")
                    if not os.path.exists(tag_out):
                        self.generate_tag_segment(audio_path, tag_path, tag_out)
                    result_data['tag'] = tag_out

            return result_data

        log(f"[INFO] Disparando ThreadPoolExecutor GLOBAL para {len(dialogues)} blocos em paralelo...")
        import os as _os_module
        max_workers = max(1, min(16, _os_module.cpu_count() or 4))
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            tasks = [(i, d) for i, d in enumerate(dialogues)]
            futures = [executor.submit(process_dial, t) for t in tasks]
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    results.append(res)
        
        # Ordena os resultados para garantir a concatenação correta
        results.sort(key=lambda x: x['index'])
        
        for r in results:
            segments_audio.append(r['audio'])
            _mapa_temas_falas.append(r['mapa'])
            if r['video']: segments_video.append(r['video'])
            if r['tag']: segments_tags.append(r['tag'])
        
        # 6. Concatenar (Finalização)
        if "audio" in modes and segments_audio:
            final_audio_raw = os.path.join(self.output_dir, "podcast_final_audio_raw.mp3")
            final_audio_paced = os.path.join(self.output_dir, "podcast_final_audio_paced.mp3")
            final_audio_compressed = os.path.join(self.output_dir, "podcast_final_audio_compressed.mp3")
            final_audio = os.path.join(self.output_dir, "podcast_final_audio.mp3")
            
            # 6.0 Concatenação Inicial
            log(f"[INFO] Concatenando {len(segments_audio)} segmentos de áudio...")
            self._concat_files(segments_audio, final_audio_raw)
            
            # Verifica se a concatenação teve sucesso antes de prosseguir
            if not os.path.exists(final_audio_raw) or os.path.getsize(final_audio_raw) == 0:
                log(f"[ERRO CRÍTICO] Falha na concatenação dos áudios! O arquivo bruto não foi criado.")
                log(f"[INFO] Verificando segmentos: {len(segments_audio)} arquivos encontrados.")
                for seg in segments_audio:
                    exists = os.path.exists(seg)
                    size = os.path.getsize(seg) if exists else 0
                    log(f"  - {os.path.basename(seg)}: {'OK' if exists and size > 0 else 'PROBLEMA!'} ({size} bytes)")
            else:
                log(f"[INFO] Concatenação OK. Arquivo bruto: {os.path.getsize(final_audio_raw)} bytes")
                current_audio = final_audio_raw
                
                # 6.2 Compressor
                if self.config_manager.get("use_compressor", False):
                    self.apply_compressor(current_audio, final_audio_compressed)
                    if os.path.exists(final_audio_compressed) and os.path.getsize(final_audio_compressed) > 0:
                        if current_audio != final_audio_raw: os.remove(current_audio)
                        current_audio = final_audio_compressed

                # 6.3 Normalização (Final)
                if normalize_audio:
                    log(f"[INFO] Aplicando normalização (-10 LUFS)...")
                    self.apply_audio_normalization(current_audio, final_audio)
                    if os.path.exists(final_audio) and os.path.getsize(final_audio) > 0:
                        if current_audio != final_audio_raw and os.path.exists(current_audio): os.remove(current_audio)
                        if os.path.exists(final_audio_raw) and final_audio_raw != current_audio: os.remove(final_audio_raw)
                    else:
                        # Normalização falhou - usa o arquivo de estágio atual como fallback
                        log(f"[AVISO] Normalização falhou, usando áudio sem normalização como fallback...")
                        import shutil
                        shutil.copy2(current_audio, final_audio)
                else:
                    # Se não normalizar, renomeia o último estágio para final
                    if os.path.exists(final_audio): os.remove(final_audio)
                    import shutil
                    shutil.copy2(current_audio, final_audio)
                    if os.path.exists(current_audio): os.remove(current_audio)

                if os.path.exists(final_audio) and os.path.getsize(final_audio) > 0:
                    log(f"[SUCESSO] Podcast Áudio gerado: podcast_final_audio.mp3 ({os.path.getsize(final_audio)//1024} KB)")
                    # ─── GERAR MAPA DE TEMAS (somente se solicitado) ──────────────────────
                    if gerar_mapa_cores and _mapa_temas_falas:
                        cursor = 0.0
                        mapa_final = []
                        for fala in _mapa_temas_falas:
                            start_t = round(cursor, 3)
                            end_t   = round(cursor + fala["duracao"], 3)
                            mapa_final.append({
                                "personagem": fala["personagem"],
                                "perfil_legenda": fala["perfil_legenda"],
                                "start": start_t,
                                "end": end_t
                            })
                            cursor = end_t
                        mapa_path = os.path.join(self.output_dir, "mapa_temas_podcast.json")
                        with open(mapa_path, "w", encoding="utf-8") as _mf:
                            json.dump(mapa_final, _mf, indent=4, ensure_ascii=False)
                        log(f"[MAPA] mapa_temas_podcast.json gerado: {len(mapa_final)} falas mapeadas.")
                    elif not gerar_mapa_cores:
                        log("[INFO] Mapa de cores não solicitado (ative o checkbox se precisar).")
                    # ────────────────────────────────────────────────────────────────────────
                else:
                    log(f"[ERRO CRÍTICO] Arquivo final NÃO foi gerado! Verifique se o FFmpeg está instalado corretamente.")
        if "video" in modes and segments_video:
            # Vídeo final com substituição do áudio pelo normalizado
            video_concat = os.path.join(self.output_dir, "podcast_temp_video.mp4")
            self._concat_files(segments_video, video_concat)
            
            final_video = os.path.join(self.output_dir, "podcast_final_video.mp4")
            
            if normalize_audio and os.path.exists(os.path.join(self.output_dir, "podcast_final_audio.mp3")):
                log("[INFO] Substituindo áudio do vídeo pelo áudio normalizado...")
                audio_norm = os.path.join(self.output_dir, "podcast_final_audio.mp3")
                cmd_swap = [
                    'ffmpeg', '-y',
                    '-i', video_concat,
                    '-i', audio_norm,
                    '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-map', '0:v:0', '-map', '1:a:0',
                    '-shortest',
                    final_video
                ]
                subprocess.run(cmd_swap, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(video_concat): os.remove(video_concat)
            else:
                if os.path.exists(final_video): os.remove(final_video)
                os.rename(video_concat, final_video)

            log(f"[SUCESSO] Podcast Vídeo gerado: podcast_final_video.mp4")

        if "tags" in modes and segments_tags:
            self._concat_files(segments_tags, os.path.join(self.output_dir, "podcast_final_tags.mov"))
            log(f"[SUCESSO] Podcast Tags gerado: podcast_final_tags.mov")
        
        # 7. LIMPEZA DE ARQUIVOS TEMPORÁRIOS
        log(f"[INFO] Limpando arquivos temporários...")
        temp_files_removed = 0
        
        # Remove segmentos individuais de áudio
        for audio_file in segments_audio:
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    temp_files_removed += 1
            except Exception as e:
                log(f"[AVISO] Não foi possível remover {audio_file}: {e}")
        
        # Remove segmentos individuais de vídeo
        for video_file in segments_video:
            try:
                if os.path.exists(video_file):
                    os.remove(video_file)
                    temp_files_removed += 1
            except Exception as e:
                log(f"[AVISO] Não foi possível remover {video_file}: {e}")
        
        # Remove segmentos individuais de tags
        for tag_file in segments_tags:
            try:
                if os.path.exists(tag_file):
                    os.remove(tag_file)
                    temp_files_removed += 1
            except Exception as e:
                log(f"[AVISO] Não foi possível remover {tag_file}: {e}")
        
        # Remove arquivos intermediários de processamento
        intermediate_files = [
            os.path.join(self.output_dir, "podcast_final_audio_raw.mp3"),
            os.path.join(self.output_dir, "podcast_final_audio_paced.mp3"),
            os.path.join(self.output_dir, "podcast_final_audio_compressed.mp3"),
            os.path.join(self.output_dir, "concat_list.txt")
        ]
        
        for temp_file in intermediate_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    temp_files_removed += 1
            except Exception as e:
                log(f"[AVISO] Não foi possível remover {temp_file}: {e}")
        
        log(f"[SUCESSO] Limpeza concluída: {temp_files_removed} arquivos temporários removidos")

    def _concat_files(self, file_list: List[str], output_file: str):
        """Concatena arquivos usando ffmpeg"""
        list_file = os.path.join(self.output_dir, "concat_list.txt")
        with open(list_file, 'w', encoding='utf-8') as f:
            for path in file_list:
                # Usa barras normais (/) para compatibilidade com ffmpeg no Windows
                safe_path = path.replace('\\', '/')
                f.write(f"file '{safe_path}'\n")
        
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', list_file, '-c', 'copy', output_file
        ]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"[ERRO] FFmpeg falhou na concatenação: {result.stderr.decode('utf-8', errors='replace')[-500:]}")

if __name__ == "__main__":
    generator = PodcastGenerator()
    
    # Criar roteiro de teste avançado se não existir
    SCRIPT_FILE = "roteiro_prompt_complexo.txt"
    if not os.path.exists(SCRIPT_FILE):
        with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
            f.write("Bloco 1 - Personagem: Rafael Descargas - Estado emocional do video - Feliz - Emoção TTS - (voz do personagem muito animado vibrante e alegre) - TTS - \"que legal amigos. eu estou muito feliz nesse exemplo de voz\"\n")
    
    # Exemplo de chamada:
    # generator.generate_podcast(SCRIPT_FILE, modes=["audio", "video", "tags"])
    generator.generate_podcast(SCRIPT_FILE, modes=["audio", "video", "tags"])
