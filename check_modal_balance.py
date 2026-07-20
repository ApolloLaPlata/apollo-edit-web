import subprocess
import json
import sys

def check_balance():
    print("Obtendo dados de faturamento da Modal (mês atual)...")
    try:
        result = subprocess.run(
            ["modal", "billing", "report", "--for", "this month", "--json"], 
            capture_output=True, text=True, check=True
        )
        
        data = json.loads(result.stdout)
        total_cost = 0.0
        
        for item in data:
            total_cost += float(item.get("cost", 0))
            
        free_tier = 30.0
        remaining = free_tier - total_cost
        
        print(f"\n--- Resumo de Saldo Modal (Conta Ativa) ---")
        print(f"Gasto Total no Mês: ${total_cost:.4f}")
        print(f"Crédito Grátis Restante (Est.): ${remaining:.4f}")
        print("------------------------------------------")
        
        if remaining < 5.0:
            print("⚠️ ATENÇÃO: O saldo gratuito está acabando!")
            
    except subprocess.CalledProcessError as e:
        print("Erro ao consultar o saldo Modal:", e.stderr)
    except Exception as e:
        print("Erro inesperado:", str(e))

if __name__ == "__main__":
    check_balance()
