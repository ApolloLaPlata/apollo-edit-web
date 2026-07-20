import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.ai_director import AIDirectorPipeline

router = APIRouter(prefix="/api/v1/ai-director", tags=["AI Director"])

# We instantiate with a dummy config manager, or read from env
class DummyConfig:
    def get(self, key, default=None):
        return os.environ.get(key, default)
    def get_api_config(self, *args, **kwargs):
        return None

director = AIDirectorPipeline(config_manager=DummyConfig())

class AnalysisRequest(BaseModel):
    roteiro: str
    pastas_disponiveis: List[str]
    configs: Optional[Dict[str, Any]] = None

@router.post("/analyze")
def api_analyze_script(req: AnalysisRequest):
    try:
        # Passar os parametros corretos: self, texto_roteiro, subpastas_disponiveis, configs_diretor
        configs = req.configs or {}
        if 'llm_provider' not in configs:
            configs['llm_provider'] = "gemini"
        
        result = director.analisar_roteiro(req.roteiro, req.pastas_disponiveis, configs)
        return {"success": True, "analysis": result, "tokens_used": director.get_last_token_usage()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
