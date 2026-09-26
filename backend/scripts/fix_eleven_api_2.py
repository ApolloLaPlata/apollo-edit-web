import re

FILE_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\api\routes_studio.py"
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Modify ElevenLabRequest to include ref_text
old_class = """class ElevenLabRequest(BaseModel):
    model: str
    text: str
    instruct: Optional[str] = None
    temperature: float = 0.7
    speed: float = 1.0
    voice_name: Optional[str] = None
    ref_audio_base64: Optional[str] = None"""

new_class = """class ElevenLabRequest(BaseModel):
    model: str
    text: str
    instruct: Optional[str] = None
    ref_text: Optional[str] = None
    temperature: float = 0.7
    speed: float = 1.0
    voice_name: Optional[str] = None
    ref_audio_base64: Optional[str] = None"""

content = content.replace(old_class, new_class)

# Modify payload mapping
old_payload = """        # O Qwen TTS e possivelmente outros usam "instruct" para emocao/prompt de interpretacao
        if payload.instruct:
            req_payload["instruct"] = payload.instruct
            req_payload["prompt"] = payload.instruct  # Compatibilidade com outros que esperam prompt"""

new_payload = """        # O Qwen TTS e possivelmente outros usam "instruct" para emocao/prompt de interpretacao
        if payload.instruct:
            req_payload["instruct"] = payload.instruct
            req_payload["prompt"] = payload.instruct  # Compatibilidade com outros que esperam prompt
            
        if payload.ref_text:
            req_payload["ref_text"] = payload.ref_text
            req_payload["reference_text"] = payload.ref_text"""

content = content.replace(old_payload, new_payload)

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print("routes_studio.py updated with ref_text!")
