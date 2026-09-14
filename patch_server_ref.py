import sys

with open("servidor_web.py", "r", encoding="utf-8") as f:
    text = f.read()

target = 'lyrics = body.get("lyrics", "")'
if "reference_audio_b64 = body.get" not in text:
    text = text.replace(target, target + '\n        reference_audio_b64 = body.get("reference_audio_b64", "")')

payload_target = '"duration": float(duration)'
if '"reference_audio_b64": reference_audio_b64' not in text:
    text = text.replace(payload_target, payload_target + ',\n            "reference_audio_b64": reference_audio_b64')

with open("servidor_web.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Patched servidor_web.py")
