import re

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/apollo_modal_engine.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """        # AQUI FOI REMOVIDO O STREAMING_RESPONSE PORQUE O PROXY DA ORACLE JÁ FAZ HEARTBEAT
        from modal.functions import FunctionCall
        import base64
        
        call_fc = FunctionCall.from_id(fc.object_id)
        # Usamos .get() de forma sincrona já que a thread atual é do FastAPI Worker (sem problemas no Modal)
        try:
            res = call_fc.get(timeout=1200)
            
            if isinstance(res, bytes):
                b64 = base64.b64encode(res).decode('utf-8')
                return {"status": "success", "audio_base64": b64, "message": f"{model.upper()} Recebido da Nuvem!"}
            elif isinstance(res, dict) and "audio_base64" in res:
                return {"status": "success", "audio_base64": res["audio_base64"], "message": f"{model.upper()} Recebido da Nuvem!"}
            else:
                return {"status": "error", "error_type": "generation_failed", "message": f"Erro na geracao {model}: formato desconhecido"}
                
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return {"status": "error", "message": f"Erro interno AudioLab: {str(e)}", "trace": error_trace}"""

new_block = """        async def stream_result():
            try:
                from modal.functions import FunctionCall
                import asyncio
                import json
                import base64
                
                # Retrieve the FunctionCall by its ID
                call_fc = FunctionCall.from_id(fc.object_id)
                task = asyncio.create_task(call_fc.get.aio(timeout=1200))
                
                while not task.done():
                    yield json.dumps({"status": "processing", "message": f"Processando áudio na nuvem... ({model})"}) + "\\n"
                    done, pending = await asyncio.wait([task], timeout=5.0)
                    if done:
                        break
                        
                res = task.result()
                
                if isinstance(res, bytes):
                    b64 = base64.b64encode(res).decode('utf-8')
                    yield json.dumps({"status": "success", "audio_base64": b64, "message": f"{model.upper()} Recebido da Nuvem!"}) + "\\n"
                elif isinstance(res, dict) and "audio_base64" in res:
                    yield json.dumps({"status": "success", "audio_base64": res["audio_base64"], "message": f"{model.upper()} Recebido da Nuvem!"}) + "\\n"
                else:
                    yield json.dumps({"status": "error", "error_type": "generation_failed", "message": f"Erro na geracao {model}: formato desconhecido"}) + "\\n"
                    
            except Exception as e:
                import traceback
                import json
                error_trace = traceback.format_exc()
                yield json.dumps({"status": "error", "message": f"Erro interno AudioLab: {str(e)}", "trace": error_trace}) + "\\n"

        return StreamingResponse(stream_result(), media_type="application/x-ndjson")"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Sucesso ao restaurar o streaming.")
else:
    print("Bloco não encontrado.")
