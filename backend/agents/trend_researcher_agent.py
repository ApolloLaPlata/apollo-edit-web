import logging
import asyncio
import time
import sqlite3
import os
import random
from backend.agents.base_agent import BaseAgent
from backend.router.waterfall_router import router_instance

logger = logging.getLogger("TrendResearcher")

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'apollo_users.db')

class TrendResearcherAgent(BaseAgent):
    """
    Agente Olheiro (Trend Researcher).
    Vasculha agregadores e APIs em busca das IAs mais hypadas do mercado.
    Salva relatórios no DB para análise do Maestro/Diretor Geral.
    """
    def __init__(self):
        super().__init__(agent_name="TrendResearcher")
        self.router = router_instance

    async def start_patrol(self):
        self.is_running = True
        logger.info("🔭 [TrendResearcher] Olheiro ativado. Procurando tendências de IA...")
        self.update_memory("status", "researching_trends")
        
        while self.is_running:
            try:
                await self._research_trends()
                
                self.memory_data["last_action"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.save_memory()
                
                # Executa a cada 24 horas (86400 segundos)
                await asyncio.sleep(86400)
            except Exception as e:
                logger.error(f"[TrendResearcher] Erro durante pesquisa: {e}")
                await asyncio.sleep(600)

    async def _research_trends(self):
        """Busca modelos hypados e salva no banco de dados."""
        logger.debug("[TrendResearcher] Analisando fontes de tendências...")
        
        # Simulação de scraping (HuggingFace / Notícias / Twitter / OpenRouter)
        trends_found = [
            {
                "model_name": "x-ai/grok-3-vision",
                "trending_score": random.randint(80, 100),
                "analysis_text": "Batendo recordes de velocidade na geração de vídeo. Milhões de citações nas últimas 24h.",
                "source_url": "https://openrouter.ai/x-ai/grok-3-vision"
            },
            {
                "model_name": "banana-corp/nano-banana-v2",
                "trending_score": random.randint(70, 95),
                "analysis_text": "Comunidade abraçou fortemente pela baixíssima latência. Ideal para Extensões Locais.",
                "source_url": "https://huggingface.co/nano-banana-v2"
            },
            {
                "model_name": "anthropic/claude-4.6-sonnet",
                "trending_score": 99,
                "analysis_text": "Benchmarks impressionantes de raciocínio. Excelente para o núcleo do Maestro.",
                "source_url": "https://openrouter.ai/anthropic/claude-4.6-sonnet"
            }
        ]
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_trends_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT,
                    trending_score INTEGER,
                    analysis_text TEXT,
                    source_url TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            new_discoveries = 0
            for trend in trends_found:
                cursor.execute("SELECT id FROM ai_trends_reports WHERE model_name = ?", (trend["model_name"],))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO ai_trends_reports (model_name, trending_score, analysis_text, source_url)
                        VALUES (?, ?, ?, ?)
                    """, (trend["model_name"], trend["trending_score"], trend["analysis_text"], trend["source_url"]))
                    new_discoveries += 1
                    
                    # Testando o Roteador no modo BAIXO CUSTO para uma tarefa simples de validação
                    prompt = f"Gere uma mensagem curta para o Diretor Geral confirmando que o modelo '{trend['model_name']}' foi detectado nos radares como tendência."
                    res = await self.router.request_ai_generation(prompt=prompt, system_prompt="Você é um assistente de pesquisa.")
                    
                    if res.get("status") == "success":
                        await self.speak("trend_detected", {"model": trend["model_name"], "score": trend["trending_score"], "msg": res["content"]})
                        
            conn.commit()
            conn.close()
            
            if new_discoveries > 0:
                logger.warning(f"🔭 [TrendResearcher] {new_discoveries} novas IAs bombando foram encontradas e reportadas!")
        except Exception as e:
            logger.error(f"[TrendResearcher] Erro ao salvar tendências: {e}")
