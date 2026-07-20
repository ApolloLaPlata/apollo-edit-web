import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.settings_manager import ConfigManager

router = APIRouter(prefix="/api/v1/settings", tags=["Configuracoes"])

# Load config manager instance globally
config_file = os.path.join(os.getcwd(), "config.json")
config_manager = ConfigManager(config_file)

class SettingsRequest(BaseModel):
    settings: Dict[str, Any]

@router.get("/")
def api_get_settings():
    return {"settings": config_manager.config}

@router.post("/update")
def api_update_settings(req: SettingsRequest):
    for key, value in req.settings.items():
        config_manager.set(key, value)
    config_manager.save_config()
    return {"success": True, "message": "Configurações atualizadas"}
