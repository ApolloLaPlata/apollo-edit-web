import logging
import asyncio
import json
from typing import Dict, Any, List
import os

from backend.router.waterfall_router import WaterfallRouter

logger = logging.getLogger("DirectorEngine")

class AsyncDirectorEngine:
    """
    Motor Assíncrono do Diretor de IA.
    Substitui o antigo `ai_director_pipeline.py`.
    Usa o WaterfallRouter para despachar análises de roteiro, limpeza semântica e curadoria de B-Rolls
    para a Colmeia de LLMs sem travar o Event Loop.
    """
    def __init__(self, router: WaterfallRouter):
        self.router = router

    async def analyze_script(self, text: str) -> Dict[str, Any]:
        """
        Análise Semântica do script para gerar palavras-chave de B-Rolls.
        """
        logger.info(f"🧠 [DirectorEngine] Analisando roteiro de {len(text)} caracteres...")
        
        # Lendo a Bíblia de Edição
        knowledge_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "cinematography_guidelines.md")
        guidelines = ""
        if os.path.exists(knowledge_path):
            with open(knowledge_path, "r", encoding="utf-8") as f:
                guidelines = f.read()

        prompt = f"""Você é um Diretor de Arte Cinematográfica e Editor de Vídeo Profissional de um estúdio.
Seu trabalho não é apenas gerar palavras-chave, mas DECUPAR um roteiro em uma sequência de cortes matemáticos e orgânicos, aplicando técnicas reais de retenção de atenção.

LEIA E OBEDEÇA AS SEGUINTES DIRETRIZES DE CINEMATOGRAFIA OBRIGATORIAMENTE:
=================
{guidelines}
=================

Analise o roteiro abaixo e devolva APENAS um JSON contendo a "Cut Sheet" (Lista de Cortes) estruturada.
Formato JSON exigido:
{{
  "scenes": [
    {{
      "text_snippet": "o pedaço exato do roteiro falado nesta cena",
      "broll_prompt": "Prompt visual cinematográfico avançado em inglês descrevendo a ação (ex: 'Close-up of a neon glowing eye, low key lighting')",
      "camera_angle": "Wide / Medium / Close-up / POV",
      "duration_seconds": 3.5,
      "transition": "cut / j-cut / l-cut / whip-pan",
      "energy_level": "high / medium / low"
    }}
  ]
}}

O ROTEIRO:
{text}
"""
        response = await self.router.request_ai_generation(
            prompt=prompt
        )
        response_text = response.get("content", "")

        
        try:
            # Limpeza do markdown ```json
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
                
            data = json.loads(response_text)
            
            # Garantia de Retrocompatibilidade (para não quebrar sistemas atuais que esperam 'broll_keywords')
            if "broll_keywords" not in data:
                keywords = []
                for scene in data.get("scenes", []):
                    # Extrai algumas palavras do prompt cinematográfico para servir como keyword legada
                    prompt_words = scene.get("broll_prompt", "").split()
                    keywords.extend([w for w in prompt_words if len(w) > 4][:2])
                data["broll_keywords"] = list(set(keywords)) if keywords else ["cinematic", "abstract"]

            logger.info(f"✅ [DirectorEngine] Decupagem (Cut Sheet) concluída: {len(data.get('scenes', []))} cenas estruturadas.")
            return data
        except Exception as e:
            logger.error(f"❌ [DirectorEngine] Falha ao parsear Cut Sheet do LLM: {e}\nRaw: {response_text}")
            return {"scenes": [{"text_snippet": text, "broll_prompt": "cinematic abstract technology", "camera_angle": "Medium", "duration_seconds": 4.0, "transition": "cut", "energy_level": "medium"}]}

    async def suggest_sfx(self, clip_context: str) -> str:
        """
        Gera uma sugestão de Sound Effect baseada no contexto do clipe.
        """
        prompt = f"""Baseado na cena descrita: "{clip_context}"
Sugira um tipo de efeito sonoro (SFX) curto para transição. Retorne apenas o nome (ex: "whoosh", "impact", "riser")."""

        sfx = await self.router.dispatch_llm_request(
            prompt=prompt,
            role="fast",
            max_tokens=10
        )
        return sfx.strip().lower()
