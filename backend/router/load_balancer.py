"""
Apollo Load Balancer v1.0
Roteador inteligente para as 4 contas Lightning AI.

Lógica de Prioridade:
  1. Seleciona a conta com maior saldo de crédito disponível.
  2. Se a conta principal falhar, redireciona para o backup automaticamente.
  3. Quando TODAS as contas esgotam, retorna erro "Free Crystals Unavailable".

Configuração:
  Defina as variáveis de ambiente abaixo para cada conta.
  Ex: LIGHTNING_KEY_FLUX1, LIGHTNING_KEY_FLUX2, etc.
"""

import os
import time
import asyncio
import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date
import json

# Importa o Cão de Guarda (Serverless Manager)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from cloud_tools.lightning_manager import watchdog
except ImportError:
    watchdog = None

# ─────────────────────────────────────────
# CONFIGURAÇÃO DAS 4 CONTAS LIGHTNING AI
# ─────────────────────────────────────────
# IMPORTANTE: Preencha com suas credenciais reais ou use .env
ACCOUNTS = [
    {
        "id":        "flux-prod",
        "label":     "⚡ Conta 1 — Flux (Produção)",
        "role":      "image",           # 'image' ou 'video'
        "priority":  1,                 # 1 = maior prioridade (usa primeiro)
        "studio":    "Maquina Flux Dev",
        "api_url":   os.getenv("LIGHTNING_URL_FLUX1", "http://localhost:8001"),
        "api_key":   os.getenv("LIGHTNING_KEY_FLUX1", "APOLLO_SECRET_KEY_123"),
        "budget_usd": 15.00,
        "storage_cost_usd": 3.50,       # Estimativa: custo mensal de armazenar Flux (~23GB)
    },
    {
        "id":        "video-prod",
        "label":     "🎬 Conta 2 — Vídeo (Produção)",
        "role":      "video",
        "priority":  1,
        "studio":    "Modelos Medios",
        "api_url":   os.getenv("LIGHTNING_URL_VID1", "http://localhost:8002"),
        "api_key":   os.getenv("LIGHTNING_KEY_VID1", "APOLLO_SECRET_KEY_123"),
        "budget_usd": 15.00,
        "storage_cost_usd": 2.80,       # LTX + WAN modelos (~13GB)
    },
    {
        "id":        "flux-backup",
        "label":     "🔄 Conta 3 — Flux (Backup)",
        "role":      "image",
        "priority":  2,                 # 2 = só usa se prioridade 1 falhar
        "studio":    "apollo-flux-2",
        "api_url":   os.getenv("LIGHTNING_URL_FLUX2", "http://localhost:8003"),
        "api_key":   os.getenv("LIGHTNING_KEY_FLUX2", "APOLLO_SECRET_KEY_123"),
        "budget_usd": 15.00,
        "storage_cost_usd": 3.50,
    },
    {
        "id":        "video-backup",
        "label":     "🔄 Conta 4 — Vídeo (Backup)",
        "role":      "video",
        "priority":  2,
        "studio":    "apollo-video-2",
        "api_url":   os.getenv("LIGHTNING_URL_VID2", "http://localhost:8004"),
        "api_key":   os.getenv("LIGHTNING_KEY_VID2", "APOLLO_SECRET_KEY_123"),
        "budget_usd": 15.00,
        "storage_cost_usd": 2.80,
    },
]

# ─────────────────────────────────────────
# ESTADO EM MEMÓRIA (futuro: Redis/Supabase)
# ─────────────────────────────────────────
# Simula saldo restante (em produção, consulta Lightning SDK real)
account_state = {
    acc["id"]: {
        "credit_used_usd": acc["storage_cost_usd"],  # começa já descontado o storage
        "generations_today": 0,
        "last_error": None,
        "healthy": True,
    }
    for acc in ACCOUNTS
}

# Contagem global de gerações hoje
daily_stats = {"date": str(date.today()), "total_generations": 0}

# Rastreamento de ociosidade para o Cão de Guarda (Serverless)
last_used_timestamps = {}

# ─────────────────────────────────────────
# LÓGICA DE ROTEAMENTO
# ─────────────────────────────────────────
def get_credit_remaining(account_id: str) -> float:
    """Retorna crédito líquido restante em USD."""
    acc = next(a for a in ACCOUNTS if a["id"] == account_id)
    state = account_state[account_id]
    return acc["budget_usd"] - state["credit_used_usd"]

def select_best_account(role: str) -> Optional[dict]:
    """
    Seleciona a melhor conta para o role ('image' ou 'video').
    Prioridade: maior saldo primeiro, fallback para backup se produção cair.
    """
    candidates = [a for a in ACCOUNTS if a["role"] == role]
    
    # Filtra contas saudáveis com crédito suficiente (mínimo $0.10 para gerar)
    available = [
        a for a in candidates
        if account_state[a["id"]]["healthy"]
        and get_credit_remaining(a["id"]) > 0.10
    ]
    
    if not available:
        return None  # Todas as contas desse tipo esgotadas
    
    # Ordena: prioridade 1 antes de 2, depois pelo maior crédito restante
    available.sort(key=lambda a: (a["priority"], -get_credit_remaining(a["id"])))
    return available[0]

def estimate_cost(model: str) -> float:
    """Custo estimado em USD por geração por modelo."""
    costs = {
        "flux": 0.004,      # ~250 gerações por $1
        "flux-pro": 0.012,
        "ltx": 0.008,
        "wan": 0.010,
        "hailuo": 0.015,    # API externa, custo maior
        "kling": 0.012,
    }
    return costs.get(model, 0.005)

# ─────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────
app = FastAPI(title="Apollo Multi-Account Load Balancer", version="1.0.0")

async def delayed_shutdown_check(studio_name: str, delay_sec: int = 300):
    """
    Background task: aguarda X segundos e desliga a máquina 
    se não tiver recebido novos pedidos nesse meio tempo.
    """
    await asyncio.sleep(delay_sec)
    time_since_last = time.time() - last_used_timestamps.get(studio_name, 0)
    if time_since_last >= delay_sec:
        print(f"[Watchdog-Cron] Estúdio '{studio_name}' ocioso por {delay_sec}s. Desligando...")
        if watchdog:
            watchdog.shutdown(studio_name)
    else:
        print(f"[Watchdog-Cron] Cancelando desligamento de '{studio_name}', ele foi usado recentemente.")

class RouteRequest(BaseModel):
    model: str          # "flux", "ltx", "wan", etc.
    prompt: str
    user_id: str
    job_id: str         # Vem do Maestro

class AccountStatusResponse(BaseModel):
    accounts: list

@app.get("/status")
async def get_all_account_status():
    """Retorna o status financeiro de todas as 4 contas. Usado pelo painel Admin."""
    result = []
    for acc in ACCOUNTS:
        state = account_state[acc["id"]]
        remaining = get_credit_remaining(acc["id"])
        pct = (remaining / acc["budget_usd"]) * 100
        result.append({
            "id": acc["id"],
            "label": acc["label"],
            "role": acc["role"],
            "priority": acc["priority"],
            "budget_usd": acc["budget_usd"],
            "storage_cost_usd": acc["storage_cost_usd"],
            "credit_used_usd": round(state["credit_used_usd"], 3),
            "credit_remaining_usd": round(remaining, 3),
            "credit_pct": round(pct, 1),
            "generations_today": state["generations_today"],
            "healthy": state["healthy"],
            "last_error": state["last_error"],
            "alert": pct < 20,   # Alerta quando menos de 20% restante
            "critical": pct < 5, # Crítico quando menos de 5%
        })
    return {"accounts": result, "daily_stats": daily_stats}

@app.post("/route")
async def route_generation(req: RouteRequest, background_tasks: BackgroundTasks):
    """
    Ponto de entrada principal do Load Balancer.
    Recebe do Maestro e redireciona para a conta correta.
    """
    # Determina o 'role' baseado no modelo
    role = "video" if req.model in ["ltx", "wan", "hailuo", "kling"] else "image"
    
    # Seleciona a melhor conta disponível
    account = select_best_account(role)
    
    if not account:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "FREE_CRYSTALS_UNAVAILABLE",
                "message": "Todas as cotas gratuitas foram usadas hoje. Use um Cristal Pago ou tente amanhã!",
                "retry_at": "Amanhã às 00:00 (renovação mensal/diária)"
            }
        )
    
    acc_id = account["id"]
    studio_name = account.get("studio")
    headers = {"Authorization": f"Bearer {account['api_key']}"}
    payload = {"prompt": req.prompt}
    
    print(f"[Router] Job {req.job_id} → {account['label']} ({role})")
    
    # [WATCHDOG] Acorda o estúdio associado à conta (se estiver dormindo) e extrai a URL real
    target_url = f"{account['api_url']}/predict"
    if watchdog and studio_name:
        watchdog.wake_up(studio_name)
        status = watchdog.get_status(studio_name)
        if status and "url" in status:
            target_url = f"{status['url']}/predict"
            print(f"[Router] URL dinâmica capturada: {target_url}")
    
    try:
        data = None
        max_retries = 6
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=180.0) as client:
                    response = await client.post(target_url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    break # Sucesso, sai do loop de retry
            except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as conn_err:
                # Se for erro 502 (Bad Gateway) ou erro de conexão, a máquina pode estar iniciando
                is_booting_error = isinstance(conn_err, httpx.ConnectError) or isinstance(conn_err, httpx.TimeoutException) or (hasattr(conn_err, 'response') and conn_err.response is not None and conn_err.response.status_code in [502, 503])
                if is_booting_error and attempt < max_retries - 1:
                    print(f"[Router] O servidor LitServe de '{studio_name}' ainda não está pronto (Tentativa {attempt+1}/{max_retries}). Aguardando 15s...")
                    await asyncio.sleep(15)
                else:
                    raise conn_err

        
        # Atualiza o consumo da conta
        cost = estimate_cost(req.model)
        account_state[acc_id]["credit_used_usd"] += cost
        account_state[acc_id]["generations_today"] += 1
        daily_stats["total_generations"] += 1
        
        # [WATCHDOG] Atualiza timestamp e agenda checagem de desligamento (5 minutos)
        if studio_name:
            last_used_timestamps[studio_name] = time.time()
            background_tasks.add_task(delayed_shutdown_check, studio_name, 300)
        
        print(f"[Router] ✅ Geração OK. Custo: ${cost:.4f}. Saldo restante Conta {acc_id}: ${get_credit_remaining(acc_id):.2f}")
        
        return {
            "status": "success",
            "account_used": acc_id,
            "account_label": account["label"],
            "credit_remaining": get_credit_remaining(acc_id),
            "result": data
        }
    
    except Exception as e:
        # Marca a conta como não saudável temporariamente
        account_state[acc_id]["healthy"] = False
        account_state[acc_id]["last_error"] = str(e)
        
        print(f"[Router] ❌ Conta {acc_id} falhou: {e}. Tentando próxima...")
        
        # Retry automático na próxima conta disponível
        fallback = select_best_account(role)
        if fallback and fallback["id"] != acc_id:
            # Re-rota para o backup
            return await route_generation(req, background_tasks)
        
        raise HTTPException(
            status_code=500,
            detail={"code": "ALL_ACCOUNTS_FAILED", "message": str(e)}
        )

@app.post("/admin/heal/{account_id}")
async def heal_account(account_id: str):
    """Marca uma conta como saudável novamente (após manutenção)."""
    if account_id not in account_state:
        raise HTTPException(status_code=404, detail="Conta não encontrada.")
    account_state[account_id]["healthy"] = True
    account_state[account_id]["last_error"] = None
    return {"status": "healed", "account_id": account_id}

@app.post("/admin/reset_daily")
async def reset_daily_stats():
    """Reseta as estatísticas diárias (chamado pelo cron job à meia-noite)."""
    for acc_id in account_state:
        account_state[acc_id]["generations_today"] = 0
    daily_stats["total_generations"] = 0
    daily_stats["date"] = str(date.today())
    return {"status": "reset", "date": daily_stats["date"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
