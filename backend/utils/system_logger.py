import logging
from logging.handlers import RotatingFileHandler
import os
import sys

# Força o stdout a usar UTF-8 no Windows para evitar o erro cp1252 com emojis
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def setup_system_logger():
    """
    Configura o logger global do sistema para capturar todos os eventos e erros.
    Gera arquivos de log rotativos (max 10MB) na pasta 'logs/'.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "apollo_system.log")
    
    # Formatador detalhado para os arquivos
    file_formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - %(name)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    
    # Formatador simples para o terminal
    console_formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - %(message)s"
    )

    # Handler de Arquivo Rotativo (10MB max, guarda os últimos 5)
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)

    # Handler de Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Configurando o root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove handlers antigos se houver (para evitar logs duplicados no reload)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info("[SystemLogger] Logging inicializado. Gravando no apollo_system.log")

# Chamada imediata para garantir que o logger seja configurado ao importar este módulo
setup_system_logger()
