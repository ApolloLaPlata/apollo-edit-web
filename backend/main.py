import os
import asyncio
import logging
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import backend.utils.system_logger
from backend.middleware.rate_limiter import RateLimitMiddleware

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ApolloServer")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("✅ Apollo Edit Web (Motor Desacoplado) ONLINE.")
    yield
    logger.info("🛑 Encerrando Apollo Edit Web...")

app = FastAPI(
    title="Apollo Edit Web - UI & Orchestration",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro Global não tratado na rota {request.url.path}: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"message": "Ocorreu um erro interno no servidor."}
    )

# Importando apenas as rotas relevantes para Edição e UI (Zero-Trust/Desacopladas)
from backend.api import (
    routes_export,
    routes_video, 
    routes_subtitles, 
    routes_editor, 
    routes_ai_director, 
    routes_clip_factory, 
    routes_auto_mapper, 
    routes_settings, 
    routes_queue, 
    routes_render, 
    routes_auth, 
    routes_payments, 
    routes_webhooks, 
    routes_ui_ws, 
    routes_storage_gateway,
    routes_nanobanana, routes_copilot, routes_tts_proxy
)

# Registrando rotas focadas em Edição Visual e Frontend
app.include_router(routes_video.router)
app.include_router(routes_subtitles.router)
app.include_router(routes_editor.router)
app.include_router(routes_export.router)
app.include_router(routes_ai_director.router)
app.include_router(routes_clip_factory.router)
app.include_router(routes_auto_mapper.router)
app.include_router(routes_settings.router)
app.include_router(routes_queue.router)
app.include_router(routes_render.router)
app.include_router(routes_auth.router)
app.include_router(routes_payments.router)
app.include_router(routes_webhooks.router)
app.include_router(routes_ui_ws.router)
app.include_router(routes_storage_gateway.router)
app.include_router(routes_nanobanana, routes_copilot, routes_tts_proxy.router)


app.include_router(routes_copilot, routes_tts_proxy.router)


app.include_router(routes_tts_proxy.router)

