import base64
import io
import time
from fastapi import Request
from fastapi.responses import JSONResponse

try:
    import torch
    import litserve as ls
    from diffusers import FluxPipeline
except ImportError:
    class Dummy:
        LitAPI = object
    ls = Dummy()

APOLLO_SECRET_KEY = "APOLLO_SECRET_KEY_123" # Em prod, use os.environ.get("APOLLO_SECRET")

class FluxAPI(ls.LitAPI):
    def setup(self, device):
        print(f"[{time.strftime('%X')}] Carregando modelo Flux.1-schnell na {device}...")
        self.pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell", 
            torch_dtype=torch.bfloat16
        ).to(device)
        print(f"[{time.strftime('%X')}] Modelo carregado com sucesso!")

    def decode_request(self, request):
        return {
            "prompt": request.get("prompt", "A futuristic city in cyberpunk style"),
            "num_inference_steps": request.get("steps", 4),
            "guidance_scale": request.get("guidance", 3.5),
            "width": request.get("width", 1024),
            "height": request.get("height", 1024)
        }

    def predict(self, inputs):
        print(f"[{time.strftime('%X')}] Gerando imagem para o prompt: '{inputs['prompt']}'")
        result = self.pipe(
            prompt=inputs["prompt"],
            num_inference_steps=inputs["num_inference_steps"],
            guidance_scale=inputs["guidance_scale"],
            width=inputs["width"],
            height=inputs["height"]
        )
        return result.images[0]

    def encode_response(self, output):
        buffered = io.BytesIO()
        output.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return {
            "status": "success",
            "image_base64": img_str,
            "message": "Geração concluída."
        }

if __name__ == "__main__":
    server = ls.LitServer(FluxAPI(), accelerator="auto", max_batch_size=1)
    
    # Segurança de Borda (MiddleWare JWT/Bearer Token)
    @server.app.middleware("http")
    async def verify_token(request: Request, call_next):
        # Protege rotas de inferência
        if request.url.path == "/predict":
            token = request.headers.get("Authorization")
            if not token or token != f"Bearer {APOLLO_SECRET_KEY}":
                return JSONResponse(status_code=401, content={"detail": "Forbiden: Operário recusou a conexão (Token Inválido ou Ausente)."})
        return await call_next(request)

    server.run(port=8000)
