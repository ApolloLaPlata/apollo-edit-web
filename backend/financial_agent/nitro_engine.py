"""
nitro_engine.py — Motor de Nitro e Cálculo de ETA
===================================================
Implementa a lógica central da monetização por velocidade de render:
  - Calcula o ETA (tempo estimado) para renderização em cada tier de GPU
  - Gera o payload de upsell para a tela de checkout do Nitro
  - Processa a compra de Nitro e despacha para o tier correto via Load Balancer

Tiers de GPU:
  FREE     → CPU compartilhada (mais lento)
  NITRO    → T4  GPU (2x mais rápido) → +X Cristais
  NITRO+   → A10 GPU (4x mais rápido) → +Y Cristais
  NITRO_M  → A100 GPU (8x mais rápido) → +Z Cristais (Master apenas)
"""

import os
import math
import logging
import httpx
import asyncio
from typing import Optional

from .coin_ledger import charge_operation, can_afford, OPERATION_COSTS

logger = logging.getLogger("NitroEngine")

LOAD_BALANCER_URL = os.getenv("LOAD_BALANCER_URL", "http://localhost:3001")

# ─────────────────────────────────────────
# DEFINIÇÃO DOS TIERS
# ─────────────────────────────────────────
GPU_TIERS = {
    "free": {
        "label":       "Grátis (CPU)",
        "speed_mult":  1.0,
        "operation":   "render_free_tier",
        "crystal_cost": 0,
        "gpu_class":   "cpu",
        "emoji":       "🐢",
    },
    "nitro": {
        "label":       "Nitro (T4 GPU)",
        "speed_mult":  2.5,
        "operation":   "render_nitro_t4",
        "crystal_cost": 50,
        "gpu_class":   "t4",
        "emoji":       "⚡",
    },
    "nitro_plus": {
        "label":       "Nitro+ (A10 GPU)",
        "speed_mult":  4.5,
        "operation":   "render_nitro_t4",    # mesmo custo de moedas
        "crystal_cost": 120,
        "gpu_class":   "a10",
        "emoji":       "🚀",
    },
    "nitro_master": {
        "label":       "Nitro Master (A100)",
        "speed_mult":  8.0,
        "operation":   "render_nitro_master_a100",
        "crystal_cost": 280,
        "gpu_class":   "a100",
        "emoji":       "☄️",
        "plan_required": "master",   # Apenas plano Master pode usar
    },
}


# ─────────────────────────────────────────
# ESTIMATIVA DE TEMPO (ETA)
# ─────────────────────────────────────────
def estimate_render_time(
    duration_seconds: float,
    has_ai_effects: bool = False,
    has_image_gen: bool = False,
    resolution: str = "1080p",
) -> dict:
    """
    Estima o tempo base de render (em segundos) para cada tier de GPU.
    
    Fatores:
      - Duração do vídeo
      - Resolução (720p / 1080p / 4K)
      - Efeitos de IA (aumenta o tempo)
      - Geração de imagem/vídeo incluso
    """
    # Tempo base: ~3 segundos de processamento por segundo de vídeo (CPU)
    resolution_multiplier = {"720p": 1.0, "1080p": 1.8, "4K": 4.5}.get(resolution, 1.8)
    ai_multiplier = 1.5 if has_ai_effects else 1.0
    image_gen_overhead = 45 if has_image_gen else 0  # +45s para geração de imagem

    base_time_sec = (duration_seconds * 3.0 * resolution_multiplier * ai_multiplier) + image_gen_overhead

    tiers_eta = {}
    for tier_id, tier in GPU_TIERS.items():
        eta_sec = math.ceil(base_time_sec / tier["speed_mult"])
        eta_min = eta_sec / 60
        tiers_eta[tier_id] = {
            **tier,
            "eta_seconds": eta_sec,
            "eta_display": _format_time(eta_sec),
        }

    return {
        "base_time_seconds": int(base_time_sec),
        "input": {
            "duration_seconds": duration_seconds,
            "resolution": resolution,
            "has_ai_effects": has_ai_effects,
            "has_image_gen": has_image_gen,
        },
        "tiers": tiers_eta,
    }


def _format_time(seconds: int) -> str:
    """Formata segundos como '2min 30s' ou '1h 15min'."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        m = seconds // 60
        s = seconds % 60
        return f"{m}min {s}s" if s > 0 else f"{m}min"
    else:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h}h {m}min"


# ─────────────────────────────────────────
# GERAÇÃO DO PAYLOAD DE UPSELL (Tela de Checkout)
# ─────────────────────────────────────────
def build_nitro_checkout(
    user_id: str,
    user_plan: str,
    duration_seconds: float,
    has_ai_effects: bool = False,
    has_image_gen: bool = False,
    resolution: str = "1080p",
) -> dict:
    """
    Monta o payload completo para a tela de checkout do Nitro.
    Inclui ETA de cada tier, custo e disponibilidade por plano.
    """
    eta_data = estimate_render_time(duration_seconds, has_ai_effects, has_image_gen, resolution)
    
    checkout_tiers = []
    for tier_id, tier_info in eta_data["tiers"].items():
        plan_required = tier_info.get("plan_required")
        available = (plan_required is None) or (user_plan == plan_required) or (user_plan == "master")
        
        checkout_tiers.append({
            "tier_id": tier_id,
            "label": tier_info["label"],
            "emoji": tier_info["emoji"],
            "eta_display": tier_info["eta_display"],
            "eta_seconds": tier_info["eta_seconds"],
            "crystal_cost": tier_info["crystal_cost"],
            "available": available,
            "locked_reason": f"Requer Plano Master" if not available else None,
            "is_recommended": tier_id == "nitro",
        })

    return {
        "user_id": user_id,
        "user_plan": user_plan,
        "project_summary": eta_data["input"],
        "base_time_display": _format_time(eta_data["base_time_seconds"]),
        "tiers": checkout_tiers,
        "message": "Escolha a velocidade de renderização. O Nitro usa nossas GPUs dedicadas para entregar seu vídeo mais rápido.",
    }


# ─────────────────────────────────────────
# PROCESSAMENTO DA COMPRA E DESPACHO DO JOB
# ─────────────────────────────────────────
async def purchase_and_dispatch(
    user_id: str,
    tier_id: str,
    prompt: str,
    metadata: Optional[dict] = None,
) -> dict:
    """
    1. Verifica se o usuário pode pagar pelo tier escolhido.
    2. Cobra as moedas.
    3. Despacha o job para o Load Balancer no tier correto.
    4. Retorna o job_id para polling.
    """
    tier = GPU_TIERS.get(tier_id)
    if not tier:
        return {"success": False, "error": f"Tier '{tier_id}' não existe."}

    # Verifica saldo de moedas
    operation = tier["operation"]
    affordable, details = can_afford(user_id, operation)
    if not affordable:
        return {
            "success": False,
            "error": "Saldo insuficiente.",
            "shortfalls": details.get("shortfalls", {}),
            "tip": "Compre mais Apollo Coins ou faça upgrade do seu plano.",
        }

    # Cobra as moedas do usuário
    charge_result = charge_operation(user_id, operation, metadata={"tier": tier_id})
    if not charge_result["success"]:
        return {"success": False, "error": "Falha ao processar o pagamento."}

    # Despacha para o Load Balancer
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(
                f"{LOAD_BALANCER_URL}/dispatch",
                json={
                    "prompt": prompt,
                    "role": "video" if "video" in tier_id else "general",
                    "priority": tier_id,
                    "user_id": user_id,
                    "metadata": {**(metadata or {}), "tier": tier_id, "gpu_class": tier["gpu_class"]},
                },
            )
            dispatch_data = r.json()

    except Exception as e:
        logger.error(f"[Nitro] Falha ao contatar Load Balancer: {e}")
        # Reembolsa o usuário se o dispatch falhar
        from .coin_ledger import credit_user
        cost = OPERATION_COSTS.get(operation, {})
        for currency, amount in cost.items():
            credit_user(user_id, currency, amount, reason="refund_dispatch_failure")
        return {"success": False, "error": "Falha ao despachar o job. Reembolso processado."}

    logger.info(f"[Nitro] ✅ Job despachado! user={user_id}, tier={tier_id}, job_id={dispatch_data.get('job_id', 'N/A')}")
    
    return {
        "success": True,
        "tier": tier_id,
        "tier_label": tier["label"],
        "job_id": dispatch_data.get("job_id"),
        "account_label": dispatch_data.get("account_label"),
        "wallet": charge_result["wallet"],
        "message": f"Renderização iniciada com {tier['label']}! Acompanhe pelo job_id.",
    }
