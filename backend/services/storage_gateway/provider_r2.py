import boto3
import os
from typing import Dict, Any
from botocore.exceptions import ClientError
from .base_provider import StorageProvider

class CloudflareR2Provider(StorageProvider):
    def __init__(self):
        # As credenciais deverão vir das variaveis de ambiente
        self.account_id = os.environ.get("R2_ACCOUNT_ID", "mock-account-id")
        self.access_key = os.environ.get("R2_ACCESS_KEY_ID", "mock_key")
        self.secret_key = os.environ.get("R2_SECRET_ACCESS_KEY", "mock_secret")
        self.bucket_name = os.environ.get("R2_BUCKET_NAME", "apollo-media")
        
        self.s3_client = boto3.client(
            service_name="s3",
            endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="auto" # Cloudflare R2 usa 'auto'
        )

    def get_provider_name(self) -> str:
        return "cloudflare_r2"

    async def put_object(self, file_bytes: bytes, file_name: str, content_type: str) -> str:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_bytes,
                ContentType=content_type,
                CacheControl="public, max-age=31536000"
            )
            # Retorna o identificador interno
            return f"r2://{self.bucket_name}/{file_name}"
        except ClientError as e:
            print(f"Erro no Cloudflare R2 Upload: {e}")
            raise e

    def get_public_url(self, file_id_or_url: str) -> str:
        # A URL pública real vai depender de como o Cloudflare Pages/Worker está configurado.
        # Exemplo: https://cdn.apolloedit.com/file_name
        file_name = file_id_or_url.split("/")[-1]
        custom_domain = os.environ.get("R2_PUBLIC_DOMAIN", "https://cdn.mock-apolloedit.com")
        return f"{custom_domain}/{file_name}"

    async def get_quota_state(self) -> Dict[str, Any]:
        # A API de métricas do Cloudflare é via GraphQL, para simplicidade retornamos mock.
        # R2 tem limite de 10GB free.
        return {
            "storage_used_bytes": 0, # Implementar consulta real
            "storage_limit_bytes": 10 * 1024 * 1024 * 1024, # 10 GB
            "egress_limit_bytes": -1 # -1 significa ilimitado
        }

    async def delete_object(self, file_id_or_url: str) -> bool:
        file_name = file_id_or_url.split("/")[-1]
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_name)
            return True
        except ClientError:
            return False
