import os
import asyncio
import logging
import httpx
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Inicializa o Logger Rotativo do Sistema
import backend.utils.system_logger

# Arquitetura Nativa (Gateway, Agentes e Rotas)
from backend.router.waterfall_router import WaterfallRouter, CLOUD_ACCOUNTS
from backend.agents.watchdog_agent import WatchdogAgent
from backend.agents.cerbero_agent import CerberoAgent
from backend.agents.zelador_agent import ZeladorAgent
from backend.agents.market_analyst_agent import MarketAnalystAgent
from backend.agents.pricing_scraper_agent import PricingScraperAgent
from backend.agents.traffic_manager_agent import TrafficManagerAgent
from backend.agents.trend_researcher_agent import TrendResearcherAgent
from backend.agents.hive_bus import hive_bus
from backend.api import routes_audio_lab
from backend.api import routes_video, routes_admin, routes_whatsapp, routes_phantom, worker_routes, routes_economy, routes_ui_ws, routes_render, routes_auth, routes_payments, routes_webhooks, routes_subtitles, routes_podcast, routes_tts, routes_dubbing, routes_editor, routes_ai_director, routes_clip_factory, routes_auto_mapper, routes_dark_facil, routes_settings, routes_queue, routes_copilot
# Sistema de Economia e Load Balancer
from backend.financial_agent.coin_ledger import OPERATION_COSTS
from backend.financial_agent.subscription_manager import get_all_plans_comparison
from backend.cloud_tools.account_pool import account_pool

# Carregar variÃƒÂ¡veis de ambiente
load_dotenv()

# ConfiguraÃƒÆ’Ã‚Â§ÃƒÆ’Ã‚Â£o de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ApolloServer")

# Instanciando o Gateway Global e a Colmeia de Agentes Administrativos
gateway = WaterfallRouter()
watchdog = WatchdogAgent(router_instance=gateway)
cerbero = CerberoAgent()

# O Maestro agora ÃƒÆ’Ã‚Â© instanciado aqui com acesso ao Gateway para poder "pensar"
from backend.agents.maestro_agent import MaestroAgent
from backend.agents.user_concierge import UserConciergeAgent

maestro = MaestroAgent(router_instance=gateway)
concierge = UserConciergeAgent(router_instance=gateway)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("🚀 Iniciando Motor Central Apollo...")
    # from backend.services.render_queue import render_queue
    # render_queue.start()

    # 1. Colmeia de Agentes Administrativos
    asyncio.create_task(watchdog.start_patrol())
    asyncio.create_task(cerbero.start_patrol())
    # O Zelador (Espaço e Lixo)
    zelador = ZeladorAgent()
    asyncio.create_task(zelador.start_patrol())
    
    # Os Economistas (Analista Financeiro e Scraper de Preços)
    analyst = MarketAnalystAgent()
    asyncio.create_task(analyst.start_patrol())
    
    scraper = PricingScraperAgent()
    asyncio.create_task(scraper.start_patrol())
    
    # Marketing e TendÃƒÆ’Ã‚Âªncias (Gestor de TrÃƒÆ’Ã‚Â¡fego e Olheiro)
    traffic_mgr = TrafficManagerAgent()
    asyncio.create_task(traffic_mgr.start_patrol())
    
    trend_res = TrendResearcherAgent()
    asyncio.create_task(trend_res.start_patrol())
    asyncio.create_task(maestro.start_patrol())
    asyncio.create_task(concierge.start_patrol())
    logger.info("\U0001f6e1\ufe0f Colmeia Multi-Agente ativada (Watchdog, C\xe9rbero, Zelador, Maestro, Concierge).")
    
    # Injetando a referÃƒÆ’Ã‚Âªncia do Maestro nas rotas de WhatsApp
    routes_whatsapp.set_maestro(maestro)

    # 2. Inscreve o Maestro no HiveBus para receber todos os eventos
    async def maestro_hive_listener(sender: str, topic: str, payload: dict):
        """O Maestro escuta todos os t\xf3picos cr\xedticos do HiveBus."""
        if topic == "financial.alert":
            logger.warning(f"[Maestro] \U0001f4a1 Alerta financeiro recebido de {sender}: {payload}")
            # Aqui: enviar via WhatsApp webhook (pr\xf3ximo passo)
        elif topic == "job.failed":
            logger.error(f"[Maestro] \u274c Job falhou reportado por {sender}: {payload}")

    hive_bus.subscribe("financial.alert", maestro_hive_listener)
    hive_bus.subscribe("job.failed", maestro_hive_listener)
    hive_bus.subscribe("*", maestro_hive_listener)
    logger.info("\U0001f4fb HiveBus conectado. Maestro escutando todos os t\xf3picos.")

    # 3. Inicia rota\xe7\xe3o de sa\xfade do Pool de Contas (a cada 30min)
    async def pool_health_loop():
        while True:
            await asyncio.sleep(1800)  # 30 minutos
            status = account_pool.status_report()
            for acc in status:
                if not acc["is_healthy"]:
                    await hive_bus.publish(
                        "financial.alert",
                        sender="PoolMonitor",
                        payload={"type": "account_unhealthy", "account": acc["label"]}
                    )
    asyncio.create_task(pool_health_loop())
    logger.info("\U0001fa7a Pool Monitor iniciado (ciclo de 30min).")

    logger.info("\u2705 Apollo Motor Central ONLINE.")
    yield
    # ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ SHUTDOWN ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ Ã¢â€šÂ¬
    logger.info("ÃƒÂ°Ã…Â¸Ã¢â‚¬ÂºÃ¢â‚¬Ëœ Encerrando Apollo Motor Central...")
    # from backend.services.render_queue import render_queue
    # render_queue.stop()


app = FastAPI(
    title="Apollo Edit Web - Motor Central Nativo",
    version="2.0.0",
    lifespan=lifespan
)

from fastapi.middleware.cors import CORSMiddleware
from backend.middleware.rate_limiter import RateLimitMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import httpx
from fastapi.responses import JSONResponse

@app.get("/info")
async def gradio_info_proxy():
    # ZeroGPU proxy needs a 200 OK JSON response for /info, but gr.mount_gradio_app
    # moves it to /gradio_api/info. We proxy it internally.
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://127.0.0.1:7860/gradio_api/info", timeout=5.0)
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

app.add_middleware(RateLimitMiddleware)

from backend.api import routes_audio_lab
from backend.api import routes_video, routes_admin, routes_whatsapp, routes_phantom, worker_routes, routes_economy, routes_ui_ws, routes_render, routes_auth, routes_payments, routes_webhooks, routes_subtitles, routes_podcast, routes_tts, routes_dubbing, routes_editor, routes_ai_director, routes_clip_factory, routes_auto_mapper, routes_dark_facil, routes_settings, routes_queue, routes_copilot, routes_youtube, routes_studio, routes_storage_gateway, routes_radio, routes_voice

@app.get("/api/mobile/pending_approvals")
def get_pending_approvals():
    return {"status": "ok", "pending": []}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro Global nÃƒÂ£o tratado na rota {request.url.path}: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"message": "Ocorreu um erro interno no servidor. Os logs foram capturados pelo zelador."}
    )

# Registrando as Rotas de VÃƒÂ­deo (Site), Admin (Painel), WhatsApp, Workers, Phantom Fleet, Economia e UI WebSocket
app.include_router(routes_audio_lab.router)
app.include_router(routes_video.router)
app.include_router(routes_subtitles.router)
app.include_router(routes_editor.router)
app.include_router(routes_ai_director.router)
app.include_router(routes_clip_factory.router)
app.include_router(routes_auto_mapper.router)
app.include_router(routes_dark_facil.router)
app.include_router(routes_settings.router)
app.include_router(routes_queue.router)
app.include_router(routes_copilot.router)
app.include_router(routes_podcast.router)
app.include_router(routes_tts.router)
from backend.api import routes_tts_v2
app.include_router(routes_tts_v2.router)
app.include_router(routes_dubbing.router)
app.include_router(routes_admin.router)
app.include_router(routes_whatsapp.router)
app.include_router(worker_routes.router)
app.include_router(routes_phantom.router)
app.include_router(routes_economy.router)
app.include_router(routes_ui_ws.router)
app.include_router(routes_render.router)
app.include_router(routes_auth.router)
app.include_router(routes_payments.router)
app.include_router(routes_webhooks.router)
app.include_router(routes_youtube.router)
app.include_router(routes_studio.router)
app.include_router(routes_storage_gateway.router)
app.include_router(routes_radio.router)
app.include_router(routes_voice.router)

from backend.api import routes_autoblog
app.include_router(routes_autoblog.router)

# Rotas de Modelos Musicais (YuE / ACE-Step)
from backend.api import routes_audio
app.include_router(routes_audio.router)

from backend.routes import broadcaster
app.include_router(broadcaster.router, prefix="/api/broadcaster", tags=["Broadcaster"])

from fastapi.responses import HTMLResponse
from backend.routes import broadcaster_admin
app.include_router(broadcaster_admin.router, prefix="/api/broadcaster/admin", tags=["Broadcaster Admin"])

@app.get("/painel", response_class=HTMLResponse, tags=["Broadcaster Admin"])
async def serve_painel():
    with open("painel_index.html", "r", encoding="utf-8") as f:
        return f.read()

# @app.get("/")
# def read_root():
#     return {"status": "online", "message": "Apollo Motor Central Operacional"}

@app.get("/health")
def health_check():
    """Endpoint para o Painel Administrativo monitorar a saÃƒÆ’Ã‚Âºde da Nuvem"""
    
    active_lightning_keys = sum(1 for acc in CLOUD_ACCOUNTS.get("lightning", []) if acc["status"] == "active")
    total_lightning_keys = len(CLOUD_ACCOUNTS.get("lightning", []))
    
    return {
        "status": "healthy",
        "watchdog_active": watchdog.is_running,
        "cloud_status": {
            "lightning_ai": f"{active_lightning_keys}/{total_lightning_keys} contas ativas",
            "openrouter": "Online (Fallback)",
        }
    }

import httpx
from fastapi.responses import StreamingResponse
from starlette.requests import Request

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def catch_all_proxy(request: Request, path_name: str):
    """
    Cavalo de Troia Reverse Proxy:
    Redireciona todo o tráfego que não é da API para o Next.js rodando localmente na porta 3000.
    Isso permite servir o Autoblog SSR no Hugging Face pela mesma porta 7860.
    """
    url = f"http://127.0.0.1:3000/{path_name}"
    
    # Repassa os parâmetros da query string
    if request.url.query:
        url += f"?{request.url.query}"
        
    client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
    
    try:
        # Prepara a requisição para o Next.js
        req = client.build_request(
            request.method,
            url,
            headers={k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")},
            content=await request.body()
        )
        
        # Envia a requisição
        resp = await client.send(req, stream=True)
        
        # Devolve a resposta (StreamingResponse permite carregar arquivos pesados sem engasgar)
        return StreamingResponse(
            resp.aiter_raw(),
            status_code=resp.status_code,
            headers={k: v for k, v in resp.headers.items() if k.lower() not in ("content-encoding", "content-length")},
            background=client.aclose
        )
    except httpx.RequestError as e:
        await client.aclose()
        return {"error": "Autoblog SSR Proxy Failed", "details": str(e)}

if __name__ == "__main__":

    import uvicorn
    # Rodando o servidor local na porta 8000
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True, reload_excludes=["logs/*", "*.log", "Workspaces/*", ".agents/*", "scratch/*", "backend/storage/*", "backend/storage/memories/*", "*.json"])













