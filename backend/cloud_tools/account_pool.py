"""
account_pool.py — Pool de Contas Lightning AI / Modal
======================================================
Gerencia um conjunto de N contas com suas respectivas API Keys.
Estratégia: Round-Robin com Health Check + Prioridade por crédito restante.

Como adicionar contas no .env:
  LIGHTNING_ACCOUNT_1=nome_conta|user_id|api_key|teamspace
  LIGHTNING_ACCOUNT_2=nome_conta|user_id|api_key|teamspace
  ...
"""

import os
import time
import logging
import asyncio
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("AccountPool")

# ─────────────────────────────────────────
# MODELO DE CONTA
# ─────────────────────────────────────────
@dataclass
class LightningAccount:
    id: str                        # Ex: "conta_1", "conta_2"
    label: str                     # Nome legível (ex: "RecargaPay_Minha")
    user_id: str
    api_key: str
    teamspace: str
    studio_name: str               # Nome do estúdio Lightning a acordar
    role: str = "general"          # "image", "video", "general"
    
    # Runtime stats (não persistidos em .env)
    is_healthy: bool = True
    jobs_today: int = 0
    last_job_at: float = 0.0
    credit_remaining_pct: float = 100.0  # Atualizado pelo FinancialAgent
    consecutive_errors: int = 0

    def reset_daily_stats(self):
        self.jobs_today = 0

    def mark_error(self):
        self.consecutive_errors += 1
        if self.consecutive_errors >= 3:
            self.is_healthy = False
            logger.warning(f"[Pool] ⚠️ Conta '{self.label}' marcada como UNHEALTHY após 3 erros.")

    def mark_success(self):
        self.consecutive_errors = 0
        self.is_healthy = True
        self.jobs_today += 1
        self.last_job_at = time.time()


# ─────────────────────────────────────────
# CARREGADOR DE CONTAS DO .ENV
# ─────────────────────────────────────────
def load_accounts_from_env() -> list[LightningAccount]:
    """
    Lê as contas do .env no formato:
      LIGHTNING_ACCOUNT_1=label|user_id|api_key|teamspace|studio_name|role
    """
    accounts = []
    i = 1
    while True:
        raw = os.getenv(f"LIGHTNING_ACCOUNT_{i}")
        if not raw:
            break
        
        try:
            parts = [p.strip() for p in raw.split("|")]
            if len(parts) < 5:
                logger.error(f"[Pool] ❌ LIGHTNING_ACCOUNT_{i} mal formatado. Esperado: label|user_id|api_key|teamspace|studio_name|role(opcional)")
                i += 1
                continue

            acc = LightningAccount(
                id=f"conta_{i}",
                label=parts[0],
                user_id=parts[1],
                api_key=parts[2],
                teamspace=parts[3],
                studio_name=parts[4],
                role=parts[5] if len(parts) > 5 else "general",
            )
            accounts.append(acc)
            logger.info(f"[Pool] ✅ Conta carregada: [{acc.id}] {acc.label} ({acc.role})")
        except Exception as e:
            logger.error(f"[Pool] ❌ Erro ao parsear LIGHTNING_ACCOUNT_{i}: {e}")
        
        i += 1

    # Fallback: usa a conta legada do .env se não houver contas numeradas
    if not accounts:
        legacy_key = os.getenv("LIGHTNING_API_KEY", "")
        legacy_uid = os.getenv("LIGHTNING_USER_ID", "")
        legacy_ts = os.getenv("LIGHTNING_TEAMSPACE", "v5est")
        legacy_studio = os.getenv("FFMPEG_STUDIO_NAME", "CPU FREE")

        if legacy_key:
            fallback = LightningAccount(
                id="conta_legada",
                label="Conta Principal (Legada)",
                user_id=legacy_uid,
                api_key=legacy_key,
                teamspace=legacy_ts,
                studio_name=legacy_studio,
                role="general",
            )
            accounts.append(fallback)
            logger.info(f"[Pool] ⚡ Usando conta legada do .env como fallback.")

    return accounts


# ─────────────────────────────────────────
# GERENCIADOR DO POOL
# ─────────────────────────────────────────
class AccountPool:
    """
    Pool de contas com seleção inteligente.
    Estratégias de seleção disponíveis:
      - 'round_robin': Alterna entre contas em ordem
      - 'least_used': Prioriza conta com menos jobs hoje
      - 'most_credit': Prioriza conta com mais crédito restante
    """

    def __init__(self, strategy: str = "least_used"):
        self.accounts: list[LightningAccount] = load_accounts_from_env()
        self.strategy = strategy
        self._rr_index = 0  # Índice para round-robin
        self._lock = asyncio.Lock()
        logger.info(f"[Pool] 🚀 Pool inicializado com {len(self.accounts)} conta(s). Estratégia: {strategy}")

    def get_all(self) -> list[LightningAccount]:
        return self.accounts

    def get_healthy(self) -> list[LightningAccount]:
        return [a for a in self.accounts if a.is_healthy]

    async def pick(self, role: Optional[str] = None) -> Optional[LightningAccount]:
        """
        Seleciona a melhor conta disponível de acordo com a estratégia.
        Se `role` for informado, filtra por contas com aquele papel.
        """
        async with self._lock:
            candidates = self.get_healthy()
            
            if role and role != "general":
                # Tenta pegar conta especializada, senão usa geral
                specialized = [a for a in candidates if a.role == role]
                if specialized:
                    candidates = specialized

            if not candidates:
                logger.error("[Pool] ❌ Nenhuma conta saudável disponível!")
                return None

            if self.strategy == "round_robin":
                account = candidates[self._rr_index % len(candidates)]
                self._rr_index += 1

            elif self.strategy == "least_used":
                account = min(candidates, key=lambda a: a.jobs_today)

            elif self.strategy == "most_credit":
                account = max(candidates, key=lambda a: a.credit_remaining_pct)

            else:
                account = candidates[0]

            logger.info(f"[Pool] 🎯 Conta selecionada: [{account.id}] {account.label} (jobs_hoje={account.jobs_today})")
            return account

    def update_credit(self, account_id: str, credit_pct: float):
        """Atualiza o % de crédito restante de uma conta (chamado pelo FinancialAgent)."""
        for acc in self.accounts:
            if acc.id == account_id:
                acc.credit_remaining_pct = credit_pct
                break

    def report_success(self, account_id: str):
        """Reporta sucesso para a conta (zera erros e aumenta contador de uso)"""
        for acc in self.accounts:
            if acc.id == account_id:
                acc.mark_success()
                break

    def report_error(self, account_id: str):
        """Reporta falha na conta (incrementa erros e possivelmente a inativa)"""
        for acc in self.accounts:
            if acc.id == account_id:
                acc.mark_error()
                break

    def status_report(self) -> list[dict]:
        """Retorna o status de todas as contas para o endpoint /status."""
        return [
            {
                "id": a.id,
                "label": a.label,
                "role": a.role,
                "is_healthy": a.is_healthy,
                "jobs_today": a.jobs_today,
                "credit_remaining_pct": a.credit_remaining_pct,
                "last_job_at": a.last_job_at,
                "consecutive_errors": a.consecutive_errors,
            }
            for a in self.accounts
        ]


# Singleton global do Pool
account_pool = AccountPool(strategy=os.getenv("POOL_STRATEGY", "least_used"))
