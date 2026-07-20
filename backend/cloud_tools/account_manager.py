import os
import json
import subprocess
import uuid

DB_FILE = os.path.join(os.path.dirname(__file__), "cloud_accounts_db.json")

def load_accounts():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_accounts(accounts):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4)

def add_account(provider, name, workspace, token_id, token_secret):
    accounts = load_accounts()
    new_acc = {
        "id": uuid.uuid4().hex[:8],
        "provider": provider,
        "name": name,
        "workspace": workspace,
        "token_id": token_id,
        "token_secret": token_secret,
        "is_active": True,
        "last_balance": 30.0,
        "last_spend": 0.0
    }
    accounts.append(new_acc)
    save_accounts(accounts)
    return new_acc

def delete_account(acc_id):
    accounts = load_accounts()
    accounts = [a for a in accounts if a["id"] != acc_id]
    save_accounts(accounts)

def toggle_active(acc_id, provider):
    """Ativa uma conta e opcionalmente desativa outras do mesmo provedor"""
    accounts = load_accounts()
    for acc in accounts:
        if acc["id"] == acc_id:
            acc["is_active"] = True
        elif acc["provider"] == provider:
            acc["is_active"] = False
    save_accounts(accounts)

def get_modal_balance(token_id, token_secret):
    """
    Roda `modal billing report` usando variáveis de ambiente específicas.
    """
    env = os.environ.copy()
    env["MODAL_TOKEN_ID"] = token_id
    env["MODAL_TOKEN_SECRET"] = token_secret
    
    try:
        # Usando check=False para tratar erros suavemente sem quebrar o backend
        result = subprocess.run(
            ["modal", "billing", "report", "--for", "this month", "--json"],
            env=env,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return 0.0, 30.0 # Conta talvez nova ou comando falhou
            
        data = json.loads(result.stdout)
        total_cost = sum(float(item.get("cost", 0)) for item in data)
        free_tier = 30.0
        remaining = max(0.0, free_tier - total_cost)
        return total_cost, remaining
    except Exception as e:
        print(f"Erro consultando saldo modal: {e}")
        return 0.0, 30.0

def update_balances():
    """Percorre as contas Modal e atualiza o saldo real delas."""
    accounts = load_accounts()
    changed = False
    for acc in accounts:
        if acc["provider"] == "modal":
            spent, remaining = get_modal_balance(acc["token_id"], acc["token_secret"])
            if acc.get("last_spend") != spent or acc.get("last_balance") != remaining:
                acc["last_spend"] = spent
                acc["last_balance"] = remaining
                changed = True
    if changed:
        save_accounts(accounts)
    return accounts
def mark_exhausted(workspace):
    """Zera o saldo de uma conta que foi rejeitada por falta de pagamento (402/403)"""
    accounts = load_accounts()
    changed = False
    for acc in accounts:
        if acc.get("workspace") == workspace and acc.get("last_balance", 0.0) > 0.0:
            acc["last_balance"] = 0.0
            changed = True
    if changed:
        save_accounts(accounts)

def deduct_balance(acc_id, amount):
    """Deduz um valor do saldo de uma conta específica."""
    accounts = load_accounts()
    changed = False
    for acc in accounts:
        if acc["id"] == acc_id:
            current_balance = float(acc.get("last_balance", 0.0))
            current_spend = float(acc.get("last_spend", 0.0))
            if current_balance > 0:
                acc["last_balance"] = max(0.0, current_balance - amount)
                acc["last_spend"] = current_spend + amount
                changed = True
                break
    if changed:
        save_accounts(accounts)

class AccountManager:
    def __init__(self):
        pass
        
    def get_all_accounts(self):
        return load_accounts()
        
    def add_account(self, provider, name, workspace, token_id, token_secret):
        return add_account(provider, name, workspace, token_id, token_secret)

def get_active_account(needs_lightning=False):
    accounts = load_accounts()
    
    provider_req = "lightning" if needs_lightning else "modal"
    
    # Try to find an active account with balance
    valid = [a for a in accounts if a.get("provider") == provider_req and a.get("last_balance", 0.0) > 0.0]
    if valid:
        import random
        acc = random.choice(valid)
        acc["modal_url"] = f"https://{acc['workspace']}--apollo-render-router-api-generate-audio.modal.run" if not needs_lightning else ""
        return acc
        
    return {"workspace": "demo-workspace", "modal_url": "https://demo-workspace--apollo-render-router-api-generate-audio.modal.run"}
