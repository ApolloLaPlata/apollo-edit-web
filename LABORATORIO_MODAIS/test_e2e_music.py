import httpx
import asyncio
import json

async def run_e2e_test():
    print("=== INICIANDO TESTE E2E DA PIPELINE DE MÚSICA ===")
    
    # 1. Testar Geração de Ideias (LLM)
    url_batch = "http://163.176.135.59/api/music/generate_batch_ideas"
    print(f"\n1. Solicitando ideias ao LLM ({url_batch})...")
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url_batch, json={"theme": "Música cyberpunk de hackers", "count": 1})
            data = resp.json()
            if not data.get("success"):
                print("❌ Falha no LLM de Ideias:", data.get("error"))
                return
            
            track = data["tracks"][0]
            style = track["style"]
            lyrics = track["lyrics"]
            print(f"✅ Ideia Gerada com Sucesso!\nEstilo: {style}\nLetras:\n{lyrics[:100]}...\n")
    except Exception as e:
        print("❌ Erro de conexão no LLM:", e)
        return

    # 2. Testar Auto-Tag (Opcional, só pra validar)
    url_tag = "http://163.176.135.59/api/music/auto_tag_lyrics"
    print(f"2. Testando o Auto-Tag LLM ({url_tag})...")
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp_tag = await client.post(url_tag, json={"lyrics": "Invadi o sistema\nDinheiro na conta\nMatrix caiu"})
            data_tag = resp_tag.json()
            if data_tag.get("success"):
                print(f"✅ Auto-Tag funcionou: {data_tag.get('structured_lyrics')[:50]}...")
            else:
                print("❌ Falha no Auto-Tag:", data_tag.get("error"))
    except Exception as e:
        print("❌ Erro no Auto-Tag:", e)
        return

    print("\n=== TESTES CONCLUÍDOS COM SUCESSO! ===")

asyncio.run(run_e2e_test())
