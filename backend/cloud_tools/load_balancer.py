"""
load_balancer.py — API Interna do Load Balancer Apollo
=======================================================
Expõe endpoints para despachar jobs e verificar status das contas.
Roda como um microsserviço interno consumido pelos agentes e pelo servidor principal.

Endpoints:
  POST /dispatch   — Escolhe a melhor conta e executa um job
  GET  /status     — Retorna status de todas as contas do pool
  POST /report_result — Extensões/webhooks reportam resultado de um job
  POST /mark_error  — Registra erro em uma conta (chamado internamente)
"""

import asyncio
import logging
import os
import time
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .account_pool import account_pool, LightningAccount

logger = logging.getLogger("LoadBalancer")

app = FastAPI(title="Apollo Load Balancer", version="1.0.0")

# ─────────────────────────────────────────
# REGISTRO DE JOBS EM ANDAMENTO
# ─────────────────────────────────────────
# job_id → { account_id, status, result_url, started_at }
active_jobs: dict[str, dict] = {}
completed_jobs: dict[str, dict] = {}  # Histórico dos últimos 500 jobs


# ─────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────
class DispatchRequest(BaseModel):
    prompt: str
    role: Optional[str] = "general"     # "image", "video", "general"
    priority: Optional[str] = "normal"  # "normal", "nitro", "nitro_master"
    user_id: Optional[str] = None       # Para rastreamento financeiro
    metadata: Optional[dict] = {}

class DispatchResponse(BaseModel):
    job_id: str
    account_id: str
    account_label: str
    status: str
    message: str

class JobResultReport(BaseModel):
    job_id: str
    result_url: Optional[str] = None
    error: Optional[str] = None

class ErrorReport(BaseModel):
    account_id: str
    error_message: str


# ─────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────
@app.get("/status")
async def get_status():
    """Retorna o estado atual de todas as contas do pool."""
    accounts_status = account_pool.status_report()
    healthy_count = sum(1 for a in accounts_status if a["is_healthy"])
    total_jobs_today = sum(a["jobs_today"] for a in accounts_status)

    return {
        "pool_strategy": account_pool.strategy,
        "total_accounts": len(accounts_status),
        "healthy_accounts": healthy_count,
        "total_jobs_today": total_jobs_today,
        "active_jobs": len(active_jobs),
        "accounts": accounts_status,
        "daily_stats": {
            "total_generations": total_jobs_today
        }
    }


@app.post("/dispatch", response_model=DispatchResponse)
async def dispatch_job(req: DispatchRequest):
    """
    Seleciona a melhor conta disponível e registra o job.
    O job fica em estado 'pending' até que /report_result seja chamado
    (pelo webhook do Lightning ou pela extensão Chrome via PhantomFleet).
    """
    account: Optional[LightningAccount] = await account_pool.pick(role=req.role)

    if not account:
        raise HTTPException(
            status_code=503,
            detail="Nenhuma conta Lightning disponível no momento. Tente novamente em instantes."
        )

    job_id = str(uuid.uuid4())
    started_at = time.time()

    active_jobs[job_id] = {
        "job_id": job_id,
        "account_id": account.id,
        "account_label": account.label,
        "prompt": req.prompt,
        "role": req.role,
        "priority": req.priority,
        "user_id": req.user_id,
        "status": "pending",
        "result_url": None,
        "error": None,
        "started_at": started_at,
        "metadata": req.metadata,
    }

    logger.info(
        f"[LB] ✅ Job {job_id[:8]}... despachado para [{account.id}] {account.label} "
        f"(role={req.role}, priority={req.priority})"
    )

    return DispatchResponse(
        job_id=job_id,
        account_id=account.id,
        account_label=account.label,
        status="pending",
        message=f"Job registrado. Aguardando processamento pela conta '{account.label}'.",
    )


@app.post("/report_result")
async def report_result(report: JobResultReport):
    """
    Endpoint chamado pelo webhook do Lightning AI ou extensão Chrome
    quando o resultado de um job fica pronto.
    """
    if report.job_id not in active_jobs:
        raise HTTPException(status_code=404, detail=f"Job '{report.job_id}' não encontrado ou já finalizado.")

    job = active_jobs.pop(report.job_id)

    if report.error:
        job["status"] = "error"
        job["error"] = report.error
        # Penaliza a conta que gerou o erro
        for acc in account_pool.get_all():
            if acc.id == job["account_id"]:
                acc.mark_error()
                break
        logger.error(f"[LB] ❌ Job {report.job_id[:8]}... falhou na conta [{job['account_id']}]: {report.error}")
    else:
        job["status"] = "done"
        job["result_url"] = report.result_url
        # Registra sucesso na conta
        for acc in account_pool.get_all():
            if acc.id == job["account_id"]:
                acc.mark_success()
                break
        logger.info(f"[LB] 🎉 Job {report.job_id[:8]}... concluído! URL: {report.result_url}")

    job["finished_at"] = time.time()
    job["duration_sec"] = round(job["finished_at"] - job["started_at"], 2)

    # Arquiva no histórico (mantém últimos 500)
    completed_jobs[report.job_id] = job
    if len(completed_jobs) > 500:
        oldest_key = next(iter(completed_jobs))
        del completed_jobs[oldest_key]

    return {"status": "ok", "job": job}


@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Consulta o status de um job específico (polling)."""
    if job_id in active_jobs:
        return active_jobs[job_id]
    if job_id in completed_jobs:
        return completed_jobs[job_id]
    raise HTTPException(status_code=404, detail=f"Job '{job_id}' não encontrado.")


@app.post("/mark_error")
async def mark_account_error(report: ErrorReport):
    """Marca uma conta como com erro (chamado por agentes internos)."""
    for acc in account_pool.get_all():
        if acc.id == report.account_id:
            acc.mark_error()
            return {"status": "ok", "account": acc.id, "healthy": acc.is_healthy}
    raise HTTPException(status_code=404, detail=f"Conta '{report.account_id}' não encontrada.")


@app.post("/recover/{account_id}")
async def recover_account(account_id: str):
    """Força a reativação de uma conta marcada como unhealthy (chamado pelo admin)."""
    for acc in account_pool.get_all():
        if acc.id == account_id:
            acc.is_healthy = True
            acc.consecutive_errors = 0
            logger.info(f"[LB] 🔧 Conta '{account_id}' recuperada manualmente.")
            return {"status": "ok", "message": f"Conta {account_id} reativada."}
    raise HTTPException(status_code=404, detail=f"Conta '{account_id}' não encontrada.")


# Para rodar standalone: uvicorn load_balancer:app --port 3001
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("LOAD_BALANCER_PORT", "3001")))
