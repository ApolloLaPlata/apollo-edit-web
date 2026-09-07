import os
import subprocess
import json

class VoiceCloner:
    def __init__(self, config):
        self.config = config
        self.characters_dir = os.path.join(self.config.get_path("base_dir"), "backend", "storage", "characters")
        os.makedirs(self.characters_dir, exist_ok=True)
        
    def get_character_path(self, character_name: str) -> str:
        safe_name = character_name.replace(" ", "_").lower()
        return os.path.join(self.characters_dir, safe_name)

    def init_character_folder(self, character_name: str) -> str:
        """Cria as pastas básicas para um novo personagem."""
        char_dir = self.get_character_path(character_name)
        emotions_dir = os.path.join(char_dir, "emotions")
        os.makedirs(emotions_dir, exist_ok=True)
        
        # Cria profile basico se nao existir
        profile_path = os.path.join(char_dir, "profile.json")
        if not os.path.exists(profile_path):
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump({"name": character_name, "base_voice": "", "variants": {}}, f, indent=4)
                
        return char_dir

    def clean_audio(self, input_path: str, output_path: str) -> bool:
        """
        Limpa o áudio usando FFmpeg (silence removal e normalização).
        Isso é crucial para o modelo extrair um timbre perfeito.
        """
        try:
            # Comando FFmpeg para remover silêncio no início e fim, e normalizar o volume
            # -af silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.1...
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-af", "silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-50dB,loudnorm",
                "-ar", "24000", "-ac", "1", # Conversão padrão para melhor leitura TTS
                output_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
            print(f"✅ [VoiceCloner] Áudio limpo com sucesso: {output_path}")
            return True
        except Exception as e:
            print(f"❌ [VoiceCloner] Falha ao limpar áudio {input_path}: {e}")
            return False

    def generate_emotional_variants(self, character_name: str, base_clean_audio: str) -> bool:
        """
        Gera as 6 variantes emocionais a partir do áudio limpo usando Fish Speech.
        """
        char_dir = self.get_character_path(character_name)
        emotions_dir = os.path.join(char_dir, "emotions")
        
        # Mapeamento de Emoções do Sistema para Tags Viscerais do Fish Speech
        emotion_map = {
            "neutral": {"tags": "(calm) (serious)", "text": "Este é um teste neutro para calibrar a minha voz."},
            "sad": {"tags": "(crying loudly) (sobbing)", "text": "Eu não acredito que isso aconteceu... Meu coração está partido."},
            "angry": {"tags": "(furious) (shouting)", "text": "Isso é um absurdo! Eu não vou aceitar uma situação dessas de jeito nenhum!"},
            "happy": {"tags": "(laughing) (chuckling)", "text": "Hahaha! Que notícia maravilhosa, eu estou muito feliz com isso!"},
            "fearful": {"tags": "(terrified) (panting)", "text": "Por favor, não faz isso... Eu estou com muito medo do que pode acontecer."},
            "surprised": {"tags": "(shocked) (gasping)", "text": "Nossa! Eu jamais imaginaria que as coisas iam virar desse jeito!"}
        }
        
        print(f"🧠 [VoiceCloner] Iniciando geração de variantes para '{character_name}'...")
        
        from backend.cloud_tools.engines.fish_speech_engine import FishSpeechEngine
        # Busca URL do config ou usa localhost por padrão
        fish_url = self.config.get("fish_speech_url", "http://localhost:8080")
        engine = FishSpeechEngine(api_url=fish_url)
        
        sucesso_total = True
        
        for emot, data in emotion_map.items():
            out_wav = os.path.join(emotions_dir, f"{emot}.wav")
            print(f"🔄 Gerando take [{emot.upper()}]...")
            
            success = engine.generate_emotional_take(
                text=data["text"], 
                emotion_tags=data["tags"], 
                reference_audio_path=base_clean_audio, 
                output_path=out_wav
            )
            
            if not success:
                sucesso_total = False
                print(f"⚠️ Falha na geração do Fish Speech para '{emot}'. O servidor local está rodando (docker compose up)?")
                # Fallback: Copia o áudio base limpo para que o XTTS não quebre por falta de arquivo
                import shutil
                shutil.copy2(base_clean_audio, out_wav)
                print(f"🔄 Fallback aplicado para '{emot}'. Usando voz base.")
                
        if sucesso_total:
            print(f"🎉 Matriz emocional de '{character_name}' criada com sucesso na pasta 'emotions/'.")
        
        return True
