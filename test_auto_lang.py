import modal
import base64
import wave, struct
import io
import sys
sys.path.append('.')
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine

@app.local_entrypoint()
def run():
    buf = io.BytesIO()
    with wave.open(buf, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(struct.pack('<h', 0) * 24000)
    b64_audio = base64.b64encode(buf.getvalue()).decode()

    engine = QwenTtsCloneEngine()
    print("Testing Qwen with language=auto...")
    res = engine.clone.remote(text="Hello world, this is a test in English.", ref_audio_b64=b64_audio, ref_text="Silence", language="auto", instruct="")
    print(res["status"])
    if res["status"] == "error":
        print(res.get("message"))
