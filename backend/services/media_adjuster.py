import os
import subprocess
import glob

def _natural_sort_key(s):
    """Chave para ordenação natural: arquivo2 < arquivo10."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split('(\\d+)', os.path.basename(s))]

def natural_sort(file_list):
    return sorted(file_list, key=_natural_sort_key)

def is_image(path: str) -> bool:
    return path.lower().endswith(IMAGE_EXTS)

def is_video(path: str) -> bool:
    return path.lower().endswith(VIDEO_EXTS)

class MediaProcessor:
    """
    Constrói e executa comandos FFmpeg para padronização de mídia.
    Pode ser instanciado de forma independente da UI.
    """

    def __init__(self):
        self.width = 1280
        self.height = 720
        self.min_duration = 5
        self.blur_strength = 20
        self.use_background_video = False
        self.background_video_path = None
        self.bitrate = '4M'
        self.fps = 30

    def set_preset(self, preset: str):
        if preset == '1080p':
            self.width, self.height = (1920, 1080)
        else:
            self.width, self.height = (1280, 720)

    def get_duration(self, path: str) -> float:
        """Retorna duração em segundos via ffprobe. Retorna 0.0 em erro."""
        try:
            config = ConfigManager()
            result = subprocess.run([config.get_ffprobe_path(), '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', path], capture_output=True, text=True)
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    def get_dims(self, path: str) -> tuple:
        try:
            config = ConfigManager()
            r = subprocess.run([config.get_ffprobe_path(), '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path], capture_output=True, text=True)
            parts = r.stdout.strip().split(',')
            if len(parts) == 2:
                return (int(parts[0]), int(parts[1]))
        except:
            pass
        return (None, None)

    def build_command(self, input_path: str, output_path: str) -> list:
        """
        Gera o comando FFmpeg completo para processar um arquivo.
        Lógica:
          - Imagem  → vídeo de min_duration segundos
          - Vídeo curto (< min_duration) → estica até min_duration com setpts
          - Vídeo longo (≥ min_duration) → mantém duração original
        Fundo: blur da própria mídia OU vídeo externo.
        NOTA: fg NÃO usa pad (pad black cobria o blur). 
              O overlay posiciona o fg centralizado sobre o bg.
        """
        w, h = (self.width, self.height)
        vw, vh = self.get_dims(input_path)
        if vw and vh:
            if vh > vw:
                w, h = (1080, 1920)
            elif vw > vh:
                w, h = (1920, 1080)
            else:
                w, h = (1080, 1080)
        arquivo_e_imagem = is_image(input_path)
        if self.use_background_video and self.background_video_path:
            bg_filter = f'[1:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}[bg]'
            fg_filter = f'[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease[fg_raw]'
            extra_inputs = ['-hwaccel', 'auto', '-i', self.background_video_path]
            split_filter = ''
        else:
            split_filter = f'[0:v]split=2[src_bg][src_fg];'
            bg_filter = f'[src_bg]scale={w}:{h}:force_original_aspect_ratio=increase,boxblur={self.blur_strength}:10,crop={w}:{h}[bg]'
            fg_filter = f'[src_fg]scale={w}:{h}:force_original_aspect_ratio=decrease[fg_raw]'
            extra_inputs = []
        stretch_filter = ''
        duration_flag = []
        if arquivo_e_imagem:
            duration_flag = ['-t', str(self.min_duration)]
            final_fg = 'fg_raw'
        else:
            duracao = self.get_duration(input_path)
            if 0 < duracao < self.min_duration:
                fator = round(self.min_duration / duracao, 6)
                stretch_filter = f';[fg_raw]setpts={fator}*PTS[fg]'
                final_fg = 'fg'
            else:
                final_fg = 'fg_raw'
        filter_complex = f'{split_filter}{bg_filter};{fg_filter}{stretch_filter};[bg][{final_fg}]overlay=(W-w)/2:(H-h)/2[out]'
        config = ConfigManager()
        cmd = [config.get_ffmpeg_path(), '-y', '-threads', '0']
        if arquivo_e_imagem:
            cmd += ['-loop', '1']
        else:
            cmd += ['-hwaccel', 'auto']
        cmd += ['-i', input_path]
        cmd += extra_inputs
        cmd += duration_flag
        import hardware_detector
        encoder = hardware_detector.detect_h264_encoder()
        if encoder == 'libx264':
            cmd += ['-filter_complex', filter_complex, '-map', '[out]', '-r', str(self.fps), '-b:v', self.bitrate, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', output_path]
        elif 'nvenc' in encoder:
            cmd += ['-filter_complex', filter_complex, '-map', '[out]', '-r', str(self.fps), '-b:v', self.bitrate, '-c:v', encoder, '-preset', 'p4', '-tune', 'hq', '-rc', 'vbr', '-cq', '24', '-spatial-aq', '1', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', output_path]
        else:
            cmd += ['-filter_complex', filter_complex, '-map', '[out]', '-r', str(self.fps), '-b:v', self.bitrate, '-c:v', encoder, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', output_path]
        return cmd

    def process_file(self, input_path: str, output_path: str, log_callback=None):
        """Executa o FFmpeg para um arquivo. Retorna True se OK."""

        def log(msg):
            if log_callback:
                log_callback(msg)
        cmd = self.build_command(input_path, output_path)
        log(f'   🔧 FFmpeg: {os.path.basename(input_path)} → {os.path.basename(output_path)}')
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                log(f'   ❌ Erro FFmpeg: código {result.returncode}')
                return False
            return True
        except FileNotFoundError:
            log('   ❌ FFmpeg não encontrado! Verifique se está no PATH.')
            return False
        except Exception as e:
            log(f'   ❌ Erro inesperado: {e}')
            return False