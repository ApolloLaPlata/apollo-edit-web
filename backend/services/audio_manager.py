import os
from typing import Optional

# Evita falha se o modal não estiver instalado localmente (embora esteja)
try:
    import modal
    from backend.cloud_tools.engines.stable_audio_engine import StableAudioEngine
except ImportError:
    StableAudioEngine = None


class AudioManager:
    """
    Manager responsável por centralizar a comunicação com a nuvem (Modal)
    para geração de Efeitos Sonoros (SFX) e Música de Fundo (BGM).
    Usa o Stable Audio Open 1.0 (Comercialmente liberado sob a Stability AI Community License).
    """

    def __init__(self):
        # A inicialização real do motor do Modal ocorre apenas no momento do chamado
        # para evitar bloqueios assíncronos no start do backend.
        pass

    def generate_sfx(self, prompt: str, duration_s: float = 3.0, output_path: str = "output_sfx.wav") -> Optional[str]:
        """
        Gera um efeito sonoro (Foley/SFX) e salva no caminho desejado.
        """
        if not StableAudioEngine:
            raise RuntimeError("Dependências do Modal não estão instaladas ou configuradas.")
        
        # A API do Stable Audio exige prompts no formato de condicionamento de áudio.
        # Adicionamos '44k, high quality' para melhorar a geração se o usuário não incluir.
        enhanced_prompt = f"44k, high quality, {prompt}" if "44k" not in prompt else prompt
        
        print(f"[AudioManager] Solicitando geração de SFX na nuvem: {prompt}")
        engine = StableAudioEngine()
        
        try:
            wav_data = engine.generate_audio.remote(
                prompt=enhanced_prompt, 
                duration_s=duration_s, 
                num_inference_steps=200
            )
            with open(output_path, "wb") as f:
                f.write(wav_data)
            print(f"[AudioManager] SFX gerado com sucesso: {output_path}")
            return output_path
        except Exception as e:
            print(f"[AudioManager] Falha ao gerar SFX: {e}")
            return None

    def generate_music(self, prompt: str, duration_s: float = 15.0, output_path: str = "output_bgm.wav") -> Optional[str]:
        """
        Gera música de fundo (BGM) e salva no caminho desejado.
        """
        if not StableAudioEngine:
            raise RuntimeError("Dependências do Modal não estão instaladas ou configuradas.")
            
        enhanced_prompt = f"44k, high quality, instrumental, {prompt}" if "44k" not in prompt else prompt
        
        print(f"[AudioManager] Solicitando geração de Música na nuvem: {prompt}")
        engine = StableAudioEngine()
        
        try:
            # Reutiliza o mesmo endpoint (generate_audio suporta até 47s de áudio geral)
            wav_data = engine.generate_audio.remote(
                prompt=enhanced_prompt, 
                duration_s=duration_s, 
                num_inference_steps=200
            )
            with open(output_path, "wb") as f:
                f.write(wav_data)
            print(f"[AudioManager] Música gerada com sucesso: {output_path}")
            return output_path
        except Exception as e:
            print(f"[AudioManager] Falha ao gerar Música: {e}")
            return None
