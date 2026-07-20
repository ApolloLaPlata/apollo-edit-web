import os
import subprocess
import random
import time
import json
from config_manager import ConfigManager

class MusicVideoEngine:
    def __init__(self, workspace_dir=None):
        self.workspace_dir = workspace_dir
        self.config = ConfigManager()

    def get_audio_duration(self, audio_path):
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of',
            'default=noprint_wrappers=1:nokey=1', audio_path
        ]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    def get_random_background(self, bg_dir):
        bg_dir = self.config.resolve_path(bg_dir)
        if not os.path.exists(bg_dir):
            return None
        videos = [os.path.join(bg_dir, f) for f in os.listdir(bg_dir) if f.lower().endswith(('.mp4', '.mov', '.mkv', '.avi'))]
        if not videos:
            return None
        return random.choice(videos)

    def generate_music_video(self, audio_path, bg_dir, song_name, output_path, template_path=None, cover_path=None, callback=None):
        """
        Gera o videoclipe combinando áudio, fundo aleatório, cover_path e templates JSON.
        """
        if not template_path or not os.path.exists(template_path):
            raise Exception("Template Visual não encontrado.")

        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
            
        if cover_path:
            cover_path = self.config.resolve_path(cover_path)

        bg_video = self.get_random_background(bg_dir)
        if not bg_video:
            raise Exception("Nenhum vídeo de fundo encontrado na pasta de backgrounds.")

        duration = self.get_audio_duration(audio_path)
        if duration == 0:
            raise Exception("Não foi possível determinar a duração do áudio.")

        format_type = template.get('format', 'vertical')
        width, height = (1080, 1920) if format_type == 'vertical' else (1920, 1080)

        # Configurações Padrão
        wave_x, wave_y, wave_w, wave_h = (0, height - 300, width, 300)
        title_x, title_y, title_w, title_h = (width//2 - 400, height//2, 800, 100)
        prog_x, prog_y, prog_w, prog_h = (0, height - 20, width, 20)
        capa_x, capa_y, capa_w, capa_h = (width//2 - 200, height//2 - 300, 400, 400)
        
        has_wave, has_title, has_prog, has_capa = False, False, False, False
        wave_style = 'freqs'
        extra_images = []

        layers = template.get('layers', {})
        for l_id, l_data in layers.items():
            if not l_data.get('visible', True):
                continue
                
            if l_id == 'lay_musica_onda':
                has_wave = True
                wave_x, wave_y, wave_w, wave_h = l_data.get('x', wave_x), l_data.get('y', wave_y), l_data.get('w', wave_w), l_data.get('h', wave_h)
                wave_style = l_data.get('wave_style', 'freqs')
            elif l_id == 'lay_musica_titulo':
                has_title = True
                title_x, title_y, title_w, title_h = l_data.get('x', title_x), l_data.get('y', title_y), l_data.get('w', title_w), l_data.get('h', title_h)
            elif l_id == 'lay_musica_progresso':
                has_prog = True
                prog_x, prog_y, prog_w, prog_h = l_data.get('x', prog_x), l_data.get('y', prog_y), l_data.get('w', prog_w), l_data.get('h', prog_h)
            elif l_id == 'lay_capa_musica':
                has_capa = True
                capa_x, capa_y, capa_w, capa_h = l_data.get('x', capa_x), l_data.get('y', capa_y), l_data.get('w', capa_w), l_data.get('h', capa_h)
            elif l_id.startswith('lay_extra_') and l_data.get('path'):
                path = l_data.get('path')
                path = self.config.resolve_path(path)
                if os.path.exists(path):
                    extra_images.append({'path': path, 'x': l_data.get('x', 0), 'y': l_data.get('y', 0), 'w': l_data.get('w', 100), 'h': l_data.get('h', 100)})

        # Construção Dinâmica do FFMPEG
        cmd = ['ffmpeg', '-y', '-threads', '0', '-stream_loop', '-1', '-hwaccel', 'auto', '-i', bg_video, '-i', audio_path]
        
        # Add cover image if required and available
        if has_capa and cover_path and os.path.exists(cover_path):
            cmd.extend(['-i', cover_path])
        
        for ext in extra_images:
            cmd.extend(['-i', ext['path']])
            
        filter_parts = []
        filter_parts.append(f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},format=yuv420p[bg]")
        last_v = "[bg]"
        
        if has_wave:
            if wave_style == 'vectorscope':
                filter_parts.append(f"[1:a]avectorscope=s={wave_w}x{wave_h}:zoom=1.5:rc=0:gc=255:bc=255:draw=line,format=yuva420p,colorchannelmixer=aa=0.8[wave]")
            elif wave_style == 'cqt':
                filter_parts.append(f"[1:a]showcqt=s={wave_w}x{wave_h}:bar_h={int(wave_h*0.3)}:axis_h=0:sono_h={int(wave_h*0.7)}:format=yuva420p[wave]")
            elif wave_style == 'osc':
                filter_parts.append(f"[1:a]showwaves=s={wave_w}x{wave_h}:mode=cline:colors=cyan|magenta,format=yuva420p,colorkey=0x000000:0.1:0.1[wave]")
            else:
                filter_parts.append(f"[1:a]showfreqs=s={wave_w}x{wave_h}:mode=bar:colors=cyan|magenta|yellow:ascale=log:fscale=log,format=yuva420p,colorchannelmixer=aa=0.8[wave]")
            
            filter_parts.append(f"{last_v}[wave]overlay={wave_x}:{wave_y}[v_wave]")
            last_v = "[v_wave]"
            
        img_idx = 2
        if has_capa and cover_path and os.path.exists(cover_path):
            filter_parts.append(f"[{img_idx}:v]scale={capa_w}:{capa_h}:force_original_aspect_ratio=decrease,format=rgba[capa]")
            filter_parts.append(f"{last_v}[capa]overlay={capa_x}:{capa_y}[v_capa]")
            last_v = "[v_capa]"
            img_idx += 1

        for ext in extra_images:
            filter_parts.append(f"[{img_idx}:v]scale={ext['w']}:{ext['h']}[ext{img_idx}]")
            filter_parts.append(f"{last_v}[ext{img_idx}]overlay={ext['x']}:{ext['y']}[v_ext{img_idx}]")
            last_v = f"[v_ext{img_idx}]"
            img_idx += 1
            
        if has_title:
            fsize = int(title_h * 0.8)
            # Use curly quote to prevent FFmpeg drawtext parsing errors
            safe_name = song_name.replace("'", "\u2019")
            tx = f"{title_x}+({title_w}-text_w)/2"
            ty = f"{title_y}+({title_h}-text_h)/2"
            filter_parts.append(f"{last_v}drawtext=text='{safe_name}':fontcolor=white:fontsize={fsize}:x={tx}:y={ty}:borderw=3:bordercolor=black:shadowcolor=black:shadowx=3:shadowy=3[v_txt]")
            last_v = "[v_txt]"
            
        if has_prog:
            filter_parts.append(f"{last_v}drawbox=x={prog_x}:y={prog_y}:color=red@0.8:width={prog_w}*t/{duration}:height={prog_h}:t=fill[v_prog]")
            last_v = "[v_prog]"
            
        if last_v != "[out]":
            filter_parts.append(f"{last_v}copy[out]")
            
        cmd.extend([
            '-filter_complex', "; ".join(filter_parts),
            '-map', '[out]',
            '-map', '1:a',
            '-t', str(duration)
        ])
        
        import hardware_detector
        encoder = hardware_detector.detect_h264_encoder()
        if encoder == 'libx264':
            cmd.extend(['-c:v', 'libx264', '-preset', 'fast', '-crf', '23'])
        else:
            cmd.extend(['-c:v', encoder, '-b:v', '4M'])
            
        cmd.extend([
            '-af', 'loudnorm=I=-14:LRA=11:TP=-1.5',
            '-c:a', 'aac', '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            output_path
        ])

        if callback:
            callback(f"Gerando clipe para '{song_name}' (Duração: {duration:.1f}s)...")
            
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        
        for line in process.stdout:
            # We could parse 'time=' to report progress, but for simplicity we just let it run
            pass
            
        process.wait()
        
        if process.returncode != 0:
            raise Exception(f"Erro no FFmpeg ao gerar {song_name}")
            
        return output_path

    def concat_videos(self, video_list, output_path, callback=None):
        """
        Usa o concat demuxer do FFmpeg para emendar dezenas de vídeos instantaneamente.
        Requisito: todos os vídeos devem ter mesma resolução, framerate e codec.
        """
        if not video_list:
            raise Exception("Lista de vídeos vazia.")
            
        list_file = os.path.join(os.path.dirname(output_path), "concat_list.txt")
        with open(list_file, 'w', encoding='utf-8') as f:
            for vid in video_list:
                # O caminho no txt do ffmpeg precisa escapar aspas simples e ser absoluto com barras normais
                safe_path = vid.replace('\\', '/').replace("'", "'\\''")
                f.write(f"file '{safe_path}'\n")
                
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c', 'copy', # Mágica: Copia sem re-renderizar!
            output_path
        ]
        
        if callback:
            callback(f"Concatenando {len(video_list)} vídeos...")
            
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        process.wait()
        
        if os.path.exists(list_file):
            try: os.remove(list_file)
            except: pass
            
        if process.returncode != 0:
            raise Exception("Erro no FFmpeg ao concatenar os vídeos.")
            
        return output_path
