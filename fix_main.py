import re

filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

correct_code = '''# O Maestro agora é instanciado aqui com acesso ao Gateway para poder "pensar"
from backend.agents.maestro_agent import MaestroAgent
from backend.agents.user_concierge import UserConciergeAgent

maestro = MaestroAgent(router_instance=gateway)
concierge = UserConciergeAgent(router_instance=gateway)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──────────────────────────────────────────────
    logger.info("🚀 Iniciando Motor Central Apollo...")
    from backend.services.render_queue import render_queue
    render_queue.start()

    # 1. Colmeia de Agentes Administrativos
    asyncio.create_task(watchdog.start_patrol())
    asyncio.create_task(cerbero.start_patrol())
    # O Zelador (Espaço e Lixo)
    zelador = ZeladorAgent()
    asyncio.create_task(zelador.start_patrol())
    
    # Os Economistas (Analista Financeiro e Scraper de Preços)'''

content = re.sub(r'# O Maestro agora é instanciado aqui com acesso ao Gateway para poder "pensar"\n    \n    # Os Economistas \(Analista Financeiro e Scraper de Preços\)', correct_code, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
