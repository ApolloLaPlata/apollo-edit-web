from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
import os
import requests
import logging

logger = logging.getLogger("SystemLogger")
router = APIRouter()
security = HTTPBasic()

# Credenciais do Painel de Controle (Pode ser alterado no .env depois)
ADMIN_USER = os.getenv("RADIO_ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("RADIO_ADMIN_PASS", "darktrap247")

# Token da Conta 2 (V5estudio) para ler o Galpao Privado
HF_TOKEN = os.getenv("HF_TOKEN_V5ESTUDIO", "")
DATASET_REPO = "V5estudio/radio-assets-24h"

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USER or credentials.password != ADMIN_PASS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso Negado à Torre de Controle",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@router.get("/inventory")
async def get_inventory(admin: str = Depends(verify_admin)):
    """
    Lista os arquivos de video salvos no Galpao Privado (HF Conta 2).
    """
    try:
        url = f"https://huggingface.co/api/datasets/{DATASET_REPO}/tree/main"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        # Desabilita verify=False temporariamente caso haja erro de SSL local no Python do Windows
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 404:
            return JSONResponse(content={"hf_galpao": [], "status": "Dataset vazio ou nao encontrado."})
            
        response.raise_for_status()
        files = response.json()
        
        video_files = [
            {
                "filename": f["path"],
                "size_mb": round(f.get("size", 0) / (1024 * 1024), 2),
                "url": f"https://huggingface.co/datasets/{DATASET_REPO}/resolve/main/{f['path']}"
            }
            for f in files if f.get("type") == "file" and not f["path"].startswith(".")
        ]
        
        return JSONResponse(content={
            "hf_galpao": video_files,
            "status": "online"
        })
        
    except Exception as e:
        logger.error(f"[Broadcaster Admin] Erro ao ler inventario do HF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro de conexao com o Galpao HF Conta 2: {str(e)}")

@router.get("/oracle-status")
async def get_oracle_status(admin: str = Depends(verify_admin)):
    """ Retorna mocks do status da Oracle (Será preenchido pelo script downloader) """
    return JSONResponse(content={
        "oracle_hd_used_gb": "0.0",
        "current_video": "Nenhum",
        "is_broadcasting": False
    })

