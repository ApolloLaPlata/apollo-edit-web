import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.copilot_engine import CopilotEngine

router = APIRouter(prefix="/api/v1/copilot", tags=["Copilot"])

copilot_engine = CopilotEngine()

class CopilotRequest(BaseModel):
    prompt: str

@router.post("/query")
def api_query_copilot(req: CopilotRequest):
    try:
        response = copilot_engine.query_copilot(req.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
