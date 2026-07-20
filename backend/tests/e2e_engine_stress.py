import httpx
import sys
sys.stdout.reconfigure(encoding='utf-8')
"""
e2e_engine_stress.py - Teste End-to-End do Roteamento e Geração de Roteiro
==========================================================================
Simula a jornada completa de um usuário (com e sem tokens) acessando a API 
de geração de vídeo e roteiro, testando a resiliência do WaterfallRouter e dos Agentes.
"""

import sys
import os
import asyncio
from httpx import AsyncClient

# Garante que o diretório pai esteja no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app
from backend.financial_agent.coin_ledger import create_user_record, get_wallet, credit_user

async def run_e2e_tests():
    print("\n[E2E] 🚀 Iniciando Teste de Estresse do Motor 3.0...\n")
    
    # 1. Cria usuário de teste
    test_user_id = "test_e2e_user_999"
    test_email = "e2e_stress@apollo.test"
    try:
        create_user_record(test_user_id, test_email, "dummy_hash")
        print(f"[E2E] ✅ Usuário {test_email} criado no Ledger.")
    except Exception:
        print(f"[E2E] ⚠️ Usuário {test_email} já existia, prosseguindo.")
        
    wallet_before = get_wallet(test_user_id)
    print(f"[E2E] 💼 Carteira Inicial: {wallet_before.get('coins')} coins, {wallet_before.get('chips_llm')} chips LLM")

    # 2. Testa a Rota de Geração de Roteiro
    print("\n[E2E] 🧪 Disparando /api/v1/videos/generate...")
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # Falso header de autorização para bypass do middleware se existir, ou usar dados diretos
        payload = {
            "tipo_esteira": "dark_channel",
            "tema": "Como sobreviver ao inverno na Sibéria",
            "copiloto_id": "filosofia",
            "user_id": test_user_id
        }
        
        response = await client.post("/api/v1/videos/generate", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("[E2E] ✅ Resposta Sucesso (200 OK)")
            print(f"[E2E] 📜 Roteiro Gerado (trecho): {str(data.get('script', ''))[:150]}...")
            print(f"[E2E] 🌐 Roteador Usado: {data.get('provider')}")
        else:
            print(f"[E2E] ❌ Falha na Rota: {response.status_code}")
            print(response.json())
            
    # 3. Verifica cobrança no Ledger
    wallet_after = get_wallet(test_user_id)
    print(f"\n[E2E] 💼 Carteira Final: {wallet_after.get('coins')} coins, {wallet_after.get('chips_llm')} chips LLM")
    
    if wallet_after.get('chips_llm', 0) < wallet_before.get('chips_llm', 0):
        print("[E2E] ✅ O EconomyAgent funcionou perfeitamente e cobrou a taxa LLM.")
    else:
        print("[E2E] ❌ O EconomyAgent não debitou os fundos do usuário!")

    print("\n[E2E] 🏁 Teste de Estresse Finalizado.")

if __name__ == "__main__":
    asyncio.run(run_e2e_tests())
