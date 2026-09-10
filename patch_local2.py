with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded.py', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('async def audio_interceptor():')
end_idx = text.find('return StreamingResponse(audio_interceptor())')

if start_idx != -1 and end_idx != -1:
    new_interceptor = '''async def audio_interceptor():
                yield json.dumps({"status": "processing", "message": "Iniciando geração de áudio no Modal..."}).encode('utf-8') + b"\\n"
                try:
                    print(f"[Modal Proxy] Interceptando requisição para audio_lab...")
                    import httpx
                    import asyncio
                    async with httpx.AsyncClient(timeout=1200.0) as local_client:
                        task = asyncio.create_task(local_client.post(modal_url, content=body, headers=req_headers))
                        
                        while not task.done():
                            yield json.dumps({"status": "processing", "message": "Processando áudio na nuvem..."}).encode('utf-8') + b"\\n"
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
    text = text[:start_idx] + new_interceptor + text[end_idx:]

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded.py', 'w', encoding='utf-8') as f:
    f.write(text)

import py_compile
try:
    py_compile.compile('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded.py', doraise=True)
    print("Sintaxe Python Correta!")
except Exception as e:
    print(f"Erro de sintaxe: {e}")
