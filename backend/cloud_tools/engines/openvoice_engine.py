import modal
import os
import subprocess
import base64

# A imagem docker com os requerimentos do OpenVoice v2
openvoice_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg", "git", "wget", "pkg-config", "libavformat-dev", "libavcodec-dev", "libavdevice-dev", "libavutil-dev", "libswscale-dev", "libswresample-dev", "libavfilter-dev")
    .run_commands("git clone https://github.com/myshell-ai/OpenVoice.git /openvoice")
    .workdir("/openvoice")
    .pip_install("torch==2.1.2", "torchaudio==2.1.2", "torchvision==0.16.2", index_url="https://download.pytorch.org/whl/cu121")
    .pip_install(
        "librosa==0.9.2",
        "faster-whisper",
        "pydub==0.25.1",
        "wavmark==0.0.3",
        "numpy",
        "eng_to_ipa==0.0.2",
        "inflect==7.0.0",
        "unidecode==1.3.7",
        "whisper-timestamped==1.14.2",
        "jieba==0.42.1",
        "pypinyin==0.50.0",
        "cn2an==0.5.22"
    )
    .run_commands(
        "pip install git+https://github.com/myshell-ai/MeloTTS.git",
        "python -m unidic download"
    )
)

from backend.cloud_tools.modal_app import app
vol = modal.Volume.from_name("openvoice-weights", create_if_missing=True)

@app.cls(
    image=openvoice_image,
    gpu="L4",
    volumes={"/openvoice/weights": vol},
    timeout=600
)
class OpenVoiceEngine:
    @modal.enter()
    def setup(self):
        import zipfile
        import os
        
        # Download weights if not present
        if not os.path.exists("/openvoice/weights/checkpoints_v2"):
            print("Downloading OpenVoice v2 checkpoints from HF...")
            os.makedirs("/openvoice/weights", exist_ok=True)
            # The download is now handled by the persistent volume script.
            # If it's missing, it will raise an error rather than hanging.
            raise Exception("Pesos do OpenVoice não encontrados no volume! Rode o script de download do HuggingFace.")
            
        import torch
        from openvoice import se_extractor
        from openvoice.api import ToneColorConverter
        
        self.ckpt_converter = "/openvoice/weights/checkpoints_v2/converter"
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        self.tone_color_converter = ToneColorConverter(f"{self.ckpt_converter}/config.json", device=self.device)
        self.tone_color_converter.load_ckpt(f"{self.ckpt_converter}/checkpoint.pth")

    @modal.method()
    def clone_voice(self, source_audio_b64: str, reference_audio_b64: str) -> str:
        import uuid
        import torch
        from openvoice import se_extractor
        
        uid = uuid.uuid4().hex
        source_path = f"/tmp/{uid}_source.wav"
        ref_path = f"/tmp/{uid}_ref.wav"
        out_path = f"/tmp/{uid}_output.wav"
        
        with open(source_path, "wb") as f:
            f.write(base64.b64decode(source_audio_b64))
        with open(ref_path, "wb") as f:
            f.write(base64.b64decode(reference_audio_b64))
            
        target_se, audio_name = se_extractor.get_se(ref_path, self.tone_color_converter, vad=True)
        source_se, _ = se_extractor.get_se(source_path, self.tone_color_converter, vad=True)
        
        self.tone_color_converter.convert(
            audio_src_path=source_path, 
            src_se=source_se, 
            tgt_se=target_se, 
            output_path=out_path,
            message="@MyShell",
            tau=0.0
        )
        
        with open(out_path, "rb") as f:
            result_b64 = base64.b64encode(f.read()).decode("utf-8")
            
        os.remove(source_path)
        os.remove(ref_path)
        os.remove(out_path)
        
        return result_b64
