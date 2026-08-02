from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import RedirectResponse
import os
import uuid
from backend.services.storage_gateway.router import StorageRouter

router = APIRouter(prefix="/media", tags=["Storage Gateway"])
storage_router = StorageRouter()

# Mock DB Lookup (This vai ser trocado pelo client do Supabase real)
def get_media_record(media_id: str):
    # TODO: Implement Supabase fetch from `media_storage_map` table
    # return {"provider": "cloudflare_r2", "provider_url": "r2://apollo-media/file.jpg"}
    return None

def save_media_record(media_id: str, provider: str, provider_url: str, type: str, ttl_status: str):
    # TODO: Implement Supabase insert into `media_storage_map` table
    pass

@router.get("/{media_id}")
async def redirect_media(media_id: str):
    """
    Abstract Storage Gateway Redirect.
    The frontend calls this URL. The backend looks up the real location of the file in the database
    and redirects the client via HTTP 302 to the actual zero-cost CDN provider (Cloudflare, Telegram, etc).
    """
    record = get_media_record(media_id)
    
    if not record:
        return {"error": "Media not found or not mapped yet."}
    
    provider_name = record.get("provider")
    provider_url = record.get("provider_url")
    
    if not provider_name or not provider_url:
        raise HTTPException(status_code=500, detail="Database record incomplete.")
    
    try:
        public_url = storage_router.get_public_redirect_url(provider_name, provider_url)
        # 302 Redirect to the actual provider CDN
        return RedirectResponse(url=public_url, status_code=302)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_media_abstract(file: UploadFile = File(...), ttl_status: str = "bagagem"):
    """
    Abstract Upload Endpoint.
    Envia o arquivo para o Gateway. Ele decide (via FinOps) onde hospedar,
    faz o upload e registra no banco.
    """
    file_bytes = await file.read()
    content_type = file.content_type or "application/octet-stream"
    
    # Gera UUID seguro
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    media_id = f"med_{uuid.uuid4().hex}{ext}"
    
    try:
        # Envia para a Inteligência de Roteamento
        result = await storage_router.upload_inteligente(file_bytes, media_id, content_type)
        
        provider_name = result["provider"]
        provider_url = result["provider_url"]
        
        # Define o tipo
        media_type = "video" if "video" in content_type else "image"
        
        # Registra no DB
        save_media_record(media_id, provider_name, provider_url, media_type, ttl_status)
        
        return {
            "status": "success",
            "media_id": media_id,
            "abstract_url": f"/media/{media_id}",
            "provider_used": provider_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
