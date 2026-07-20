import os
import subprocess
import json
import uuid
import tempfile
import logging

def gerar_video(payload: dict, callback=None):
    videos = payload.get('videos', [])
    saida_dir = payload.get('saida_dir')
    nome_final = payload.get('nome_final', 'output.mp4')
    audio_narrador = payload.get('audio_narrador')
    
    if not audio_narrador or not os.path.exists(audio_narrador):
        raise Exception("Audio do narrador invalido ou nao encontrado.")
        
    if not videos:
        raise Exception("Nenhum video fornecido para a edicao.")
        
    if not saida_dir:
        raise Exception("Diretorio de saida nao definido.")
        
    output_path = os.path.join(saida_dir, nome_final)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        for vid in videos:
            # escaping backslashes for FFmpeg
            vid_escaped = vid.replace("\\", "\\\\")
            f.write(f"file '{vid_escaped}'\n")
        list_file = f.name
        
    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0', '-i', list_file,
            '-i', audio_narrador,
            '-c:v', 'libx264', '-crf', '28', '-preset', 'fast',
            '-c:a', 'aac', '-b:a', '128k',
            '-map', '0:v', '-map', '1:a',
            '-shortest', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Erro FFmpeg:\n{result.stderr}")
            
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)
            
    return output_path

def probe_duration(file_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode == 0:
        try:
            return float(result.stdout.strip())
        except:
            return 0.0
    return 0.0
