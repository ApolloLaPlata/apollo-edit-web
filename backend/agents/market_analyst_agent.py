import logging
import asyncio
import time
import sqlite3
import os
from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.router.waterfall_router import router_instance

logger = logging.getLogger("MarketAnalyst")

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'financial_agent', 'economy.db')

class MarketAnalystAgent(BaseAgent):
    """
    Gestor Financeiro / Analista de Mercado.
    Aba do Painel: Economia & Marketing
    Monitora uso da economia, ajusta custos baseados na demanda
    e avisa o Maestro se houver escassez de recursos.
    """
    def __init__(self):
        super().__init__(agent_name="MarketAnalyst")
        self.router = router_instance
        
        if "market_health" not in self.memory_data["data"]:
            self.memory_data["data"]["market_health"] = "stable"
            self.memory_data["data"]["last_analysis"] = ""
            self.save_memory()

    async def start_patrol(self):
        self.is_running = True
        logger.info("📈 [MarketAnalyst] Analista de Mercado acordou. Analisando o fluxo de moedas...")
        self.update_memory("status", "analyzing_market")
        
        while self.is_running:
            try:
                await self._analyze_economy()
                
                self.memory_data["last_action"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.save_memory()
                
                # Executa a cada 2 horas (7200 segundos)
                await asyncio.sleep(7200)
            except Exception as e:
                logger.error(f"[MarketAnalyst] Erro durante a análise: {e}")
                await asyncio.sleep(300)

    async def _analyze_economy(self):
        """Analisa a inflação das moedas e envia relatórios/insights via Hive Bus."""
        logger.debug("[MarketAnalyst] Coletando métricas do banco SQLite (economy.db)...")
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Conta o total de moedas no sistema (dinheiro em circulação)
            c.execute("SELECT SUM(coins), SUM(chips_llm), SUM(gpu_tokens) FROM users")
            row = c.fetchone()
            
            if row and row[0]:
                total_coins = row[0]
                total_chips = row[1]
                total_gpus = row[2]
                
                logger.info(f"📈 [MarketAnalyst] Circulação: {total_coins} Coins | {total_chips} Chips | {total_gpus} GPU Tokens")
                
                # Regra de Inflação (Simulação de precificação dinâmica):
                # Se houver mais de 50.000 moedas em circulação, o mercado está inflacionado
                if total_coins > 50000:
                    msg = "⚠️ Alerta de Inflação! Muitos usuários estão acumulando Apollo Coins. Considere criar uma 'Sale' na loja ou encarecer o Custo de Render."
                    logger.warning(msg)
                    self.memory_data["alerts"].append(msg)
                    
                    # Notifica a colmeia (o Maestro vai interceptar isso e avisar o CEO)
                    await self.speak("market_alert", {"type": "inflation", "message": msg, "total_coins": total_coins})
                else:
                    self.memory_data["alerts"] = [] # Clear alerts
                    self.memory_data["data"]["market_health"] = "healthy"

            conn.close()
            
        except Exception as e:
            logger.error(f"[MarketAnalyst] Erro ao conectar no DB da Economia: {e}")

