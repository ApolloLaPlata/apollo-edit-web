import asyncio
import httpx
import base64
import os

async def test_modal_endpoints():
    print("🚀 INICIANDO TESTE DIRETO NOS WEBHOOKS DA CONTA 10 (MODAL)")
    
    # Vamos ler o arquivo local para testar a clonagem
    audio_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\voices\xtts\narrador_ref.wav"
    with open(audio_path, "rb") as f:
        ref_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    text_to_say = "Testando comunicação direta com a nuvem Modal. Este é o ambiente de auditoria."
    ref_text = "O homem se escondeu nas sombras daquela velha montanha."
    instruct = "Fale com uma voz dramática e séria."
    
    endpoints = {
        "XTTS": {
            "url": "https://apollolaplata--apollo-api-xtts.modal.run",
            "payload": {
                "text": text_to_say,
                "ref_audio_base64": ref_b64,
                "language": "pt",
                "temperature": 0.7,
                "speed": 1.0,
                "return_raw_wav": True
            }
        },
        "Qwen-TTS": {
            "url": "https://apollolaplata--apollo-api-qwen-tts.modal.run",
            "payload": {
                "text": text_to_say,
                "reference_audio_base64": ref_b64,
                "reference_text": ref_text,
                "instruct": instruct,
                "language": "Portuguese"
            }
        },
        "F5-TTS": {
            "url": "https://apollolaplata--apollo-api-f5-tts.modal.run",
            "payload": {
                "text": text_to_say,
                "ref_audio_base64": ref_b64,
                "ref_text": ref_text
            }
        },
        "Moss-TTS": {
            "url": "https://apollolaplata--apollo-api-moss-tts.modal.run",
            "payload": {
                "text": text_to_say,
                "reference_audio_base64": ref_b64
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        for name, config in endpoints.items():
            print(f"\n========================================")
            print(f"🔄 Testando: {name}...")
            print(f"🔗 URL: {config['url']}")
            try:
                res = await client.post(config['url'], json=config['payload'])
                if res.status_code == 200:
                    ctype = res.headers.get("content-type")
                    size = len(res.content) / 1024
                    print(f"✅ {name} funcionou! [200 OK]")
                    print(f"📦 Content-Type: {ctype} | Tamanho: {size:.2f} KB")
                    
                    if size > 1.0:
                        save_path = f"E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\valida_{name}.wav"
                        with open(save_path, "wb") as f:
                            f.write(res.content)
                        print(f"💾 Salvo em: {save_path}")
                else:
                    print(f"❌ {name} Falhou! Código: {res.status_code}")
                    print(f"📜 Detalhe: {res.text}")
            except Exception as e:
                print(f"💥 {name} Timeout ou Falha Crítica: {e}")

if __name__ == "__main__":
    asyncio.run(test_modal_endpoints())
