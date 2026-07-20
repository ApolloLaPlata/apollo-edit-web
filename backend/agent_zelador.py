import os
import logging
import asyncio
import time
import shutil

logger = logging.getLogger("Zelador")
logger.setLevel(logging.INFO)

class ZeladorAgent:
    """
    Agente Autônomo de Manutenção (O Zelador).
    Função: Monitorar o espaço em disco do servidor,
    apagar arquivos temporários antigos e limpar o cache.
    """
    def __init__(self):
        self.is_active = True
        self.tmp_dir = os.path.join(os.path.dirname(__file__), '..', 'tmp')
        os.makedirs(self.tmp_dir, exist_ok=True)
        
        # Carrega variáveis do ambiente (.env)
        try:
            from dotenv import load_dotenv
            load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
        except ImportError:
            pass
            
        # O Zelador usa um modelo super leve (Groq Llama 3 8B) para relatórios
        self.api_key = os.environ.get("GROQ_API_KEY", "")

    async def patrol_loop(self):
        """
        Loop de manutenção contínua.
        """
        logger.info("🧹 [Zelador] Iniciando rotina de limpeza...")
        while self.is_active:
            try:
                # 1. Verifica arquivos no /tmp mais velhos que 24 horas
                current_time = time.time()
                for filename in os.listdir(self.tmp_dir):
                    file_path = os.path.join(self.tmp_dir, filename)
                    if os.path.isfile(file_path):
                        # Verifica se é mais velho que 24h (86400 segundos)
                        if current_time - os.path.getmtime(file_path) > 86400:
                            os.remove(file_path)
                            logger.info(f"🧹 [Zelador] Removido arquivo antigo: {filename}")
                
                # 2. Verifica espaço em disco do Servidor (VPS)
                total, used, free = shutil.disk_usage("/")
                free_gb = free / (2**30)
                if free_gb < 5: # Menos de 5GB livres
                    logger.critical(f"⚠️ [Zelador] ALERTA! Espaço em disco baixo: {free_gb:.2f} GB livres!")
                    # Aqui ele poderia enviar uma notificação Telegram para o CEO
                
                # Dorme por 1 hora
                await asyncio.sleep(3600)

            except Exception as e:
                logger.error(f"[Zelador] Erro na limpeza: {e}")
                await asyncio.sleep(3600)

zelador = ZeladorAgent()
