"""
Apollo Financial Agent v1.0
Agente de análise de custos e gestão financeira do sistema Lightning AI.

Roda como um cron job diário (ou pode ser chamado via API pelo painel Admin).
Funções:
  1. Monitora saldo de crédito de cada conta Lightning.
  2. Projeta esgotamento baseado no consumo médio diário.
  3. Gera recomendações de ajuste de cotas gratuitas.
  4. Envia alertas ao admin quando crédito está baixo.
  5. Registra histórico financeiro no Supabase.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional
import httpx
import asyncio

# ─────────────────────────────────────────
# CONFIGURAÇÕES DO AGENTE
# ─────────────────────────────────────────
LOAD_BALANCER_URL = os.getenv("LOAD_BALANCER_URL", "http://localhost:3001")
ADMIN_WEBHOOK_URL = os.getenv("ADMIN_WEBHOOK_URL", "")  # Ex: Discord Webhook ou WhatsApp API

# Limites de alerta (% do orçamento)
ALERT_THRESHOLD_WARNING  = 25.0   # Alerta amarelo quando < 25% restante
ALERT_THRESHOLD_CRITICAL = 10.0   # Alerta vermelho quando < 10% restante
ALERT_THRESHOLD_ZERO     = 3.0    # Emergência quando < 3% restante

# ─────────────────────────────────────────
# BANCO DE DADOS FINANCEIRO (Arquivo local / Supabase futuramente)
# ─────────────────────────────────────────
FINANCE_DB_FILE = "finance_history.json"

def load_finance_history() -> dict:
    if os.path.exists(FINANCE_DB_FILE):
        with open(FINANCE_DB_FILE, "r") as f:
            return json.load(f)
    return {"daily_records": [], "monthly_summary": {}}

def save_finance_history(data: dict):
    with open(FINANCE_DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─────────────────────────────────────────
# ANÁLISE DE CUSTOS
# ─────────────────────────────────────────
async def fetch_account_status() -> dict:
    """Busca o status atual de todas as contas do Load Balancer."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{LOAD_BALANCER_URL}/status")
            return r.json()
    except Exception as e:
        print(f"[FinAgent] ❌ Não conseguiu conectar ao Load Balancer: {e}")
        return {"accounts": [], "daily_stats": {}}

def project_days_remaining(credit_remaining: float, credit_used: float, days_elapsed: int) -> int:
    """
    Projeta quantos dias o crédito restante vai durar
    baseado na taxa de consumo diária atual.
    """
    if days_elapsed == 0 or credit_used == 0:
        return 999  # Sem dados suficientes, assume o mês inteiro
    
    daily_burn_rate = credit_used / days_elapsed
    if daily_burn_rate <= 0:
        return 999
    
    return int(credit_remaining / daily_burn_rate)

def recommend_daily_quota(account: dict, days_in_month: int = 30) -> dict:
    """
    Recomenda quantas gerações gratuitas oferecer por dia
    para que o crédito dure até o fim do mês.
    """
    remaining_usd = account["credit_remaining_usd"]
    days_left = max(1, days_in_month - datetime.now().day)
    
    # Custo médio por geração (Flux = $0.004, Vídeo = $0.009)
    avg_cost = 0.004 if account["role"] == "image" else 0.009
    
    safe_daily_budget  = remaining_usd / days_left
    recommended_gens   = int(safe_daily_budget / avg_cost)
    
    return {
        "days_left_in_month": days_left,
        "safe_daily_budget_usd": round(safe_daily_budget, 3),
        "recommended_free_generations": max(0, recommended_gens),
        "avg_cost_per_gen_usd": avg_cost
    }

# ─────────────────────────────────────────
# GERADOR DE RELATÓRIO
# ─────────────────────────────────────────
def generate_daily_report(status_data: dict) -> dict:
    """Gera o relatório financeiro diário completo."""
    accounts  = status_data.get("accounts", [])
    today     = datetime.now()
    day_of_month = today.day
    
    # Calcular totais
    total_budget   = sum(a["budget_usd"] for a in accounts)
    total_used     = sum(a["credit_used_usd"] for a in accounts)
    total_remaining = sum(a["credit_remaining_usd"] for a in accounts)
    total_gens_today = status_data.get("daily_stats", {}).get("total_generations", 0)
    
    # Projeções
    days_elapsed = max(1, day_of_month)
    daily_burn   = total_used / days_elapsed
    projected_eol = datetime.now() + timedelta(days=(total_remaining / daily_burn) if daily_burn > 0 else 30)
    
    # Alertas por conta
    alerts = []
    for acc in accounts:
        pct = acc.get("credit_pct", 100)
        if pct < ALERT_THRESHOLD_ZERO:
            alerts.append({"level": "EMERGENCY", "account": acc["label"], "pct": pct, "action": "Recarregar AGORA"})
        elif pct < ALERT_THRESHOLD_CRITICAL:
            alerts.append({"level": "CRITICAL", "account": acc["label"], "pct": pct, "action": "Recarregar em até 24h"})
        elif pct < ALERT_THRESHOLD_WARNING:
            alerts.append({"level": "WARNING", "account": acc["label"], "pct": pct, "action": "Reduzir cota gratuita"})
    
    # Recomendações por conta
    recommendations = {acc["id"]: recommend_daily_quota(acc) for acc in accounts}
    
    report = {
        "timestamp": today.isoformat(),
        "day_of_month": day_of_month,
        "financial_summary": {
            "total_budget_usd": total_budget,
            "total_used_usd": round(total_used, 3),
            "total_remaining_usd": round(total_remaining, 3),
            "total_remaining_pct": round((total_remaining / total_budget) * 100, 1),
            "daily_burn_rate_usd": round(daily_burn, 4),
            "projected_exhaustion_date": projected_eol.strftime("%d/%m/%Y"),
            "total_generations_today": total_gens_today,
        },
        "accounts": accounts,
        "alerts": alerts,
        "recommendations": recommendations,
        "capital_de_giro": {
            # Esta seção será preenchida com dados reais do Supabase
            "entrada_cristais_vendidos_usd": 0.00,
            "saida_lightning_usd": round(total_used, 3),
            "saida_supabase_usd": 0.00,        # Custo estimado Supabase
            "saida_outros_usd": 0.00,
            "saldo_liquido_usd": 0.00,
            "nota": "Integre com Stripe/Mercado Pago para preencher 'entrada'."
        }
    }
    
    return report

# ─────────────────────────────────────────
# ALERTAS
# ─────────────────────────────────────────
async def send_alert(report: dict):
    """Envia alertas ao admin via webhook (Discord/WhatsApp/Email)."""
    if not ADMIN_WEBHOOK_URL or not report["alerts"]:
        return
    
    alert_text = f"⚠️ **Apollo Financial Alert** — {report['timestamp'][:10]}\n"
    for alert in report["alerts"]:
        emoji = "🚨" if alert["level"] in ["EMERGENCY", "CRITICAL"] else "⚠️"
        alert_text += f"{emoji} [{alert['level']}] {alert['account']}: {alert['pct']}% restante — {alert['action']}\n"
    
    alert_text += f"\n💰 Saldo Total: ${report['financial_summary']['total_remaining_usd']:.2f} / ${report['financial_summary']['total_budget_usd']:.2f}"
    
    try:
        async with httpx.AsyncClient() as client:
            await client.post(ADMIN_WEBHOOK_URL, json={"content": alert_text})
            print(f"[FinAgent] 📢 Alerta enviado ao Admin.")
    except Exception as e:
        print(f"[FinAgent] ⚠️ Falha ao enviar alerta: {e}")

# ─────────────────────────────────────────
# EXECUÇÃO PRINCIPAL (Cron Job)
# ─────────────────────────────────────────
async def run_daily_analysis():
    """
    Função principal do Agente Financeiro.
    Chamada diariamente pelo cron job ou pelo painel Admin.
    """
    print(f"\n[FinAgent] ═══════════════════════════════════")
    print(f"[FinAgent] 🤖 Análise Financeira Diária — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"[FinAgent] ═══════════════════════════════════")
    
    # 1. Busca dados das contas
    status_data = await fetch_account_status()
    
    if not status_data["accounts"]:
        print("[FinAgent] ❌ Sem dados das contas. Abortando análise.")
        return
    
    # 2. Gera relatório
    report = generate_daily_report(status_data)
    
    # 3. Imprime resumo
    fs = report["financial_summary"]
    print(f"[FinAgent] 💰 Saldo Total: ${fs['total_remaining_usd']:.2f} / ${fs['total_budget_usd']:.2f} ({fs['total_remaining_pct']}%)")
    print(f"[FinAgent] 🔥 Taxa de queima: ${fs['daily_burn_rate_usd']:.4f}/dia")
    print(f"[FinAgent] 📅 Previsão de esgotamento: {fs['projected_exhaustion_date']}")
    print(f"[FinAgent] 🎮 Gerações hoje: {fs['total_generations_today']}")
    
    # 4. Alertas
    if report["alerts"]:
        print(f"\n[FinAgent] ⚠️ {len(report['alerts'])} ALERTAS:")
        for alert in report["alerts"]:
            print(f"  [{alert['level']}] {alert['account']}: {alert['pct']}% — {alert['action']}")
    else:
        print("[FinAgent] ✅ Todas as contas saudáveis. Sem alertas.")
    
    # 5. Recomendações
    print(f"\n[FinAgent] 📊 Recomendações de Cota Gratuita:")
    for acc_id, rec in report["recommendations"].items():
        print(f"  {acc_id}: {rec['recommended_free_generations']} gerações/dia ({rec['days_left_in_month']} dias restantes no mês)")
    
    # 6. Salva histórico
    history = load_finance_history()
    history["daily_records"].append(report)
    if len(history["daily_records"]) > 90:  # Mantém apenas 90 dias
        history["daily_records"] = history["daily_records"][-90:]
    save_finance_history(history)
    
    # 7. Envia alertas se necessário
    await send_alert(report)
    
    print(f"\n[FinAgent] ✅ Análise salva em {FINANCE_DB_FILE}")
    return report

# Para executar manualmente:
# python main.py
if __name__ == "__main__":
    asyncio.run(run_daily_analysis())
