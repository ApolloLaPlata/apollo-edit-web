import asyncio
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("PhantomFleet")
logger.setLevel(logging.INFO)

class PhantomFleetManager:
    def __init__(self):
        # Armazena as conexões ativas (Sockets das extensões do Chrome)
        self.active_extensions = {}
        # Armazena os Future objects das tarefas em andamento para podermos devolver a resposta
        self.pending_tasks = {}
        self.task_counter = 0
        
    async def connect(self, websocket, ext_id: str):
        """Registra uma extensão conectada na Frota"""
        await websocket.accept()
        self.active_extensions[ext_id] = websocket
        logger.info(f"[Phantom Fleet] Extensão aliada conectada! ID: {ext_id}")

    def disconnect(self, ext_id: str):
        """Remove a extensão caso ela desconecte ou feche a aba"""
        if ext_id in self.active_extensions:
            del self.active_extensions[ext_id]
            logger.warning(f"[Phantom Fleet] Extensão desconectada. ID: {ext_id}")

    async def send_job(self, ext_id: str, prompt: str) -> Dict[str, Any]:
        """
        Envia uma ordem de trabalho para a extensão gerar uma imagem/vídeo,
        e fica aguardando (await) a extensão responder com o link de download.
        """
        if ext_id not in self.active_extensions:
            return {"status": "error", "message": f"Extensão {ext_id} não está online."}
            
        websocket = self.active_extensions[ext_id]
        
        self.task_counter += 1
        task_id = f"phantom_task_{self.task_counter}"
        
        # Cria um "telefone" para essa tarefa específica
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.pending_tasks[task_id] = future
        
        # Manda a ordem pelo rádio para o Javascript
        payload = {
            "action": "generate_media",
            "task_id": task_id,
            "prompt": prompt
        }
        
        logger.info(f"[Phantom Fleet] Enviando Ordem: {payload} para {ext_id}")
        await websocket.send_text(json.dumps(payload))
        
        # Espera o Javascript mandar a resposta de volta com o mesmo task_id
        try:
            # Espera até 5 minutos (vídeo pode demorar)
            result = await asyncio.wait_for(future, timeout=300.0)
            return result
        except asyncio.TimeoutError:
            return {"status": "error", "message": "Timeout. A extensão não devolveu o arquivo a tempo."}
        finally:
            if task_id in self.pending_tasks:
                del self.pending_tasks[task_id]

    async def handle_incoming_message(self, ext_id: str, text_data: str):
        """Processa as respostas recebidas da extensão"""
        try:
            data = json.loads(text_data)
            action = data.get("action")
            
            if action == "media_ready":
                task_id = data.get("task_id")
                result_url = data.get("url")
                
                logger.info(f"[Phantom Fleet] Recebido download de {ext_id}: {result_url}")
                
                # Desperta a função `send_job` entregando a url recebida
                if task_id in self.pending_tasks and not self.pending_tasks[task_id].done():
                    self.pending_tasks[task_id].set_result({"status": "success", "url": result_url})
            else:
                logger.warning(f"[Phantom Fleet] Mensagem desconhecida de {ext_id}: {data}")
                
        except Exception as e:
            logger.error(f"[Phantom Fleet] Erro ao processar mensagem: {str(e)}")

# Instância global do general da frota
phantom_commander = PhantomFleetManager()
