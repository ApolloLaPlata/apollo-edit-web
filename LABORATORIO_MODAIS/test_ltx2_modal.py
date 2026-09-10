import modal
from diffusers import LTX2Pipeline
from transformers import T5EncoderModel
import torch

app = modal.App("test-ltx2")

apollo_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg", "libsm6", "libxext6")
    .pip_install("torch==2.5.1", "torchvision", "torchaudio", extra_options="--index-url https://download.pytorch.org/whl/cu124")
    .pip_install("diffusers", "transformers", "accelerate", "safetensors", "sentencepiece", "huggingface_hub", "scipy")
)

@app.function(image=apollo_image, gpu="A100", timeout=1200)
def test_ltx2_shape():
    sf_file = "/models/huggingface/hub/models--Lightricks--LTX-2.3/ltx-2.3-22b-distilled.safetensors"
    # test fallback if it's not downloaded
    import os
    if not os.path.exists(sf_file):
        print("Arquivo não encontrado no volume de teste, usando URL do HF...")
        sf_file = "https://huggingface.co/Lightricks/LTX-2.3/resolve/main/ltx-2.3-22b-distilled.safetensors"
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        # LTX 2.3 usa Gemma 3
        tokenizer = AutoTokenizer.from_pretrained(
            "CalamitousFelicitousness/LTX-2.3-Sulphur2-Base-Diffusers", 
            subfolder="tokenizer"
        )
        # Note: AutoModelForCausalLM usually resolves to Gemma3ForConditionalGeneration
        text_encoder = AutoModelForCausalLM.from_pretrained(
            "CalamitousFelicitousness/LTX-2.3-Sulphur2-Base-Diffusers", 
            subfolder="text_encoder", 
            torch_dtype=torch.bfloat16
        )
        print("Gemma3 text_encoder carregado.")
        
        from diffusers import AutoencoderKLLTX2Audio
        from diffusers.pipelines.ltx2.connectors import LTX2TextConnectors
        from diffusers.pipelines.ltx2.vocoder import LTX2Vocoder

        audio_vae = AutoencoderKLLTX2Audio.from_pretrained(
            "CalamitousFelicitousness/LTX-2.3-Sulphur2-Base-Diffusers",
            subfolder="audio_vae",
            torch_dtype=torch.bfloat16
        )
        connectors = LTX2TextConnectors.from_pretrained(
            "CalamitousFelicitousness/LTX-2.3-Sulphur2-Base-Diffusers",
            subfolder="connectors"
        )
        vocoder = LTX2Vocoder.from_pretrained(
            "CalamitousFelicitousness/LTX-2.3-Sulphur2-Base-Diffusers",
            subfolder="vocoder"
        )
        print("Componentes de áudio e conectores carregados.")

        pipe = LTX2Pipeline.from_single_file(
            sf_file, 
            config="CalamitousFelicitousness/LTX-2.3-Sulphur2-Base-Diffusers",
            tokenizer=tokenizer,
            text_encoder=text_encoder,
            audio_vae=audio_vae,
            connectors=connectors,
            vocoder=vocoder,
            torch_dtype=torch.bfloat16, 
            local_files_only=False
        )
        print("Pipeline LTX2 carregado com sucesso com config específica!")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ltx2_shape.remote()
