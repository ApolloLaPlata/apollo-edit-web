import json
import os
from pydantic import BaseModel, Field
from typing import List

class Scene(BaseModel):
    id: int
    text_to_speak: str = Field(description="O texto exato e puro, sem colchetes ou tags, que o narrador irá ler.")
    image_prompt: str = Field(description="Prompt descritivo em inglês para o Nano Banana / Flux gerar a imagem da cena.")
    instruct_mood: str = Field(description="Instrução detalhada de palco (direção) para o motor de voz (Qwen3). Ex: O ator fala em tom de suspense...")
    temperature: float = Field(description="Temperatura de geração da fala (Qwen3). Use valores baixos (0.5 a 0.8) para falas retas, sérias ou jornalísticas. Use valores extremos (1.5 a 2.0) para risadas, choro, surto de raiva ou emoção agressiva.")

class Script(BaseModel):
    title: str
    scenes: List[Scene]

class ScriptEngine:
    def __init__(self):
        # Aqui inicializamos o cliente LLM (ex: OpenAI)
        pass
        
    def generate_script(self, topic: str) -> Script:
        """
        Recebe um tema e gera um roteiro completo estruturado em cenas, 
        incluindo os textos estimulantes, as instruções teatrais para o Qwen 
        e os prompts visuais para as imagens.
        """
        # TODO: Implementar chamada real ao LLM forçando a saída para bater com o Pydantic Script
        # Exemplo Mock:
        return Script(
            title=f"Curiosidades sobre {topic}",
            scenes=[
                Scene(
                    id=1,
                    text_to_speak="Você não vai acreditar no que eu acabei de descobrir... É bizarro!",
                    image_prompt="A hyper-realistic cinematic shot of a mysterious glowing artifact in a dark room, 4k, masterpiece",
                    instruct_mood="O ator fala em um tom de sussurro misterioso e chocado, como se estivesse revelando um segredo proibido.",
                    temperature=1.2
                )
            ]
        )
