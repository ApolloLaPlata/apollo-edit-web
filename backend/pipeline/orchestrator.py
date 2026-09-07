import os
from backend.pipeline.script_engine import ScriptEngine
from backend.pipeline.voice_engine import VoiceEngine
from backend.pipeline.image_engine import ImageEngine
from backend.pipeline.video_engine import VideoEngine

class Orchestrator:
    def __init__(self):
        self.script_engine = ScriptEngine()
        self.voice_engine = VoiceEngine()
        self.image_engine = ImageEngine()
        self.video_engine = VideoEngine()
        
    def run_pipeline(self, topic: str, ref_audio_b64: str, ref_text: str, output_dir: str):
        """
        Executa a esteira completa:
        1. Gera o roteiro
        2. Para cada cena, gera o áudio e a imagem
        3. Junta tudo no FFmpeg
        """
        print(f"=== Iniciando Pipeline Apollo Edit para: '{topic}' ===")
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Roteiro
        script = self.script_engine.generate_script(topic)
        print(f"Roteiro gerado: {script.title} ({len(script.scenes)} cenas)")
        
        image_paths = []
        audio_paths = []
        
        # 2. Geração de Assets por Cena
        for cena in script.scenes:
            print(f"Processando Cena {cena.id}...")
            
            # Áudio
            audio_out = os.path.join(output_dir, f"cena_{cena.id}.wav")
            self.voice_engine.generate_audio(
                text=cena.text_to_speak,
                ref_audio_b64=ref_audio_b64,
                ref_text=ref_text,
                instruct=cena.instruct_mood,
                out_path=audio_out,
                temperature=cena.temperature
            )
            audio_paths.append(audio_out)
            
            # Imagem
            img_out = os.path.join(output_dir, f"cena_{cena.id}.jpg")
            self.image_engine.generate_image(cena.image_prompt, img_out)
            image_paths.append(img_out)
            
        # 3. Montagem
        video_out = os.path.join(output_dir, "video_final.mp4")
        self.video_engine.assemble_video(image_paths, audio_paths, video_out)
        print(f"=== Pipeline Finalizado: {video_out} ===")

if __name__ == "__main__":
    # Teste simples de invocação
    orchestrator = Orchestrator()
    print("Orquestrador instanciado com sucesso!")
