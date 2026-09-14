import sys

with open("backend/cloud_tools/apollo_modal_engine.py", "r", encoding="utf-8") as f:
    text = f.read()

target_req = 'duration: int = 30'
if 'reference_audio_b64: Optional[str] = None' not in text:
    text = text.replace(target_req, target_req + '\n    reference_audio_b64: Optional[str] = None')

target_spawn = 'fc = engine.generate.spawn(style_tags=req.prompt, lyrics=req.lyrics or "", length_seconds=req.duration, steps=50)'
new_spawn = 'fc = engine.generate.spawn(style_tags=req.prompt, lyrics=req.lyrics or "", length_seconds=req.duration, steps=50, reference_audio_b64=req.reference_audio_b64)'
if new_spawn not in text:
    text = text.replace(target_spawn, new_spawn)

with open("backend/cloud_tools/apollo_modal_engine.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Patched apollo_modal_engine.py")
