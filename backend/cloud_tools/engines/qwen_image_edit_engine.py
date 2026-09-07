
import json
import base64
import uuid

# Reusa o ArenaComfyEngine que ja esta validado com timeouts e tratamentos de erro
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine

class QwenImageEditEngineWrapper:
    """
    SaaS Orchestration Layer wrapper para Qwen Image Edit Plus.
    Usa o ArenaComfyEngine para executar o workflow na Modal.
    Garante a consistencia de personagem (Multi-Character Consistency)
    usando a habilidade nativa do Qwen de ler imagens de condicao sem perder a anatomia.
    """
    def __init__(self):
        self.comfy_engine = ArenaComfyEngine()

    def edit_image(self, prompt: str, base_image_path: str = None, base_image_b64: str = None) -> dict:
        """
        Executa a edicao mantendo a consistencia 2D do personagem.
        """
        if not base_image_b64 and base_image_path:
            with open(base_image_path, "rb") as f:
                base_image_b64 = base64.b64encode(f.read()).decode("utf-8")
        elif not base_image_b64:
            return {"status": "error", "error": "Imagem base nao fornecida."}

        # Gera um filename unico para quebrar a agressividade do cache do ComfyUI LoadImage
        unique_filename = f"qwen_ref_{uuid.uuid4().hex[:8]}.png"

        workflow = {
            "1": { "class_type": "UNETLoader", "inputs": { "unet_name": "qwen_image_edit_2511_bf16.safetensors", "weight_dtype": "default" }},
            "3": { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image" }},
            "4": { "class_type": "VAELoader", "inputs": { "vae_name": "qwen_image_vae.safetensors" }},
            "5": { "class_type": "LoadImage", "inputs": { "image": unique_filename }},
            "5b": { "class_type": "FluxKontextImageScale", "inputs": { "image": ["5", 0] }},
            "6":  { "class_type": "TextEncodeQwenImageEditPlus", "inputs": {
                "clip": ["3", 0], "prompt": prompt, "vae": ["4", 0], "image1": ["5b", 0]
            }},
            "7": { "class_type": "ConditioningZeroOut", "inputs": { "conditioning": ["6", 0] }},
            "8":  { "class_type": "EmptyLatentImage", "inputs": { "width": 1024, "height": 1024, "batch_size": 1 }},
            "9": { "class_type": "KSampler", "inputs": {
                "model": ["1", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["8", 0],
                "seed": 42, "steps": 20, "cfg": 2.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0
            }},
            "10": { "class_type": "VAEDecode", "inputs": { "samples": ["9", 0], "vae": ["4", 0] }},
            "11": { "class_type": "SaveImage", "inputs": { "images": ["10", 0], "filename_prefix": "qwen_orchestration" }}
        }

        try:
            result = self.comfy_engine.generate.remote(
                workflow_json=workflow,
                source_image_b64=base_image_b64,
                source_image_name=unique_filename
            )
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}

