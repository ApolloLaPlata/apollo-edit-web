import wave
import struct
import math

def generate_wav(filename, frequency=440.0, duration=3.0, sample_rate=24000):
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        n_frames = int(duration * sample_rate)
        for i in range(n_frames):
            value = int(32767.0 * math.sin(frequency * math.pi * float(i) / float(sample_rate)))
            data = struct.pack('<h', value)
            f.writeframesraw(data)

generate_wav(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\voices\xtts\roxingo_ref.wav', 400.0, 5.0)
generate_wav(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\voices\xtts\narrador_ref.wav', 200.0, 5.0)
print('WAV files generated!')

