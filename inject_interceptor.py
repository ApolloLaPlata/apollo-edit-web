import sys
import os

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    text = f.read()

intercept_code = """
        if path == "generate/audio_lab":
            import json
            import uuid
            
            async def audio_interceptor():
                try:
                    print(f"[Modal Proxy] Interceptando requisição para audio_lab...")
                    response = await client.send(req, stream=False)
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
                        
                        # Retorna a nova resposta com a URL em vez do base64 gigante
                        new_data = {
                            "status": "success",
                            "audio_url": f"https://www.apolloedit.com.br/media/{filename}",
                            "message": "SA3 Recebido e salvo na Oracle!"
                        }
                        yield json.dumps(new_data).encode('utf-8')
                    else:
                        yield response.content
                except Exception as e:
                    print(f"[Modal Proxy Audio Error]: {e}")
                    yield json.dumps({"status": "error", "message": f"Erro proxy interceptor: {str(e)}"}).encode('utf-8')

            return StreamingResponse(audio_interceptor())
"""

# Find where to inject it. We inject it right before 	_start = time.time()
if 'if path == "generate/audio_lab":' not in text:
    text = text.replace(
        "t_start = time.time()",
        intercept_code + "\n    t_start = time.time()"
    )

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(text)
