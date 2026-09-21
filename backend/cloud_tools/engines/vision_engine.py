import modal
import os
import io
import base64

cache_vol = modal.Volume.from_name("hf-hub-cache", create_if_missing=True)

def download_florence_model():
    from transformers import AutoProcessor, AutoModelForCausalLM
    model_id = "microsoft/Florence-2-large"
    AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
    AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

vision_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("packaging", "ninja", "torch", "torchvision")
    .pip_install("transformers==4.41.2", "Pillow", "einops", "accelerate", "timm")
    .run_commands("mkdir -p /usr/local/lib/python3.11/site-packages/flash_attn && touch /usr/local/lib/python3.11/site-packages/flash_attn/__init__.py")
    .run_function(download_florence_model)
)

# App dedicado para a Vision Engine
app = modal.App("apollo-vision-engine")

@app.cls(image=vision_image, gpu="T4", timeout=300, enable_memory_snapshot=False)
class FlorenceVisionEngine:
    @modal.enter()
    def setup(self):
        import torch
        from transformers import AutoProcessor, AutoModelForCausalLM 
        print("[VisionEngine] Inicializando Florence-2-large...")
        
        # IMPORTANTE: Durante o snap=True, o modelo PRECISA ficar na CPU.
        # Inicializar contexto CUDA antes do snapshot causa crash-looping.
        self.device = "cpu" 
        self.torch_dtype = torch.float16 # CUDA initialization removed
        
        self.model_id = "microsoft/Florence-2-large"
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id, trust_remote_code=True
        )
        self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
        print("[VisionEngine] Florence-2 pronto no CPU (Snapshotting...).")

    @modal.method()
    def analyze_image(self, image_b64: str, task_prompt: str = "<MORE_DETAILED_CAPTION>") -> str:
        import torch
        if torch.cuda.is_available() and self.model.device.type != "cuda":
            print("[VisionEngine] Movendo modelo do CPU para CUDA (pos-snapshot)...")
            self.model = self.model.to("cuda")
            self.device = "cuda"
            
        from PIL import Image
        import torch
        
        try:
            # Converte Base64 para PIL Image
            if "," in image_b64:
                image_b64 = image_b64.split(",")[1]
            image_data = base64.b64decode(image_b64)
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            
            # Processamento Florence-2
            inputs = self.processor(text=task_prompt, images=image, return_tensors="pt").to(self.device, self.torch_dtype)
            
            with torch.no_grad():
                generated_ids = self.model.generate(
                    input_ids=inputs["input_ids"],
                    pixel_values=inputs["pixel_values"],
                    max_new_tokens=1024,
                    early_stopping=False,
                    do_sample=False,
                    num_beams=3,
                )
            
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
            
            # Limpeza do token de tarefa no resultado
            parsed_answer = self.processor.post_process_generation(
                generated_text, 
                task=task_prompt, 
                image_size=(image.width, image.height)
            )
            
            result = parsed_answer.get(task_prompt, str(parsed_answer))
            print(f"[VisionEngine] Analise concluida: {result[:50]}...")
            return result
            
        except Exception as e:
            print(f"[VisionEngine] Erro ao analisar imagem: {e}")
            return f"Erro na analise visual: {str(e)}"
