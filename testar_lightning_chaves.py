import asyncio
from backend.cloud_tools.account_pool import account_pool
from backend.api.lightning_client import LightningClient

async def test_keys():
    accounts = account_pool.get_all()
    print(f"Testando {len(accounts)} contas Lightning AI do Pool...")
    
    for acc in accounts:
        print(f"\n--- Testando Conta: {acc.label} ({acc.id}) ---")
        client = LightningClient(api_key=acc.api_key)
        try:
            # Faz uma chamada simples para testar a chave
            response = client.generate_text("Diga 'Teste concluido com sucesso' em portugues.", model="openai/gpt-4o")
            print(f"[SUCESSO] A chave da conta '{acc.label}' esta funcionando!")
            print(f"Resposta da IA: {response}")
        except Exception as e:
            print(f"[ERRO] A chave da conta '{acc.label}' falhou!")
            print(f"Detalhes: {e}")

if __name__ == '__main__':
    asyncio.run(test_keys())
