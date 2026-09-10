import re

file_path = "/home/ubuntu/apollo_edit/servidor_web.py"
try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("Arquivo não encontrado. Execute este script na pasta raiz da VPS.")
    exit(1)

# Precisamos encontrar a função audio_interceptor inteira.
pattern = re.compile(r'async def audio_interceptor\(\):.*?return StreamingResponse\(audio_interceptor\(\)\)', re.DOTALL)

new_audio_interceptor = """            async def audio_interceptor():
                yield json.dumps({"status": "processing", "message": "Conectando ao roteador de áudio na nuvem..."}).encode('utf-8') + b'\\n'
                try:
                    import httpx
                    async with httpx.AsyncClient(timeout=1200.0) as local_client:
                        async with local_client.stream("POST", modal_url, content=body, headers=req_headers) as response:
                            if response.status_code != 200:
                                err_content = await response.aread()
                                yield err_content
                                return
                            
                            async for line in response.aiter_lines():
                                if not line:
                                    continue
                                try:
                                    data = json.loads(line)
                                except Exception:
                                    continue
                                
                                if data.get("status") == "success" and "audio_base64" in data:
                                    import base64
                                    import uuid
                                    b64_string = data["audio_base64"]
                                    audio_bytes = base64.b64decode(b64_string)
                                    
                                    filename = f"audio_{uuid.uuid4().hex}.wav"
                                    filepath = f"/home/ubuntu/apollo_edit/media/{filename}"
                                    try:
                                        with open(filepath, "wb") as af:
                                            af.write(audio_bytes)
                                        print(f"[Modal Proxy] Audio salvo na Oracle: {filename}")
                                        data.pop("audio_base64", None)
                                        data["audio_url"] = f"https://www.apolloedit.com.br/media/{filename}"
                                    except Exception as ex:
                                        print(f"[Modal Proxy] Erro ao salvar WAV: {ex}")
                                        
                                    yield json.dumps(data).encode('utf-8') + b'\\n'
                                else:
                                    # É apenas um heartbeat ou erro da nuvem, repassa pro frontend
                                    yield line.encode('utf-8') + b'\\n'
                except Exception as e:
                    print(f"[Modal Proxy Audio Error]: {e}")
                    yield json.dumps({"status": "error", "message": f"Erro de Conexão Nuvem-VPS: {str(e)}"}).encode('utf-8') + b'\\n'

            return StreamingResponse(audio_interceptor())"""

if pattern.search(content):
    content = pattern.sub(new_audio_interceptor, content)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCH APLICADO COM SUCESSO! A rota de audio_lab agora lê o stream corretamente.")
else:
    print("ERRO: Não encontrei a função audio_interceptor() no arquivo.")
