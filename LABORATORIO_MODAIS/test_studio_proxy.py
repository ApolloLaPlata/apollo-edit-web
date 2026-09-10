import asyncio
import httpx
import base64

async def test():
    print("Iniciando requisicao para api.apolloedit.com...")
    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.apolloedit.com/api/studio/modal/generate_image", json={
            "prompt": "a beautiful landscape of mountains at sunset, detailed, vibrant colors",
            "model": "flux2-universal",
            "format": "horizontal",
            "steps": 20
        }, timeout=600.0)
        
        print("Status code:", res.status_code)
        
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "processing":
                job_id = data.get("job_id")
                print(f"Job iniciado! ID: {job_id}. Aguardando conclusao...")
                
                while True:
                    await asyncio.sleep(5)
                    poll_res = await client.get(f"https://api.apolloedit.com/api/studio/modal/status/{job_id}")
                    if poll_res.status_code == 200:
                        poll_data = poll_res.json()
                        status = poll_data.get("status")
                        print(f"Status atual: {status}")
                        if status == "success":
                            b64_data = poll_data.get("image_base64")
                            if b64_data:
                                with open("test_proxy_output.png", "wb") as f:
                                    f.write(base64.b64decode(b64_data))
                                print("SUCESSO: Imagem salva em test_proxy_output.png!")
                                break
                            else:
                                print("ERRO: Status success mas sem imagem.", poll_data)
                                break
                        elif status == "error":
                            print("ERRO na geracao:", poll_data)
                            break
                    else:
                        print("Erro no polling:", poll_res.text)
                        break
            else:
                print("ERRO na requisicao inicial:", data)
        else:
            print("Response:", res.text)

asyncio.run(test())
