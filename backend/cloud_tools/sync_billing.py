import os
import json
import subprocess
import time

DB_FILE = os.path.join(os.path.dirname(__file__), "cloud_accounts_db.json")

def sync_modal_billing():
    if not os.path.exists(DB_FILE):
        return
        
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            accounts = json.load(f)
        except Exception:
            return
            
    has_changes = False
    for acc in accounts:
        if acc.get("provider") == "modal":
            print(f"Sincronizando gastos da conta: {acc['name']}...")
            env = os.environ.copy()
            env["MODAL_TOKEN_ID"] = acc["token_id"]
            env["MODAL_TOKEN_SECRET"] = acc["token_secret"]
            
            try:
                # Query all-time billing (using a broad range) or just this month
                # For simplicity, we query 'last month' + 'this month' to get recent active costs
                result = subprocess.run(
                    ["modal", "billing", "report", "--for", "this month", "--json"],
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                output = result.stdout.strip()
                if not output:
                    continue
                    
                data = json.loads(output)
                total_spend = sum(float(item.get("cost", 0.0)) for item in data)
                
                # Se quisermos que o 'last_spend' seja apenas o gasto do mês atual:
                old_spend = acc.get("last_spend", 0.0)
                if abs(old_spend - total_spend) > 0.0001:
                    print(f" -> Atualizado: ${old_spend:.4f} -> ${total_spend:.4f}")
                    acc["last_spend"] = total_spend
                    # Assume budget is 30.0 for Modal free tier
                    acc["last_balance"] = max(0.0, 30.0 - total_spend)
                    has_changes = True
                else:
                    print(f" -> Sem mudanças (Gasto atual: ${total_spend:.4f})")
                    
            except subprocess.CalledProcessError as e:
                print(f"Erro ao buscar billing para {acc['name']}: {e.stderr}")
            except Exception as e:
                print(f"Erro desconhecido para {acc['name']}: {e}")
                
    if has_changes:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=4)
        print("Banco de dados atualizado com novos saldos!")
    else:
        print("Nenhuma alteração nos saldos.")

if __name__ == "__main__":
    sync_modal_billing()
