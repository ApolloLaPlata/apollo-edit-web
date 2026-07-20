import os
import subprocess

def extrair_audio(video_path, output_path):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-q:a', '0', '-map', 'a', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def remover_audio(video_path, output_path):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-c:v', 'copy', '-an', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def inverter_video(video_path, output_path):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', 'reverse', '-af', 'areverse', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def comprimir_video(video_path, output_path, crf='28'):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-vcodec', 'libx264', '-crf', '28', '-preset', 'fast', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def rotacionar_video(video_path, output_path, transpose_code='1'):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', vf_param, '-c:a', 'copy', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def alterar_velocidade(video_path, output_path, speed_factor):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-filter_complex', f'[0:v]setpts={v_speed}*PTS[v];[0:a]atempo={a_speed}[a]', '-map', '[v]', '-map', '[a]', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def remover_ultimo_frame(video_path, output_path):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-t', str(new_duration), '-c', 'copy', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def redimensionar_video(video_path, output_path):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', f'scale={largura}:{altura}', '-c:a', 'copy', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def ajustar_brilho_contraste(video_path, output_path, brilho='0', contraste='1'):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', f'eq=brightness={brilho}:contrast={contraste}', '-c:a', 'copy', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def detectar_formato_video(video_path, output_path):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def espelhar_video(video_path, output_path):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', 'hflip', '-c:a', 'copy', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def remover_silencios(video_path, output_path):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-af', 'silenceremove=start_periods=1:start_threshold=-50dB:stop_periods=-1:stop_threshold=-50dB:stop_duration=0.5', '-c:v', 'copy', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def converter_mp4(video_path, output_path):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-c:v', 'libx264', '-preset', 'fast', '-c:a', 'aac', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def extrair_frames(video_path, output_path):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', 'fps=1', out_pattern]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path

def padronizar_vertical(video_path, output_path):
    cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', vf, '-c:a', 'copy', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Erro no FFmpeg: {result.stderr}')
    return output_path
