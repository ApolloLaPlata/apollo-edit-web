from pydantic import BaseModel
class TranscribeRequest(BaseModel):
    audio_base64: str

@web_app.post("/transcribe")
def api_transcribe(req: TranscribeRequest):
    try:
        from backend.cloud_tools.engines.qwen_stt_engine import WhisperTurboSTT
        stt = WhisperTurboSTT()
        print("[Router] Spawning WhisperTurboSTT para Transcricao avulsa")
        import base64
        ref_bytes = base64.b64decode(req.audio_base64)
        res = stt.transcribe.spawn(ref_bytes)
        out = res.get()
        if isinstance(out, dict) and out.get("status") == "success":
            return {"status": "success", "text": out.get("text", "")}
        return {"status": "error", "message": "Falha na transcrição (stt engine)"}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}
