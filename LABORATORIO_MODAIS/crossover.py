import os
import sys

try:
    import librosa
    import soundfile as sf
    import numpy as np
    import scipy.signal
except ImportError:
    print("Instalando dependências para crossover...")
    os.system("pip install librosa soundfile numpy scipy")
    import librosa
    import soundfile as sf
    import numpy as np
    import scipy.signal

def crossover_mix(original_path, audiosr_path, out_path, crossover_freq=200):
    print(f"Lendo áudio original: {original_path}")
    y_orig, sr_orig = librosa.load(original_path, sr=48000)
    
    print(f"Lendo áudio AudioSR: {audiosr_path}")
    y_sr, sr_audiosr = librosa.load(audiosr_path, sr=48000)
    
    # Igualar tamanhos caso tenham diferença de samples
    min_len = min(len(y_orig), len(y_sr))
    y_orig = y_orig[:min_len]
    y_sr = y_sr[:min_len]
    
    # Filtro Low-Pass no original (Filtro Butterworth)
    nyquist = 48000 / 2.0
    cutoff = crossover_freq / nyquist
    b, a = scipy.signal.butter(4, cutoff, btype='low')
    y_orig_low = scipy.signal.filtfilt(b, a, y_orig)
    
    # Filtro High-Pass no AudioSR
    b_high, a_high = scipy.signal.butter(4, cutoff, btype='high')
    y_sr_high = scipy.signal.filtfilt(b_high, a_high, y_sr)
    
    # Mix
    y_mix = y_orig_low + y_sr_high
    
    # Normalizar para evitar clipping
    max_val = np.max(np.abs(y_mix))
    if max_val > 0:
        y_mix = y_mix / max_val * 0.95
        
    print(f"Salvando Crossover em: {out_path}")
    sf.write(out_path, y_mix, 48000, format='WAV')

if __name__ == "__main__":
    base_dir = "LABORATORIO_MODAIS/testes_audio"
    orig = os.path.join(base_dir, "ace_step_test.wav")
    sr = os.path.join(base_dir, "4_ace_step_audiosr_test.wav")
    out = os.path.join(base_dir, "5_crossover_final_test.wav")
    
    if os.path.exists(orig) and os.path.exists(sr):
        crossover_mix(orig, sr, out)
        print("✅ Crossover concluído com sucesso!")
    else:
        print("Arquivos originais não encontrados para o crossover.")
