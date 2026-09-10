
import re

path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/apollo_modal_engine.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Replace api_generate_image
new_func = """@web_app.post("/generate/image")
def api_generate_image(req: ImageRequest):
    import json
    try:
        model = req.model.lower()
        if model not in ["flux2-universal", "qwen-image"]:
            return {"status": "error", "message": f"ERRO: Somente Qwen Image e FLUX suportados."}
            
        from backend.cloud_tools.engines.qwen_image_engine import QwenImageEngine
        engine = QwenImageEngine()
        print(f"[Router] Spawning QwenImageEngine -> format: {req.format}, ref_count: {len(req.reference_images_base64) if req.reference_images_base64 else 0}")
        
        resolved_format = req.format if req.format != "horizontal" else req.aspect_ratio
        
        job = engine.generate.spawn(
            prompt=req.prompt,
            images_b64=req.reference_images_base64,
            aspect_ratio=resolved_format,
            use_upscale=req.use_upscale
        )
        
        return {"status": "success", "job_id": job.object_id}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Erro interno de Roteamento de Imagem: {str(e)}"}
"""

code = re.sub(r"@web_app\.post\(\"/generate/image\"\)\ndef api_generate_image.*?return {\"status\": \"error\", \"message\": f\"Erro interno de Roteamento de Imagem: \{str\(e\)\}\"\}", new_func, code, flags=re.DOTALL)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)
print("Patched modal router")

