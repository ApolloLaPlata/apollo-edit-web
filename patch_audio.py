import re

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_interceptor = '''
            async def audio_interceptor():
                yield json.dumps({"status": "processing", "message": "Iniciando geraÃ§Ã£o de Ã¡udio no Modal..."}).encode('utf-8') + b"\\n"
                try:
                    print(f"[Modal Proxy] Interceptando requisiÃ§Ã£o para audio_lab...")
                    import httpx
                    import asyncio
                    async with httpx.AsyncClient(timeout=1200.0) as local_client:
                        # Executa a requisiÃ§Ã£o em background
                        task = asyncio.create_task(local_client.post(modal_url, content=body, headers=req_headers))
                        
                        # Loop para manter o Vercel vivo mandando pings a cada 5 segundos
                        while not task.done():
                            yield json.dumps({"status": "processing", "message": "Processando Ã¡udio na nuvem..."}).encode('utf-8') + b"\\n"
                            await asyncio.sleep(5)
                            
                        response = task.result()
                        
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
                            # Remove o audio_base64 para economizar banda (opcional, mas bom)
                            data.pop("audio_base64", None)
                            data["audio_url"] = f"https://www.apolloedit.com.br/media/{filename}"
                            data["message"] = "Audio gerado e salvo com sucesso!"
                            
                            yield json.dumps(data).encode('utf-8') + b"\\n"
                        else:
                            yield response.content + b"\\n"
                except Exception as e:
                    print(f"[Modal Proxy Audio Error]: {e}")
                    yield json.dumps({"status": "error", "message": f"Erro proxy interceptor: {str(e)}"}).encode('utf-8') + b"\\n"
'''

# Substitui a versÃ£o antiga
# O regex vai encontrar o def audio_interceptor() ate o final do bloco
text = re.sub(r'async def audio_interceptor\(\):[\s\S]*?yield json.dumps\(\{"status": "error"[\s\S]*?b"\\n"', new_interceptor.strip(), text)

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Substituicao concluida")
