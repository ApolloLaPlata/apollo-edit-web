import os
with open("backend/cloud_tools/engines/stable_audio_engine.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("def generate_audio(self, prompt: str, seconds: int = 120, steps: int = 100, cfg: float = 7.0):", "def generate_audio(self, prompt: str, duration_s: float = 120, steps: int = 100, cfg: float = 7.0):")
text = text.replace("seconds_total\": seconds", "seconds_total\": int(duration_s)")
text = text.replace("seconds=seconds", "seconds=int(duration_s)")
text = text.replace("Gerando {seconds}s", "Gerando {duration_s}s")

with open("backend/cloud_tools/engines/stable_audio_engine.py", "w", encoding="utf-8") as f:
    f.write(text)
print("FIXED KWARGS")
