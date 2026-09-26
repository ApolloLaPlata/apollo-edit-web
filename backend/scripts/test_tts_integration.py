import asyncio
import httpx
import sys

async def test_tts_models():
    # Modelos a serem testados
    models_to_test = [
        "XTTS",
        "Qwen-TTS", 
        "F5-TTS",
        "Moss-TTS"
    ]
    
    url = "http://127.0.0.1:8000/api/studio/modal/eleven_lab"
    
    for model in models_to_test:
        print(f"\n=============================================")
        print(f"🔄 Testando Modelo: {model}")
        
        payload = {
            "model": model,
            "text": "Olá, este é um teste de áudio executado pelo sistema automático do Antigravity.",
            "voice_name": "female_clean_ref",  # Voz nativa do backend
            "instruct": "Fale com muita alegria e animação",  # Para o Qwen
            "ref_text": "Olá, eu sou a voz feminina de referência." # Para F5 e Qwen
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                print(f"📡 Enviando requisição para o backend local (que redirecionará para Modal Conta 10)...")
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    content_type = response.headers.get("content-type")
                    data_len = len(response.content)
                    print(f"✅ SUCESSO! Código: 200")
                    print(f"📦 Content-Type: {content_type}")
                    print(f"📊 Tamanho do Áudio: {data_len / 1024:.2f} KB")
                    
                    if data_len > 1000:
                        file_ext = "wav" if "wav" in content_type else ("ogg" if "ogg" in content_type else "mp3")
                        save_path = f"E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\teste_{model}.{file_ext}"
                        with open(save_path, "wb") as f:
                            f.write(response.content)
                        print(f"💾 Áudio salvo fisicamente em: {save_path}")
                    else:
                        print("⚠️ O áudio parece muito pequeno para ser válido!")
                        
                else:
                    print(f"❌ ERRO! Código: {response.status_code}")
                    print(f"📜 Detalhe: {response.text}")
                    
        except Exception as e:
            print(f"💥 Falha catastrófica ao testar {model}: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DE INTEGRAÇÃO TTS (END-TO-END)")
    asyncio.run(test_tts_models())
