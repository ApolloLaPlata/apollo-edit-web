import logging
import asyncio
import time
import httpx
import sqlite3
import os
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("PricingScraper")

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'apollo_users.db')
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/models"

class PricingScraperAgent(BaseAgent):
    """
    Agente Scraper de Preços e Modelos de IA.
    Responsável por catalogar novos modelos no OpenRouter e manter
    a tabela models_pricing atualizada com os valores dinâmicos.
    """
    def __init__(self):
        super().__init__(agent_name="PricingScraper")
        
        if "scraper_stats" not in self.memory_data["data"]:
            self.memory_data["data"]["scraper_stats"] = {
                "new_models": 0,
                "updated_models": 0,
                "total_models": 0
            }
            self.save_memory()

    async def start_patrol(self):
        self.is_running = True
        logger.info("🕵️‍♂️ [PricingScraper] Scraper de Preços acordou. Iniciando vigilância no OpenRouter...")
        self.update_memory("status", "scraping_prices")
        
        while self.is_running:
            try:
                await self._scrape_prices()
                
                self.memory_data["last_action"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.save_memory()
                
                # Executa a cada 12 horas (43200 segundos) para evitar ban de API
                await asyncio.sleep(43200)
            except Exception as e:
                logger.error(f"[PricingScraper] Erro durante o scraping: {e}")
                await asyncio.sleep(3600)

    async def _scrape_prices(self):
        """Busca preços do OpenRouter via httpx."""
        logger.debug("[PricingScraper] Consultando API OpenRouter...")
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                res = await client.get(OPENROUTER_API_URL)
                res.raise_for_status()
                models_data = res.json().get('data', [])
        except Exception as e:
            logger.error(f"[PricingScraper] Falha ao acessar OpenRouter: {e}")
            self.memory_data["alerts"].append(f"Erro na API OpenRouter: {e}")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Criando a tabela caso não exista para evitar falhas no deploy zero
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS models_pricing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_id TEXT UNIQUE,
                    provider TEXT,
                    tier TEXT,
                    input_price_per_1m REAL,
                    output_price_per_1m REAL,
                    margin_multiplier REAL DEFAULT 1.3,
                    rpm_limit INTEGER DEFAULT 0,
                    tpm_limit INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'Ativo',
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            new_count = 0
            updated_count = 0

            for model in models_data:
                model_id = model.get('id')
                pricing = model.get('pricing', {})
                
                try:
                    prompt_price_1m = float(pricing.get('prompt', 0)) * 1_000_000
                    completion_price_1m = float(pricing.get('completion', 0)) * 1_000_000
                except ValueError:
                    prompt_price_1m = 0.0
                    completion_price_1m = 0.0
                    
                provider = "OpenRouter"
                if model_id.startswith('x-ai/'):
                    provider = "Grok"
                elif model_id.startswith('deepseek/'):
                    provider = "DeepSeek"
                    
                tier = "Free" if (prompt_price_1m == 0 and completion_price_1m == 0) else "Premium"
                
                cursor.execute("SELECT id, input_price_per_1m, output_price_per_1m FROM models_pricing WHERE model_id = ?", (model_id,))
                row = cursor.fetchone()
                
                if row:
                    old_input = float(row['input_price_per_1m'] or 0)
                    old_output = float(row['output_price_per_1m'] or 0)
                    
                    if abs(old_input - prompt_price_1m) > 0.0001 or abs(old_output - completion_price_1m) > 0.0001:
                        cursor.execute("""
                            UPDATE models_pricing 
                            SET input_price_per_1m = ?, output_price_per_1m = ?, tier = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (prompt_price_1m, completion_price_1m, tier, row['id']))
                        updated_count += 1
                else:
                    cursor.execute("""
                        INSERT INTO models_pricing (model_id, provider, tier, input_price_per_1m, output_price_per_1m, status)
                        VALUES (?, ?, ?, ?, ?, 'Ativo')
                    """, (model_id, provider, tier, prompt_price_1m, completion_price_1m))
                    new_count += 1

            conn.commit()
            
            # Atualiza o painel de métricas
            cursor.execute("SELECT COUNT(*) FROM models_pricing")
            total = cursor.fetchone()[0]
            
            self.memory_data["data"]["scraper_stats"] = {
                "new_models": new_count,
                "updated_models": updated_count,
                "total_models": total
            }
            logger.info(f"🕵️‍♂️ [PricingScraper] Scan Concluído. {new_count} novos, {updated_count} atualizados.")
            
            # Avisar o Market Analyst se houverem modelos novos via HiveBus
            if new_count > 0:
                await self.speak("new_models_found", {"count": new_count, "source": "OpenRouter"})
                
            conn.close()
        except Exception as e:
            logger.error(f"[PricingScraper] Erro de DB: {e}")
