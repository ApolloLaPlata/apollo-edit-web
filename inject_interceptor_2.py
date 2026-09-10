import sys

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Primeiro remover o interceptor antigo que estava antes de 	_start = time.time()
import re
text = re.sub(r'        if path == "generate/audio_lab":[\s\S]*?return StreamingResponse\(audio_interceptor\(\)\)', '', text)

# Agora vamos injetar o novo interceptor, MAS ele precisa ceder um status 'processing' primeiro!
intercept_code = """
        if path == "generate/audio_lab":
            import json
            import uuid
            
            async def audio_interceptor():
                yield json.dumps({"status": "processing", "message": "Iniciando geração de áudio no Modal..."}).encode('utf-8') + b"\\n"
                try:
                    print(f"[Modal Proxy] Interceptando requisição para audio_lab...")
                    import httpx
                    # Temos que fazer a requisição nós mesmos porque o client.send original blockearia o yield
                    async with httpx.AsyncClient(timeout=1200.0) as local_client:
                        response = await local_client.post(modal_url, content=body, headers=req_headers)
                        if response.status_code != 200:
                            yield response.content
                            return
                        
                        data = response.json()
                        if data.get("status") == "success" and "audio_base64" in data:
                            import base64
                            b64_string = data["audio_base64"]
                            audio_bytes = base64.b64decode(b64_string)
                            
                            filename = f"audio_{uuid.uuid4().hex}.wav"
                            filepath = f"/home/ubuntu/apollo_edit/media/{filename}"
                            with open(filepath, "wb") as af:
                                af.write(audio_bytes)
                            
                            print(f"[Modal Proxy] Audio salvo na Oracle: {filename}")
                            new_data = {
                                "status": "success",
                                "audio_url": f"https://www.apolloedit.com.br/media/{filename}",
                                "message": "SA3 Recebido e salvo na Oracle!"
                            }
                            yield json.dumps(new_data).encode('utf-8') + b"\\n"
                        else:
                            yield response.content + b"\\n"
                except Exception as e:
                    print(f"[Modal Proxy Audio Error]: {e}")
                    yield json.dumps({"status": "error", "message": f"Erro proxy interceptor: {str(e)}"}).encode('utf-8') + b"\\n"

            return StreamingResponse(audio_interceptor())
"""

text = text.replace(
    "t_start = time.time()",
    intercept_code + "\n    t_start = time.time()"
)

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(text)
