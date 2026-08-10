import modal
import wave
import struct
import os

dummy_wav_path = "dummy_ref.wav"
with wave.open(dummy_wav_path, "w") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(24000)
    for i in range(24000):
        w.writeframes(struct.pack('h', 0))

with open(dummy_wav_path, "rb") as f:
    ref_bytes = f.read()

try:
    print("Looking up Function...")
    generate_voice = modal.Function.lookup("apollo-render-router", "F5TTSEngine.generate_voice")
    print("Generating voice...")
    out_bytes = generate_voice.remote("Isso é um teste.", ref_bytes)
    print(f"Sucesso! {len(out_bytes)} bytes.")
except Exception as e:
    print(f"Erro: {e}")
finally:
    if os.path.exists(dummy_wav_path):
        os.remove(dummy_wav_path)
