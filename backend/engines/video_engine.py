import logging
import asyncio
import os
import json
import uuid
from typing import Dict, Any

logger = logging.getLogger("VideoEngine")

class AsyncVideoEngine:
    """
    Motor Assíncrono de Vídeo.
    Envelopa o complexo script `render_timeline.py` para executá-lo de forma assíncrona
    no background, liberando o FastAPI e o Maestro para continuarem operando.
    """
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.render_script = os.path.join(self.root_path, "render_timeline.py")
        self.active_renders: Dict[str, asyncio.Task] = {}
        self.render_status: Dict[str, Dict[str, Any]] = {}

    async def start_render(self, timeline_json: Dict[str, Any]) -> str:
        """
        Inicia uma renderização em background.
        Salva o JSON temporário, dispara o processo FFmpeg e monitora o progresso.
        Retorna o job_id da renderização.
        """
        job_id = str(uuid.uuid4())
        json_path = os.path.join(self.root_path, f"timeline_export_job_{job_id}.json")
        
        # Salva o arquivo de instrução para o script legado
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(timeline_json, f, ensure_ascii=False)
            
        self.render_status[job_id] = {"state": "starting", "progress": 0, "message": "Iniciando motor FFmpeg..."}
        
        # Dispara a Task no background
        task = asyncio.create_task(self._run_render_process(job_id, json_path))
        self.active_renders[job_id] = task
        
        return job_id

    async def _run_render_process(self, job_id: str, json_path: str):
        """Executa o render_timeline.py no terminal sem bloquear."""
        try:
            self.render_status[job_id]["state"] = "processing"
            
            # O script render_timeline_async.py (ou o próprio modificado) precisaria ler o JSON específico.
            # Como o render_timeline.py legado lê de timeline_export.json chumbado, precisamos passar o path se modificá-lo.
            # Aqui assumimos que chamamos o script passando o path como argumento.
            
            cmd = ["python", self.render_script, json_path]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.root_path
            )
            
            # Lê o stderr em tempo real para extrair progresso se o script ecoar algo
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                # Se o script printar progresso, podemos capturar aqui
                decoded = line.decode('utf-8', errors='replace').strip()
                logger.debug(f"[VideoEngine-{job_id}] {decoded}")
                
            await process.wait()
            
            if process.returncode == 0:
                self.render_status[job_id] = {"state": "done", "progress": 100, "message": "Renderização concluída com sucesso."}
                logger.info(f"✅ [VideoEngine] Job {job_id} concluído.")
            else:
                stderr = await process.stderr.read()
                err_msg = stderr.decode('utf-8', errors='replace')
                self.render_status[job_id] = {"state": "error", "progress": 0, "message": f"Erro FFmpeg: {err_msg[:200]}"}
                logger.error(f"❌ [VideoEngine] Job {job_id} falhou: {err_msg}")
                
        except Exception as e:
            self.render_status[job_id] = {"state": "error", "progress": 0, "message": str(e)}
            logger.error(f"❌ [VideoEngine] Exceção no Job {job_id}: {e}")
        finally:
            # Limpeza do JSON temporário
            if os.path.exists(json_path):
                try:
                    os.remove(json_path)
                except:
                    pass

    def get_status(self, job_id: str) -> Dict[str, Any]:
        return self.render_status.get(job_id, {"state": "not_found", "progress": 0})
