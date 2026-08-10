import wave
import struct

w = wave.open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/default_voice.wav', 'r')
frames = w.readframes(w.getnframes())
samples = struct.unpack(f'{w.getnframes()}h', frames)
max_amp = max(samples)
min_amp = min(samples)
print(f'Mínimo: {min_amp}, Máximo: {max_amp}')
