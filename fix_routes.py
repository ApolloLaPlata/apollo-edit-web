import re

filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\api\routes_video.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

correct_code = '''    request_data = {
        "tema": request.tema,
        "copiloto": request.copiloto_id,
        "instrucoes": request.instrucoes_adicionais,
        "user_id": request.user_id
    }
    
    try:
        # Coloca o pedido na fila de renderização assíncrona ao invés de bloquear a rota HTTP
        from backend.services.render_queue import render_queue
        await render_queue.add_task(orchestrator.run_pipeline, request.tipo_esteira, request_data)
        
        return {"status": "success", "message": "Vídeo adicionado à fila de renderização. Acompanhe o progresso na interface."}
    except Exception as e:
        logger.error(f"Erro Crítico na Geração: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no Servidor Apollo durante a geração do vídeo.")'''

# I'll use simple replace to avoid regex issues on the end of the file
content = content.replace('''    request_data = {
        "tema": request.tema,
        "copiloto": request.copiloto_id,
        "instrucoes": request.instrucoes_adicionais
    }
    
    try:
        # Passa o pedido para o Orquestrador Nativo em Python
        resultado = await orchestrator.run_pipeline(request.tipo_esteira, request_data)
        return resultado
    except ValueError as ve:
        logger.error(f"Erro de Validao na Esteira: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Erro Crtico na Gerao: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no Servidor Apollo durante a gerao do vdeo.")''', correct_code)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
