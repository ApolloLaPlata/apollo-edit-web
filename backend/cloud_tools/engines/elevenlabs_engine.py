"""
Motor TTS ElevenLabs
======================================
Implementação direta usando a API oficial da ElevenLabs para o Plano Premium.
Utilizado para criação de Matrizes Emocionais Zero-Shot hiper-realistas.
"""

import os
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

class ElevenLabsEngine:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("ElevenLabs API Key é obrigatória.")
        self.client = ElevenLabs(api_key=api_key)
        self.model_id = "eleven_multilingual_v2"
        
    def clone_voice(self, name: str, description: str, file_paths: list[str]) -> str:
        """
        Sobe um áudio para a conta e cria uma Voice Clone.
        Retorna o voice_id da nova voz criada.
        """
        print(f"[ELEVENLABS] Subindo arquivos para clonagem de '{name}'...")
        
        # O SDK pede uma lista de File-like objects ou caminhos
        # Na v1 do SDK, client.voices.add espera "files" que é um iterável de paths ou file-likes
        try:
            new_voice = self.client.voices.ivc.create(
                name=name,
                description=description,
                files=[open(p, "rb") for p in file_paths]
            )
            print(f"[ELEVENLABS] Voz criada com sucesso! ID: {new_voice.voice_id}")
            return new_voice.voice_id
        except Exception as e:
            raise RuntimeError(f"Erro ao clonar voz na ElevenLabs: {e}")

    def generate_voice(self, text: str, voice_id: str) -> bytes:
        """
        Gera áudio usando uma voz específica e retorna os bytes do áudio.
        """
        print(f"[ELEVENLABS] Gerando áudio para '{text[:30]}...' com voz {voice_id}")
        try:
            response_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                output_format="mp3_44100_128",
                text=text,
                model_id=self.model_id,
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.8,
                    style=0.0,
                    use_speaker_boost=True
                )
            )
            
            # O retorno é um generator de bytes
            audio_bytes = b"".join([chunk for chunk in response_generator])
            return audio_bytes
        except Exception as e:
            raise RuntimeError(f"Erro na geração de áudio ElevenLabs: {e}")

    def delete_voice(self, voice_id: str):
        """
        Deleta uma voz da conta para liberar espaço.
        """
        print(f"[ELEVENLABS] Deletando voz ID: {voice_id}")
        self.client.voices.delete(voice_id=voice_id)
        print("[ELEVENLABS] Voz deletada.")
