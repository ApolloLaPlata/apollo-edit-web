from fastapi import APIRouter
import subprocess, os, json, concurrent.futures

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

@router.get("/hive-status")
def get_hive_status():
    """
    Endpoint acessado pela Área Administrativa do Frontend.
    Chama o Maestro, que por sua vez lê o JSON do Cérbero, Zelador e Watchdog,
    e retorna tudo consolidado para a interface.
    """
    from backend.main import maestro
    return maestro.get_hive_status()


def _check_modal_balance(acc: dict) -> dict:
    """Verifica o saldo real de uma conta Modal via CLI."""
    env = os.environ.copy()
    env["MODAL_TOKEN_ID"] = acc.get("token_id", "")
    env["MODAL_TOKEN_SECRET"] = acc.get("token_secret", "")
    try:
        r = subprocess.run(
            ["modal", "billing", "report", "--for", "this month", "--json"],
            env=env, capture_output=True, text=True, timeout=25
        )
        if r.returncode == 0 and r.stdout.strip():
            data = json.loads(r.stdout)
            spent = round(sum(float(item.get("cost", 0)) for item in data), 4)
            remaining = round(max(0.0, 30.0 - spent), 4)
            return {
                "id": acc["id"],
                "name": acc["name"],
                "workspace": acc["workspace"],
                "provider": acc["provider"],
                "spent": spent,
                "remaining": remaining,
                "budget": 30.0,
                "percent_used": round((spent / 30.0) * 100, 1),
                "status": "ok" if remaining > 2.0 else ("low" if remaining > 0.5 else "exhausted"),
            }
        else:
            return {
                "id": acc["id"], "name": acc["name"], "workspace": acc["workspace"],
                "provider": acc["provider"], "spent": None, "remaining": None,
                "budget": 30.0, "percent_used": None, "status": "error",
                "error": r.stderr.strip()[:200]
            }
    except Exception as e:
        return {
            "id": acc["id"], "name": acc["name"], "workspace": acc["workspace"],
            "provider": acc["provider"], "spent": None, "remaining": None,
            "budget": 30.0, "percent_used": None, "status": "error", "error": str(e)
        }


@router.get("/fleet-balance")
def get_fleet_balance():
    """
    Verifica o saldo de TODAS as contas do fleet em paralelo.
    Retorna o status completo de cada conta Modal + resumo do pool.
    """
    from backend.cloud_tools.account_manager import load_accounts
    accounts = load_accounts()

    modal_accounts = [a for a in accounts if a.get("provider") == "modal"]
    lightning_accounts = [a for a in accounts if a.get("provider") == "lightning"]

    # Checa todas as contas Modal em paralelo para ser rápido
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_check_modal_balance, acc): acc for acc in modal_accounts}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    # Ordena pelo nome para exibição consistente
    results.sort(key=lambda x: x["name"])

    # Calcula resumo do pool
    ok_accounts = [r for r in results if r["status"] == "ok"]
    low_accounts = [r for r in results if r["status"] == "low"]
    exhausted_accounts = [r for r in results if r["status"] == "exhausted"]
    total_remaining = sum(r["remaining"] for r in results if r["remaining"] is not None)
    total_spent = sum(r["spent"] for r in results if r["spent"] is not None)

    return {
        "fleet": results,
        "lightning": [{"name": a["name"], "workspace": a["workspace"]} for a in lightning_accounts],
        "summary": {
            "total_accounts": len(modal_accounts),
            "ok": len(ok_accounts),
            "low": len(low_accounts),
            "exhausted": len(exhausted_accounts),
            "total_remaining_usd": round(total_remaining, 2),
            "total_spent_usd": round(total_spent, 2),
            "total_budget_usd": round(30.0 * len(modal_accounts), 2),
            "active_for_routing": len(ok_accounts) + len(low_accounts),
        }
    }

