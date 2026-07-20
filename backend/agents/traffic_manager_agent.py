import logging
import asyncio
import time
import sqlite3
import os
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("TrafficManager")

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'apollo_users.db')

class TrafficManagerAgent(BaseAgent):
    """
    Gestor de Tráfego AI.
    Monitora o CTR (Click-Through Rate) dos banners injetados na plataforma.
    Desativa automaticamente campanhas com baixa performance.
    """
    def __init__(self):
        super().__init__(agent_name="TrafficManager")

    async def start_patrol(self):
        self.is_running = True
        logger.info("🚥 [TrafficManager] Gestor de Tráfego ativado. Monitorando CTR...")
        self.update_memory("status", "monitoring_traffic")
        
        while self.is_running:
            try:
                await self._analyze_performance()
                
                self.memory_data["last_action"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.save_memory()
                
                # Executa a cada 1 hora (3600 segundos)
                await asyncio.sleep(3600)
            except Exception as e:
                logger.error(f"[TrafficManager] Erro durante análise: {e}")
                await asyncio.sleep(300)

    async def _analyze_performance(self):
        """Analisa views e clicks das campanhas na tabela ad_campaigns."""
        logger.debug("[TrafficManager] Calculando métricas de conversão...")
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Criando tabelas caso não existam no ambiente novo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ad_campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    image_url TEXT,
                    link_url TEXT,
                    is_active INTEGER DEFAULT 1,
                    views INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_analysis_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_text TEXT,
                    recommended_actions TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("SELECT * FROM ad_campaigns WHERE is_active = 1")
            active_ads = cursor.fetchall()
            
            actions = []
            
            for ad in active_ads:
                views = ad['views']
                clicks = ad['clicks']
                title = ad['title']
                
                if views > 50:
                    ctr = (clicks / views) * 100
                    
                    # Demite o anúncio se CTR < 0.5% num volume aceitável
                    if ctr < 0.5 and views > 200:
                        actions.append(f"PAUSADO '{title}' por baixa conversão ({ctr:.2f}%).")
                        cursor.execute("UPDATE ad_campaigns SET is_active = 0 WHERE id = ?", (ad['id'],))
                        
                        # Avisar via HiveBus
                        await self.speak("campaign_paused", {"title": title, "ctr": ctr, "views": views})

            if actions:
                report_text = "⚠️ Ações do Gestor de Tráfego:\n" + "\n".join(actions)
                cursor.execute("""
                    INSERT INTO market_analysis_reports (report_text, recommended_actions)
                    VALUES (?, ?)
                """, (report_text, "Campanhas otimizadas automaticamente."))
                logger.warning(f"[TrafficManager] {len(actions)} campanhas foram pausadas por baixa performance.")
                
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"[TrafficManager] Erro no banco de dados: {e}")
