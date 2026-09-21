import base64
import os
import io
import time
import modal
from backend.cloud_tools.core_app import app

# Imagem com o diffusers
deforum_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg", "git")
    .pip_install(
        "torch==2.5.1",
        "torchvision",
        "accelerate>=0.33.0",
        "diffusers",
        "transformers",
        "imageio",
        "imageio-ffmpeg",
        "scipy",
        "fastapi"
    )
    .run_commands(
        [
            "huggingface-cli download runwayml/stable-diffusion-v1-5 --exclude \"*.safetensors\" \"*.ckpt\" --quiet || true",
            "python -c \"from diffusers import StableDiffusionImg2ImgPipeline; import torch; StableDiffusionImg2ImgPipeline.from_pretrained('runwayml/stable-diffusion-v1-5', torch_dtype=torch.float16, safety_checker=None)\""
        ]
    )
)

@app.cls(gpu="L4", timeout=3600, image=deforum_image)
class DeforumEngine:
    @modal.enter()
    def load_model(self):
        import torch
        from diffusers import StableDiffusionImg2ImgPipeline, StableDiffusionPipeline
        print("[DeforumEngine] Carregando SD v1.5 para TRUE DEFORUM (Img2Img)...")
        # Carrega a pipeline padrao para poder gerar o frame inicial
        self.txt2img_pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5", 
            torch_dtype=torch.float16,
            safety_checker=None
        ).to("cuda")
        
        # Carrega a pipeline img2img reaproveitando os componentes (economiza vram)
        self.pipe = StableDiffusionImg2ImgPipeline(
            vae=self.txt2img_pipe.vae,
            text_encoder=self.txt2img_pipe.text_encoder,
            tokenizer=self.txt2img_pipe.tokenizer,
            unet=self.txt2img_pipe.unet,
            scheduler=self.txt2img_pipe.scheduler,
            safety_checker=None,
            feature_extractor=None
        ).to("cuda")

    def apply_motion(self, image, zoom=1.02, angle=0.0, translation_x=0, translation_y=0):
        from PIL import Image
        w, h = image.size
        
        # Rotacao
        if angle != 0:
            image = image.rotate(angle, resample=Image.BICUBIC, expand=False)
            
        # Zoom
        if zoom != 1.0:
            new_w, new_h = int(w * zoom), int(h * zoom)
            image = image.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - w) / 2 + translation_x
            top = (new_h - h) / 2 + translation_y
            right = (new_w + w) / 2 + translation_x
            bottom = (new_h + h) / 2 + translation_y
            image = image.crop((left, top, right, bottom))
            
        return image

    @modal.method()
    def generate_true_deforum(self, prompt_schedule: list, total_frames: int = 300, fps: int = 15, strength: float = 0.65, zoom: float = 1.015, angle: float = 0.5, init_image_b64: str = None):
        """
        prompt_schedule: lista de dicts [{'frame': 0, 'prompt': '...', 'lora_id': '...'}, {'frame': 100, ...}]
        init_image_b64: base64 string da imagem inicial (opcional). Se não fornecida, gera via txt2img.
        """
        import torch
        import numpy as np
        import imageio
        from PIL import Image
        import base64
        import io

        print(f"[DeforumEngine] Iniciando TRUE DEFORUM para {total_frames} frames...")
        
        all_frames = []
        current_prompt = prompt_schedule[0]['prompt']
        current_lora = prompt_schedule[0].get('lora_id', None)
        
        def load_lora_safe(lora_id):
            try:
                self.pipe.unfuse_lora()
                self.pipe.unload_lora_weights()
                self.txt2img_pipe.unfuse_lora()
                self.txt2img_pipe.unload_lora_weights()
            except:
                pass
            if lora_id:
                print(f"[DeforumEngine] Carregando novo LoRA: {lora_id}")
                try:
                    self.txt2img_pipe.load_lora_weights(lora_id)
                    self.pipe.load_lora_weights(lora_id)
                except Exception as e:
                    print(f"Erro ao carregar LoRA: {e}")
        
        load_lora_safe(current_lora)
        
        generator = torch.Generator(device="cuda").manual_seed(42)

        if init_image_b64:
            print(f"[DeforumEngine] Frame 0 injetado a partir do vídeo base!")
            img_data = base64.b64decode(init_image_b64)
            init_image = Image.open(io.BytesIO(img_data)).convert("RGB")
            # Redimensiona para ser múltiplo de 8 (evitar erro no img2img)
            w, h = init_image.size
            new_w, new_h = (w // 8) * 8, (h // 8) * 8
            if (w, h) != (new_w, new_h):
                init_image = init_image.resize((new_w, new_h), Image.LANCZOS)
        else:
            # Gerar o Frame Zero via txt2img
            print(f"[DeforumEngine] Gerando Frame 0 (txt2img)... Prompt: {current_prompt}")
            init_image = self.txt2img_pipe(
                prompt=current_prompt,
                num_inference_steps=30,
                guidance_scale=7.5,
                generator=generator
            ).images[0]
        
        all_frames.append(init_image)
        current_image = init_image
        
        # Loop do Deforum (img2img iterativo com motion)
        schedule_idx = 0
        for f in range(1, total_frames):
            # Verifica se precisa trocar de prompt/lora
            if schedule_idx + 1 < len(prompt_schedule) and f >= prompt_schedule[schedule_idx + 1]['frame']:
                schedule_idx += 1
                current_prompt = prompt_schedule[schedule_idx]['prompt']
                new_lora = prompt_schedule[schedule_idx].get('lora_id', None)
                if new_lora != current_lora:
                    current_lora = new_lora
                    load_lora_safe(current_lora)
                print(f"[DeforumEngine] Troca de schedule no frame {f} -> Prompt: {current_prompt} | LoRA: {current_lora}")
                
            # Aplica Movimento da Câmera (Zoom in, Rotação)
            moved_image = self.apply_motion(current_image, zoom=zoom, angle=angle)
            
            # Gera proximo frame guiado pelo img2img
            current_image = self.pipe(
                prompt=current_prompt,
                image=moved_image,
                strength=strength, # 0.65 eh ideal para manter estrutura porem mudar aos poucos
                num_inference_steps=20, # Com strength 0.65, o modelo vai rodar uns 13 steps por frame
                guidance_scale=7.5,
                generator=generator # Mantem a mesma seed pro noise ser estavel
            ).images[0]
            
            all_frames.append(current_image)
            
            if f % 30 == 0:
                print(f"[DeforumEngine] Progresso: {f}/{total_frames} frames concluidos.")
                
        out_path = "/tmp/true_deforum.mp4"
        writer = imageio.get_writer(out_path, fps=fps)
        for frame in all_frames:
            writer.append_data(np.array(frame))
        writer.close()

        with open(out_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            
        return {"status": "success", "video_base64": b64}