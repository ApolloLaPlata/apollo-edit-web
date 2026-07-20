import logging
import asyncio
import json
from typing import Dict, Any, List

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
        
        prompt = f"""Você é o Diretor de Arte de um vídeo.
Analise o roteiro abaixo e extraia palavras-chave em inglês para buscar vídeos de banco de imagens (B-Rolls).
Retorne APENAS um JSON no formato: {{"broll_keywords": ["keyword1", "keyword2"]}}

Roteiro:
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
            logger.info(f"✅ [DirectorEngine] Análise concluída: {data.get('broll_keywords', [])}")
            return data
        except Exception as e:
            logger.error(f"❌ [DirectorEngine] Falha ao parsear resposta do LLM: {e}\nRaw: {response_text}")
            return {"broll_keywords": ["cinematic", "abstract", "technology"]}

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
