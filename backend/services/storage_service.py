import logging
import os
import uuid
import asyncio

logger = logging.getLogger("StorageService")

class StorageService:
    def __init__(self):
        # Configurações simuladas de S3 / R2
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "apollo-videos")
        self.cdn_url = os.getenv("CDN_URL", "https://cdn.apollo.com")
        self.use_mock = True # Em produção mudamos para False

    async def upload_video(self, local_filepath: str, user_id: str) -> str:
        """
        Simula o upload de um vídeo MP4 para a nuvem.
        Retorna a URL pública (CDN) do vídeo.
        """
        if not os.path.exists(local_filepath):
            logger.error(f"[Storage] Arquivo não encontrado: {local_filepath}")
            raise FileNotFoundError(f"Arquivo não existe: {local_filepath}")
            
        filename = os.path.basename(local_filepath)
        unique_id = uuid.uuid4().hex[:8]
        object_name = f"{user_id}/{unique_id}_{filename}"
        
        logger.info(f"[Storage] Iniciando upload do vídeo '{object_name}' para o bucket '{self.bucket_name}'...")
        
        # Simula tempo de upload (Network I/O)
        await asyncio.sleep(2) 
        
        if self.use_mock:
            public_url = f"{self.cdn_url}/{object_name}"
            logger.info(f"[Storage] Upload concluído (Mock)! URL: {public_url}")
            return public_url
        else:
            # Implementação real boto3.client('s3').upload_file(...) iria aqui
            pass
            return ""

storage_service = StorageService()
