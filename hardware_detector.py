import subprocess
import os

_cached_encoder_h264 = None
_cached_encoder_hevc = None

def detect_h264_encoder():
    global _cached_encoder_h264
    if _cached_encoder_h264:
        return _cached_encoder_h264

    encoders_to_test = ['h264_nvenc', 'h264_amf', 'h264_qsv']
    
    for enc in encoders_to_test:
        cmd = [
            'ffmpeg', '-y', '-v', 'error',
            '-f', 'lavfi', '-i', 'color=c=black:s=64x64:d=0.1',
            '-c:v', enc,
            '-f', 'null', '-'
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            if res.returncode == 0:
                _cached_encoder_h264 = enc
                return enc
        except:
            pass
            
    _cached_encoder_h264 = 'libx264'
    return 'libx264'

def detect_hevc_encoder():
    global _cached_encoder_hevc
    if _cached_encoder_hevc:
        return _cached_encoder_hevc

    encoders_to_test = ['hevc_nvenc', 'hevc_amf', 'hevc_qsv']
    
    for enc in encoders_to_test:
        cmd = [
            'ffmpeg', '-y', '-v', 'error',
            '-f', 'lavfi', '-i', 'color=c=black:s=64x64:d=0.1',
            '-c:v', enc,
            '-f', 'null', '-'
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            if res.returncode == 0:
                _cached_encoder_hevc = enc
                return enc
        except:
            pass
            
    _cached_encoder_hevc = 'libx265'
    return 'libx265'
