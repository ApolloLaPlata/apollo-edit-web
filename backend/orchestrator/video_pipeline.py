import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from backend.api.lightning_client import LightningClient
import os

logger = logging.getLogger("VideoPipeline")

class BaseVideoPipeline(ABC):
    """
    Classe base para todas as 'Esteiras' de geração de conteúdo do Apollo.
    Define o esqueleto do processo.
    """
    def __init__(self, lightning_api_key: str):
        self.llm_client = LightningClient(api_key=lightning_api_key)
        
    @abstractmethod
    async def process(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a esteira inteira e retorna o resultado final.
        """
        pass

class DarkChannelPipeline(BaseVideoPipeline):
    """
    Esteira especializada para Canais Dark (Delegação para Lightning AI).
    O Servidor FastAPI atua apenas como Roteador e repassa a carga pesada para a nuvem da Lightning.
    """
    async def process(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Iniciando Esteira Canal Dark (Modo Delegação Lightning)...")
        
        tema = request_data.get("tema", "Mistérios")
        copiloto = request_data.get("copiloto", "Você é um roteirista de suspense.")
        user_id = request_data.get("user_id", "anonymous")
        
        from backend.api.routes_ui_ws import ui_ws_manager
        from backend.services.storage_service import storage_service
        import asyncio
        import os
        import httpx
        
        # Etapa 1: Gerar Roteiro (Feito localmente ou via API leve LLM)
        logger.info("Etapa 1/4: Gerando Roteiro Base...")
        await ui_ws_manager.send_to_user(user_id, "progress_update", {"stage": "Gerando Roteiro", "progress": 25})
        
        roteiro = self.llm_client.generate_text(
            prompt=f"Escreva um roteiro curto e engajador de 1 minuto sobre o tema: {tema}.",
            system_prompt=copiloto
        )
        
        # Etapa 2: Gerar Prompts Visuais
        logger.info("Etapa 2/4: Extraindo Prompts Visuais...")
        await ui_ws_manager.send_to_user(user_id, "progress_update", {"stage": "Processando Imagens", "progress": 40})
        
        prompts = self.llm_client.generate_text(
            prompt=f"Com base neste roteiro, gere 5 prompts em inglês para geração de imagens Midjourney/Flux: {roteiro}",
            system_prompt="Você é um diretor de arte focado em imagens hiper-realistas."
        )
        
        # Etapa 3: DELEGAÇÃO PARA O LIGHTNING AI (Processamento pesado FFmpeg/TTS)
        logger.info("Etapa 3/4: Acordando Máquina Lightning AI para Renderização (FFmpeg + TTS)...")
        await ui_ws_manager.send_to_user(user_id, "progress_update", {"stage": "Renderizando na Lightning", "progress": 60})
        
        # Simulando a chamada de Webhook/API para a sua máquina Lightning Studio
        # Em produção, usaremos algo como:
        # async with httpx.AsyncClient() as client:
        #     response = await client.post("https://seu-lightning-studio-url.com/render", json={...})
        await asyncio.sleep(2) # Simula o tempo de rede
        
        # Etapa 4: Recebimento do Vídeo da Lightning
        logger.info("Etapa 4/4: Recebendo Vídeo da Nuvem...")
        await ui_ws_manager.send_to_user(user_id, "progress_update", {"stage": "Finalizando", "progress": 95})
        
        video_url = "https://cdn.lightning.ai/seu-video-pronto.mp4"
        
        await ui_ws_manager.send_to_user(user_id, "progress_update", {"stage": "Concluído", "progress": 100})
        logger.info("Esteira Canal Dark finalizada. Vídeo gerado pela Lightning.")
        
        return {
            "status": "success",
            "pipeline": "dark_channel",
            "roteiro_final": roteiro,
            "prompts_visuais": prompts,
            "video_url": video_url,
            "mensagem": "Vídeo processado com sucesso pelos estúdios Lightning AI."
        }

class TraditionalEditPipeline(BaseVideoPipeline):
    """
    Esteira especializada para Editores Tradicionais (Usuário envia o arquivo bruto).
    """
    async def process(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Iniciando Esteira Edição Tradicional...")
        # Lógica para cortes secos, legendagem via Whisper, etc.
        return {
            "status": "success",
            "pipeline": "traditional_edit",
            "mensagem": "Cortes e correções finalizadas via FFmpeg."
        }

class PipelineOrchestrator:
    """
    O 'Gerente' que decide qual esteira acionar com base no pedido do cliente.
    """
    def __init__(self):
        # A chave deve idealmente vir do cofre ou sistema de rodízio
        self.api_key = os.environ.get("LIGHTNING_API_KEY", "dummy_key")
        
        self.pipelines = {
            "dark_channel": DarkChannelPipeline(self.api_key),
            "traditional_edit": TraditionalEditPipeline(self.api_key)
        }

    async def run_pipeline(self, pipeline_type: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        if pipeline_type not in self.pipelines:
            raise ValueError(f"Esteira desconhecida: {pipeline_type}")
            
        pipeline = self.pipelines[pipeline_type]
        return await pipeline.process(request_data)
