import re

FILE_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\api\routes_studio.py"
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Modify ElevenLabRequest
old_class = """class ElevenLabRequest(BaseModel):
    model: str
    text: str
    temperature: float = 0.7
    speed: float = 1.0
    voice_name: Optional[str] = None
    ref_audio_base64: Optional[str] = None"""

new_class = """class ElevenLabRequest(BaseModel):
    model: str
    text: str
    instruct: Optional[str] = None
    temperature: float = 0.7
    speed: float = 1.0
    voice_name: Optional[str] = None
    ref_audio_base64: Optional[str] = None"""

content = content.replace(old_class, new_class)

# Modify payload mapping
old_payload = """        req_payload = {
            "text": payload.text,
            "temperature": payload.temperature,
            "speed": payload.speed,
            "language": "pt",
            "return_raw_wav": True
        }"""

new_payload = """        req_payload = {
            "text": payload.text,
            "temperature": payload.temperature,
            "speed": payload.speed,
            "language": "pt",
            "return_raw_wav": True
        }
        
        # O Qwen TTS e possivelmente outros usam "instruct" para emocao/prompt de interpretacao
        if payload.instruct:
            req_payload["instruct"] = payload.instruct
            req_payload["prompt"] = payload.instruct  # Compatibilidade com outros que esperam prompt"""

content = content.replace(old_payload, new_payload)

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print("routes_studio.py updated!")
