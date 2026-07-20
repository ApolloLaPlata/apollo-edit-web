"""
subscription_manager.py — Gerenciador de Assinaturas Apollo
============================================================
Gerencia os planos Free / Pro / Master:
  - Ativação e renovação de planos
  - Controle de cotas (canais, renders paralelos)
  - Integração com o CoinLedger para concessão mensal de moedas
  - Webhooks de pagamento (Stripe / Mercado Pago — futuramente)
"""

import sqlite3
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from .coin_ledger import grant_monthly_plan, get_wallet, PLAN_MONTHLY_GRANTS

logger = logging.getLogger("SubscriptionManager")

DB_PATH = os.path.join(os.path.dirname(__file__), "economy.db")

# ─────────────────────────────────────────
# PREÇOS DOS PLANOS (em R$)
# ─────────────────────────────────────────
PLAN_PRICES_BRL = {
    "free":   0.00,
    "pro":    49.90,
    "master": 99.90,
}

PLAN_LABELS = {
    "free":   "🆓 Free",
    "pro":    "⚡ Pro",
    "master": "👑 Master",
}


# ─────────────────────────────────────────
# INICIALIZAÇÃO
# ─────────────────────────────────────────
def init_subscription_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabela de assinaturas
    c.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            plan TEXT NOT NULL DEFAULT 'free',
            started_at TEXT,
            expires_at TEXT,
            renewal_day INTEGER DEFAULT 1,
            payment_method TEXT,
            payment_ref TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Tabela de limites de uso
    c.execute("""
        CREATE TABLE IF NOT EXISTS usage_limits (
            user_id TEXT PRIMARY KEY,
            plan TEXT DEFAULT 'free',
            channels_used INTEGER DEFAULT 0,
            max_channels INTEGER DEFAULT 1,
            parallel_renders_used INTEGER DEFAULT 0,
            max_parallel_renders INTEGER DEFAULT 1,
            last_reset_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    logger.info("[SubManager] ✅ Tabelas de assinatura inicializadas.")


# ─────────────────────────────────────────
# OPERAÇÕES DE PLANO
# ─────────────────────────────────────────
def activate_plan(user_id: str, plan: str, payment_ref: Optional[str] = None) -> dict:
    """
    Ativa ou faz upgrade de plano para um usuário.
    Concede as moedas mensais imediatamente na ativação.
    """
    if plan not in PLAN_MONTHLY_GRANTS:
        return {"success": False, "error": f"Plano '{plan}' não existe."}

    now = datetime.utcnow()
    expires = now + timedelta(days=30)
    grants = PLAN_MONTHLY_GRANTS[plan]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Atualiza o plano na tabela users
    c.execute(
        "INSERT OR IGNORE INTO users (user_id, coins, chips_llm, gpu_tokens, fuel, crystals, plan) "
        "VALUES (?, 0, 0, 0, 0, 0, 'free')",
        (user_id,)
    )
    c.execute(
        "UPDATE users SET plan = ?, plan_expires_at = ? WHERE user_id = ?",
        (plan, expires.isoformat(), user_id)
    )

    # Registra a assinatura
    c.execute(
        "INSERT INTO subscriptions (user_id, plan, started_at, expires_at, payment_ref) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, plan, now.isoformat(), expires.isoformat(), payment_ref or "")
    )

    # Atualiza os limites de uso
    c.execute("""
        INSERT INTO usage_limits (user_id, plan, max_channels, max_parallel_renders)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            plan = excluded.plan,
            max_channels = excluded.max_channels,
            max_parallel_renders = excluded.max_parallel_renders
    """, (user_id, plan, grants["max_channels"], grants["parallel_renders"]))

    conn.commit()
    conn.close()

    # Concede as moedas mensais
    grant_monthly_plan(user_id, plan)

    logger.info(f"[SubManager] 🎉 Plano '{plan}' ativado para {user_id}. Expira: {expires.date()}")
    return {
        "success": True,
        "user_id": user_id,
        "plan": plan,
        "plan_label": PLAN_LABELS[plan],
        "expires_at": expires.isoformat(),
        "grants": grants,
        "wallet": get_wallet(user_id),
    }


def get_plan_info(user_id: str) -> dict:
    """Retorna as informações de plano e limites do usuário."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "SELECT plan, plan_expires_at FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = c.fetchone()

    if not row:
        conn.close()
        return {"plan": "free", "plan_label": PLAN_LABELS["free"], "is_active": False}

    plan, expires_at = row[0] or "free", row[1]

    # Verifica se o plano expirou
    is_active = True
    if expires_at and plan != "free":
        try:
            exp_dt = datetime.fromisoformat(expires_at)
            if datetime.utcnow() > exp_dt:
                is_active = False
                plan = "free"  # Downgrade automático
        except Exception:
            pass

    # Busca limites de uso
    c.execute(
        "SELECT channels_used, max_channels, parallel_renders_used, max_parallel_renders "
        "FROM usage_limits WHERE user_id = ?",
        (user_id,)
    )
    limits_row = c.fetchone()
    conn.close()

    limits = {}
    if limits_row:
        limits = {
            "channels_used": limits_row[0],
            "max_channels": limits_row[1],
            "parallel_renders_used": limits_row[2],
            "max_parallel_renders": limits_row[3],
        }
    else:
        # Defaults do plano free
        g = PLAN_MONTHLY_GRANTS["free"]
        limits = {
            "channels_used": 0,
            "max_channels": g["max_channels"],
            "parallel_renders_used": 0,
            "max_parallel_renders": g["parallel_renders"],
        }

    return {
        "user_id": user_id,
        "plan": plan,
        "plan_label": PLAN_LABELS.get(plan, plan),
        "is_active": is_active,
        "expires_at": expires_at,
        "limits": limits,
        "price_brl": PLAN_PRICES_BRL.get(plan, 0),
        "available_upgrades": [
            p for p in ["pro", "master"]
            if PLAN_PRICES_BRL[p] > PLAN_PRICES_BRL.get(plan, 0)
        ],
    }


def check_channel_limit(user_id: str) -> dict:
    """Verifica se o usuário pode criar mais canais."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT channels_used, max_channels FROM usage_limits WHERE user_id = ?",
        (user_id,)
    )
    row = c.fetchone()
    conn.close()

    if not row:
        return {"can_add": True, "used": 0, "max": 1}

    used, max_ch = row
    return {
        "can_add": used < max_ch,
        "used": used,
        "max": max_ch,
        "message": f"Você já tem {used}/{max_ch} canais. Faça upgrade para adicionar mais." if used >= max_ch else None,
    }


def increment_channel_count(user_id: str):
    """Incrementa o contador de canais ao criar um novo."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE usage_limits SET channels_used = channels_used + 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()


def get_all_plans_comparison() -> dict:
    """Retorna a tabela comparativa de todos os planos para exibição na UI."""
    return {
        "plans": [
            {
                "id": plan_id,
                "label": PLAN_LABELS[plan_id],
                "price_brl": PLAN_PRICES_BRL[plan_id],
                "price_display": "Grátis" if plan_id == "free" else f"R$ {PLAN_PRICES_BRL[plan_id]:.2f}/mês",
                "grants": PLAN_MONTHLY_GRANTS[plan_id],
            }
            for plan_id in ["free", "pro", "master"]
        ]
    }


# Inicializa ao importar
init_subscription_tables()
