import sys
import codecs

path = 'backend/cloud_tools/engines/flux_engine.py'
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

split_token = 'class FluxImg2ImgEngine:'
if split_token in content:
    content = content.split(split_token)[0]
    content = content.rsplit('@app.cls', 1)[0]
else:
    print('Could not find class')
    sys.exit(1)

new_class = '''@app.cls(gpu="h100", timeout=600, image=flux_dev_image, scaledown_window=120)
class FluxImg2ImgEngine:
    @modal.enter()
    def load_model(self):
        import torch
        from diffusers import FluxImg2ImgPipeline, FluxTransformer2DModel
        from transformers import BitsAndBytesConfig, T5EncoderModel
        
        torch.set_grad_enabled(False)
        print("[FluxImg2ImgEngine] Loading FLUX.1-dev native (Diffusers Img2Img, 8-bit Quantized)...")
        
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        
        transformer = FluxTransformer2DModel.from_pretrained(
            "/models/flux1_dev",
            subfolder="transformer",
            quantization_config=quantization_config,
            torch_dtype=torch.bfloat16,
            local_files_only=True
        )

        text_encoder_2 = T5EncoderModel.from_pretrained(
            "/models/flux1_dev",
            subfolder="text_encoder_2",
            quantization_config=quantization_config,
            torch_dtype=torch.bfloat16,
            local_files_only=True
        )
        
        self.pipe = FluxImg2ImgPipeline.from_pretrained(
            "/models/flux1_dev",
            transformer=transformer,
            text_encoder_2=text_encoder_2,
            torch_dtype=torch.bfloat16,
            local_files_only=True
        )
        self.pipe.to("cuda")
        print("[FluxImg2ImgEngine] Pipeline loaded on GPU (8-bit).")

    @modal.method()
    def generate(self, prompt: str, aspect_ratio: str = "horizontal", seed: int = 42, reference_images_base64: list[str] = None) -> dict:
        import torch
        from PIL import Image
        import io
        import base64
        import time
        import traceback
        
        t0 = time.time()
        print(f"[FluxImg2ImgEngine] Request received. Aspect Ratio: {aspect_ratio}")
        
        cfg = FORMATS.get(aspect_ratio.lower(), FORMATS["horizontal"])
        generator = torch.Generator(device="cpu").manual_seed(seed)

        try:
            torch.cuda.empty_cache()
            
            if not reference_images_base64 or len(reference_images_base64) == 0:
                raise ValueError("This engine requires a reference image.")
                
            b64_data = reference_images_base64[0]
            if "," in b64_data:
                b64_data = b64_data.split(",")[1]
            b64_data += "=" * ((4 - len(b64_data) % 4) % 4)
                
            img_data = base64.b64decode(b64_data)
            init_image = Image.open(io.BytesIO(img_data)).convert("RGB")
            init_image = init_image.resize((cfg["width"], cfg["height"]), Image.LANCZOS)
            
            # Inference 
            output = self.pipe(
                prompt=prompt,
                image=init_image,
                strength=0.75,
                guidance_scale=3.5,
                num_inference_steps=20,
                max_sequence_length=512,
                generator=generator
            )
            
            image = output.images[0]
            
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            render_time = time.time() - t0
            
            return {
                "status": "success",
                "image_base64": b64,
                "render_time_seconds": round(render_time, 2),
                "engine": "FLUX-Img2Img-Native",
                "estimated_cost_usd": round(render_time * 0.0012, 4)
            }

        except Exception as e:
            err = traceback.format_exc()
            print(f"[FluxImg2ImgEngine] ERROR: {err}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": err
            }
'''
with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content + new_class)
print('DONE')
