import logging
import asyncio
import time
import shutil
import os
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("ZeladorAgent")

class ZeladorAgent(BaseAgent):
    """
    Agente Autônomo de Limpeza (O Zelador).
    Aba do Painel: Infraestrutura/Disco
    """
    def __init__(self):
        super().__init__(agent_name="Zelador")
        self.tmp_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'tmp')
        os.makedirs(self.tmp_dir, exist_ok=True)
        
        if "cleaned_files" not in self.memory_data["data"]:
            self.memory_data["data"]["cleaned_files"] = 0
            self.memory_data["data"]["disk_free_gb"] = 0.0
            self.save_memory()

    async def start_patrol(self):
        self.is_running = True
        logger.info("🧹 [Zelador] Iniciando rotina de limpeza...")
        self.update_memory("status", "cleaning")
        
        while self.is_running:
            try:
                # Lógica de Espaço em Disco
                total, used, free = shutil.disk_usage("/")
                free_gb = free / (2**30)
                self.memory_data["data"]["disk_free_gb"] = round(free_gb, 2)
                
                if free_gb < 5:
                    logger.critical(f"⚠️ [Zelador] ALERTA! Espaço em disco baixo: {free_gb:.2f} GB!")
                    self.memory_data["alerts"].append("Espaço em disco abaixo de 5GB.")
                else:
                    self.memory_data["alerts"] = [] # Limpa os alertas se resolver

                # Lógica de limpar arquivos velhos (> 24h)
                current_time = time.time()
                files_deleted = 0
                for filename in os.listdir(self.tmp_dir):
                    file_path = os.path.join(self.tmp_dir, filename)
                    if os.path.isfile(file_path):
                        if current_time - os.path.getmtime(file_path) > 86400:
                            os.remove(file_path)
                            files_deleted += 1
                            
                if files_deleted > 0:
                    logger.info(f"🧹 [Zelador] Removidos {files_deleted} arquivos antigos.")
                    self.memory_data["data"]["cleaned_files"] += files_deleted

                self.memory_data["last_action"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.save_memory()
                
                await asyncio.sleep(3600) # Patrulha a cada hora
                
            except Exception as e:
                logger.error(f"[Zelador] Erro na limpeza: {e}")
                self.update_memory("status", "error")
                await asyncio.sleep(3600)
