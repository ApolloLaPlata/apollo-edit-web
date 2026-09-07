import numpy as np
import soundfile as sf
import random
import os
import subprocess

class TTSPolicyEngine:
    """
    Motor de Políticas que traduz rótulos categóricos do LLM (emotion, arousal, pace)
    em parâmetros numéricos seguros para o XTTSv2, prevenindo alucinações matemáticas.
    """
    
    EMOTION_PRESETS = {
        "neutral": {
            "temperature": 0.65,
            "repetition_penalty": 3.0,
            "speed": 1.0,
            "pause_after_ms_range": [120, 220]
        },
        "angry": {
            "temperature": 0.78,
            "repetition_penalty": 4.2,
            "speed": 1.05,
            "pause_after_ms_range": [60, 160] # Pausa curta, agressiva
        },
        "sad": {
            "temperature": 0.70,
            "repetition_penalty": 3.5,
            "speed": 0.95,
            "pause_after_ms_range": [200, 400] # Pausas dramáticas
        },
        "ironic": {
            "temperature": 0.72,
            "repetition_penalty": 3.8,
            "speed": 0.97,
            "pause_after_ms_range": [150, 300]
        }
    }

    @classmethod
    def get_params(cls, emotion_label: str, arousal: str = "medium", pace: str = "normal") -> dict:
        # Fallback de segurança
        if emotion_label not in cls.EMOTION_PRESETS:
            emotion_label = "neutral"
            
        preset = cls.EMOTION_PRESETS[emotion_label].copy()
        
        # Ajuste fino matemático baseado no Arousal (intensidade) e Pace (ritmo)
        if arousal == "low":
            preset["temperature"] = max(0.60, preset["temperature"] - 0.05)
        elif arousal == "high":
            preset["temperature"] = min(0.85, preset["temperature"] + 0.05)
            
        if pace == "slow":
            preset["speed"] = max(0.85, preset["speed"] - 0.05)
        elif pace == "fast":
            preset["speed"] = min(1.15, preset["speed"] + 0.05)
            
        # Calcular a pausa real sorteando dentro do range seguro
        min_p, max_p = preset["pause_after_ms_range"]
        
        # O Pace também dita qual extremo do range usaremos
        if pace == "slow":
            # Puxa a pausa para o terço superior
            pause = random.randint(min_p + (max_p - min_p)//2, max_p)
        elif pace == "fast":
            # Puxa a pausa para o terço inferior
            pause = random.randint(min_p, min_p + (max_p - min_p)//2)
        else:
            pause = random.randint(min_p, max_p)
            
        preset["pause_after_ms"] = pause
        return preset

class AudioStitcher:
    """
    Stitcher Matemático que une micro-wavs gerados pelo XTTSv2
    aplicando crossfades, de-clicks (micro fades) e normalização (EBU R128).
    """
    
    @staticmethod
    def apply_micro_fades(audio_array: np.ndarray, sr: int, fade_in_ms: int = 10, fade_out_ms: int = 20) -> np.ndarray:
        """Aplica fade-in/out curtíssimos para matar 'clicks' no Sample 0 e remover rabichos de ruído."""
        n_in = int(sr * fade_in_ms / 1000)
        n_out = int(sr * fade_out_ms / 1000)
        
        x = audio_array.copy()
        
        # O arquivo pode ser menor que o fade (caso seja um áudio minúsculo corrompido)
        if len(x) <= n_in + n_out:
            return x
            
        x[:n_in] *= np.linspace(0.0, 1.0, n_in)
        x[-n_out:] *= np.linspace(1.0, 0.0, n_out)
        
        return x

    @staticmethod
    def crossfade_concat(a: np.ndarray, b: np.ndarray, sr: int, fade_ms: int = 15) -> np.ndarray:
        """Funde a cauda do a com a cabeça do b usando um crossfade triangular para evitar saltos brutos de amplitude."""
        n = int(sr * fade_ms / 1000)
        
        if len(a) < n or len(b) < n:
            return np.concatenate([a, b])
            
        fade_out = np.linspace(1.0, 0.0, n)
        fade_in = np.linspace(0.0, 1.0, n)
        
        a_tail = a[-n:] * fade_out
        b_head = b[:n] * fade_in
        mid = a_tail + b_head
        
        return np.concatenate([a[:-n], mid, b[n:]])

    @staticmethod
    def stitch_blocks(audio_blocks: list, pauses_ms: list, sr: int) -> np.ndarray:
        """
        Une uma sequência de blocos de áudio.
        audio_blocks: Lista de arrays Numpy (áudios).
        pauses_ms: Lista de inteiros com a pausa desejada APÓS o respectivo bloco.
        """
        if not audio_blocks:
            return np.array([])
            
        master = AudioStitcher.apply_micro_fades(audio_blocks[0], sr)
        
        for i in range(1, len(audio_blocks)):
            # 1. Adiciona o Padding (Silêncio) requisitado pós-frase anterior
            pause_samples = int(sr * pauses_ms[i-1] / 1000)
            if pause_samples > 0:
                silence = np.zeros(pause_samples)
                master = np.concatenate([master, silence])
                
            # 2. Prepara o próximo bloco (limpando clicks de ponta)
            next_block = AudioStitcher.apply_micro_fades(audio_blocks[i], sr)
            
            # 3. Crossfade (a junção final imperceptível)
            master = AudioStitcher.crossfade_concat(master, next_block, sr)
            
        return master

    @staticmethod
    def loudnorm_master(input_wav: str, output_wav: str, target_lufs: float = -16.0):
        """
        Aplica Loudness Normalization EBU R128 usando FFmpeg.
        Ideal para nivelar podcasts sem achatar a dinâmica.
        """
        # Utiliza loudnorm single-pass (simples e robusto)
        cmd = [
            "ffmpeg", "-y", "-i", input_wav,
            "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
            output_wav
        ]
        
        print(f"[STITCHER] Masterizando faixa para {target_lufs} LUFS...")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("[STITCHER] Masterização concluída com sucesso.")
        except subprocess.CalledProcessError as e:
            print(f"[STITCHER] Erro na masterização: {e.stderr.decode('utf-8', errors='ignore')}")
            raise
