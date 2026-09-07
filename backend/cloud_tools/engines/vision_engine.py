import modal
import os
import io
import base64

# A imagem do Modal contendo as bibliotecas necessarias para o Florence-2
vision_image = modal.Image.debian_slim().pip_install(
    "torch",
    "torchvision",
    "transformers",
    "Pillow",
    "einops",
    "accelerate"
)

# App dedicado para a Vision Engine
app = modal.App("apollo-vision-engine")

@app.cls(image=vision_image, gpu="T4", timeout=300)
class FlorenceVisionEngine:
    @modal.enter()
    def setup(self):
        import torch
        from transformers import AutoProcessor, AutoModelForCausalLM 
        print("[VisionEngine] Inicializando Florence-2-large...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        # Florence-2 e o estado da arte open source para compreensao de imagem / OCR
        self.model_id = "microsoft/Florence-2-large"
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id, torch_dtype=self.torch_dtype, trust_remote_code=True
        ).to(self.device)
        self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
        print("[VisionEngine] Florence-2 pronto para analisar imagens.")

    @modal.method()
    def analyze_image(self, image_b64: str, task_prompt: str = "<MORE_DETAILED_CAPTION>") -> str:
        """
        Analisa a imagem e retorna a transcricao textual do que ela contem.
        task_prompt padrao: <MORE_DETAILED_CAPTION>
        """
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
