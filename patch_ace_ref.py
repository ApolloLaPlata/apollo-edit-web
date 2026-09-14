import sys

with open("backend/cloud_tools/engines/ace_step_15_engine.py", "r", encoding="utf-8") as f:
    text = f.read()

target_def = 'def generate(self, style_tags: str, lyrics: str, length_seconds: int = 60, steps: int = 50, use_erg_lyric: bool = True) -> dict:'
new_def = 'def generate(self, style_tags: str, lyrics: str, length_seconds: int = 60, steps: int = 50, use_erg_lyric: bool = True, reference_audio_b64: str = None) -> dict:'
if target_def in text:
    text = text.replace(target_def, new_def)

target_params = 'inference_steps=steps\n            )'
new_params = """inference_steps=steps
            )
            if reference_audio_b64:
                import base64
                import uuid
                ref_path = f"/tmp/ref_{uuid.uuid4().hex}.mp3"
                with open(ref_path, "wb") as rf:
                    rf.write(base64.b64decode(reference_audio_b64))
                params.reference_audio = ref_path
                # Para reference audio, cover task_type tambem funciona, mas text2music com reference aceita!
"""
if "params.reference_audio =" not in text:
    text = text.replace(target_params, new_params)

with open("backend/cloud_tools/engines/ace_step_15_engine.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Patched ace_step_15_engine.py")
