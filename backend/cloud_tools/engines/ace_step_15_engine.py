import modal
import os
import base64
import time
from backend.cloud_tools.modal_app import app

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg", "wget")
    .pip_install(
        "huggingface_hub",
        "soundfile",
        "librosa",
        "scipy",
        "fastapi",
        "torch==2.4.1",
        "torchaudio",
        "torchvision",
    )
    .run_commands(
        "git clone https://github.com/ace-step/ACE-Step-1.5.git /ace-step-15",
        "cd /ace-step-15 && sed -i '/flash-attn/d' requirements.txt && pip install -r requirements.txt"
    )
)

vol = modal.Volume.from_name("model-cache-vol", create_if_missing=True)

@app.function(
    volumes={"/apollo_volume": vol},
    timeout=1800,
)
def download_acestep_models():
    import os
    from huggingface_hub import snapshot_download

    base_path = "/apollo_volume/models/acestep"
    os.makedirs(base_path, exist_ok=True)
    
    main_path = os.path.join(base_path, "Ace-Step1.5")
    if not os.path.exists(main_path):
        print(f"Baixando repositório oficial ACE-Step 1.5 em {main_path}...")
        snapshot_download("ACE-Step/Ace-Step1.5", local_dir=main_path)
        
    xl_path = os.path.join(base_path, "acestep-v15-xl-sft")
    if not os.path.exists(xl_path):
        print(f"Baixando DiT XL SFT em {xl_path}...")
        snapshot_download("ACE-Step/acestep-v15-xl-sft", local_dir=xl_path)
        
    lm4b_path = os.path.join(base_path, "acestep-5Hz-lm-4B")
    if not os.path.exists(lm4b_path):
        print(f"Baixando LM 4B em {lm4b_path}...")
        snapshot_download("ACE-Step/acestep-5Hz-lm-4B", local_dir=lm4b_path)

    print("Modelos do ACE-Step disponíveis no volume.")

@app.cls(
    image=image,
    gpu="H100",
    volumes={"/apollo_volume": vol},
    timeout=600
)
class AceStep15Engine:
    @modal.enter()
    def setup(self):
        import sys
        sys.path.append("/ace-step-15")
        
        print("[AceStep15Engine] Inicializando Handlers (LLM + DiT)... (MODELO XL DE 10B!)")
        from acestep.handler import AceStepHandler
        from acestep.llm_inference import LLMHandler
        
        self.dit_handler = AceStepHandler()
        self.llm_handler = LLMHandler()
        
        print("[AceStep15Engine] Baixando/Carregando modelos XL na VRAM...")
        # A API original do ACE espera `config_path` como o nome do folder. E espera que exista um folder VAE próximo.
        # Nós já baixamos Ace-Step1.5 (que tem o VAE).
        # Vamos passar config_path direto pra onde está o arquivo se for possivel, ou mapear.
        self.dit_handler.initialize_service(
            project_root="/apollo_volume/models/acestep",
            config_path="acestep-v15-xl-sft",
            device="cuda",
            use_flash_attention=False,
            compile_model=False
        )
        self.llm_handler.initialize(
            checkpoint_dir=None,
            lm_model_path="/apollo_volume/models/acestep/acestep-5Hz-lm-4B",
            backend="pt"
        )
        print("[AceStep15Engine] Modelos XL carregados!")

    @modal.method()
    def generate(self, style_tags: str, lyrics: str, length_seconds: int = 60, steps: int = 64, use_erg_lyric: bool = True) -> dict:
        t0 = time.time()
        print(f"[AceStep15Engine] Gerando audio de {length_seconds}s com {steps} steps (XL MODEL)...")
        
        import io
        import uuid
        out_dir = "/tmp"
        
        try:
            import sys
            sys.path.append("/ace-step-15")
            from acestep.inference import GenerationParams, GenerationConfig, generate_music
            
            params = GenerationParams(
                task_type="text2music",
                caption=style_tags,
                lyrics=lyrics,
                duration=float(length_seconds),
                inference_steps=steps
            )
            config = GenerationConfig()
            
            # Parametros avanados para melhorar a coerencia de instrumentais!
            config.guidance_scale = 7.0
            config.omega_scale = 7.0
            config.cfg_type = "true_cfg"
            config.use_erg_tag = True
            config.use_erg_lyric = use_erg_lyric
            config.use_erg_diffusion = True
            
            result = generate_music(
                self.dit_handler, 
                self.llm_handler, 
                params, 
                config, 
                save_dir=out_dir
            )
            
            if not result.success or not result.audios:
                raise Exception(f"Falha na geracao. Error: {getattr(result, 'error_msg', 'unknown')}")
            
            out_file = result.audios[0]['path']
            
            with open(out_file, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
                
            return {
                "status": "success",
                "audio_base64": audio_b64,
                "render_time_seconds": round(time.time() - t0, 2)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
