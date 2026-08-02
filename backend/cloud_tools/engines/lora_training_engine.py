import modal
import os
import json
import uuid

# Volume to store downloaded diffusers models for AI-Toolkit (to avoid redownloading 24GB every time)
diffusers_volume = modal.Volume.from_name("flux-diffusers-vol", create_if_missing=True)
# Volume to store the resulting user LoRAs
loras_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

# Define the environment for training
lora_trainer_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1", "libglib2.0-0", "git", "wget")
    .run_commands(
        "git clone https://github.com/ostris/ai-toolkit.git /root/ai-toolkit",
        "cd /root/ai-toolkit && git submodule update --init --recursive",
        "pip install -r /root/ai-toolkit/requirements.txt",
        # Install huggingface_hub to download the model
        "pip install huggingface_hub"
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

from backend.cloud_tools.modal_app import app

@app.function(
    image=lora_trainer_image,
    volumes={"/flux_diffusers": diffusers_volume},
    secrets=[modal.Secret.from_name("huggingface-secret")], # Need a HF token to download FLUX.1-dev
    timeout=3600
)
def download_flux_diffusers():
    """Baixa o modelo Diffusers do Flux uma unica vez para o Volume"""
    import os
    from huggingface_hub import snapshot_download
    
    print("Iniciando download do FLUX.1-dev em formato diffusers...")
    os.makedirs("/flux_diffusers", exist_ok=True)
    snapshot_download(
        repo_id="black-forest-labs/FLUX.1-dev",
        local_dir="/flux_diffusers",
        local_dir_use_symlinks=False,
        ignore_patterns=["*.msgpack", "*.safetensors.index.json"] 
    )
    print("Download concluido com sucesso no Volume.")

@app.cls(
    gpu="A100",  # Requires at least A100/H100 40GB+
    image=lora_trainer_image,
    volumes={
        "/flux_diffusers": diffusers_volume,
        "/loras_output": loras_volume
    },
    timeout=7200, # 2 horas de limite
    secrets=[modal.Secret.from_name("huggingface-secret")]
)
class FluxLoraTrainer:
    
    @modal.method()
    def train_lora(self, user_id: str, character_name: str, images_b64: list, trigger_word: str = "ohwx"):
        import base64
        import yaml
        import time
        import shutil
        import subprocess
        
        t0 = time.time()
        dataset_dir = f"/tmp/dataset_{uuid.uuid4().hex}"
        os.makedirs(dataset_dir, exist_ok=True)
        
        # 1. Salvar imagens enviadas
        for i, b64_str in enumerate(images_b64):
            try:
                # Remove header se existir
                if "," in b64_str:
                    b64_str = b64_str.split(",")[1]
                img_data = base64.b64decode(b64_str)
                with open(os.path.join(dataset_dir, f"img_{i}.jpg"), "wb") as f:
                    f.write(img_data)
                
                # Opcional: Salvar txt para captioning se enviarmos caption
                with open(os.path.join(dataset_dir, f"img_{i}.txt"), "w") as f:
                    f.write(trigger_word)
            except Exception as e:
                print(f"Erro salvando imagem {i}: {e}")
                
        # 2. Configurar YAML do ai-toolkit
        config = {
            "job": "extension",
            "config": {
                "name": character_name,
                "process": [
                    {
                        "type": "sd_trainer",
                        "training_folder": "/tmp/output",
                        "device": "cuda:0",
                        "network": {
                            "type": "lora",
                            "linear": 16,
                            "linear_alpha": 16
                        },
                        "save": {
                            "dtype": "bfloat16",
                            "save_every": 250,
                            "max_step_saves_to_keep": 1
                        },
                        "datasets": [
                            {
                                "folder_path": dataset_dir,
                                "caption_ext": "txt",
                                "caption_dropout_rate": 0.05,
                                "shuffle_tokens": False,
                                "cache_latents_to_disk": True,
                                "resolution": [512, 768, 1024]
                            }
                        ],
                        "train": {
                            "batch_size": 1,
                            "steps": 2500, # Padrao comum para rostos
                            "gradient_accumulation_steps": 1,
                            "train_unet": True,
                            "train_text_encoder": False, # Nao treina text encoder no flux lora leve
                            "gradient_checkpointing": True,
                            "noise_scheduler": "flowmatch",
                            "optimizer": "adamw8bit",
                            "lr": 4e-4,
                            "ema_config": {
                                "use_ema": True,
                                "ema_decay": 0.99
                            },
                            "dtype": "bf16"
                        },
                        "model": {
                            "name_or_path": "/flux_diffusers", # Modelo base local
                            "is_flux": True,
                            "quantize": True
                        },
                        "sample": {
                            "sampler": "flowmatch",
                            "sample_every": 500,
                            "width": 1024,
                            "height": 1024,
                            "prompts": [
                                f"a portrait of {trigger_word}",
                                f"{trigger_word} sitting in a cafe"
                            ],
                            "neg": "",
                            "seed": 42,
                            "walk_seed": True,
                            "guidance_scale": 4,
                            "sample_steps": 20
                        }
                    }
                ],
                "meta": {
                    "name": character_name,
                    "version": "1.0"
                }
            }
        }
        
        config_path = "/root/ai-toolkit/train_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)
            
        print(f"[{character_name}] Iniciando treinamento de LoRA. Dataset com {len(images_b64)} imagens.")
        
        # 3. Rodar o treinamento
        try:
            # Roda o ai-toolkit
            os.chdir("/root/ai-toolkit")
            process = subprocess.Popen(["python", "run.py", "train_config.yaml"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                print(line.strip())
            process.wait()
            
            if process.returncode != 0:
                raise Exception(f"Treinamento falhou com codigo {process.returncode}")
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
        # 4. Mover o LoRA resultante para o volume ComfyUI
        user_loras_dir = f"/loras_output/loras/users/{user_id}"
        os.makedirs(user_loras_dir, exist_ok=True)
        
        # ai-toolkit salva em /tmp/output/{character_name}/{character_name}.safetensors
        output_safetensors = f"/tmp/output/{character_name}/{character_name}.safetensors"
        final_lora_path = os.path.join(user_loras_dir, f"{character_name}.safetensors")
        
        if os.path.exists(output_safetensors):
            shutil.copy2(output_safetensors, final_lora_path)
            print(f"LoRA salvo com sucesso em: {final_lora_path}")
            return {
                "status": "success",
                "lora_path": f"users/{user_id}/{character_name}.safetensors",
                "time_seconds": time.time() - t0
            }
        else:
            return {"status": "error", "message": "Treinamento concluiu mas safetensors nao foi encontrado."}
