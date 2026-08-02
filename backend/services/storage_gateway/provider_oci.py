import boto3
import os
from typing import Dict, Any
from botocore.exceptions import ClientError
from .base_provider import StorageProvider

class OracleOCIProvider(StorageProvider):
    def __init__(self):
        # As credenciais deverão vir das variaveis de ambiente
        self.namespace = os.environ.get("OCI_NAMESPACE", "mock-namespace")
        self.region = os.environ.get("OCI_REGION", "sa-saopaulo-1")
        self.access_key = os.environ.get("OCI_ACCESS_KEY_ID", "mock_key")
        self.secret_key = os.environ.get("OCI_SECRET_ACCESS_KEY", "mock_secret")
        self.bucket_name = os.environ.get("OCI_BUCKET_NAME", "apollo-videos")
        
        # Oracle suporta S3 Compatibility API
        endpoint_url = f"https://{self.namespace}.compat.objectstorage.{self.region}.oraclecloud.com"
        
        self.s3_client = boto3.client(
            service_name="s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )

    def get_provider_name(self) -> str:
        return "oracle_oci"

    async def put_object(self, file_bytes: bytes, file_name: str, content_type: str) -> str:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_bytes,
                ContentType=content_type,
                CacheControl="public, max-age=31536000"
            )
            return f"oci://{self.bucket_name}/{file_name}"
        except ClientError as e:
            print(f"Erro no Oracle OCI Upload: {e}")
            raise e

    def get_public_url(self, file_id_or_url: str) -> str:
        # A URL publica gerada pela Oracle ou um Custom Domain
        file_name = file_id_or_url.split("/")[-1]
        custom_domain = os.environ.get("OCI_PUBLIC_DOMAIN", f"https://objectstorage.{self.region}.oraclecloud.com/n/{self.namespace}/b/{self.bucket_name}/o")
        return f"{custom_domain}/{file_name}"

    async def get_quota_state(self) -> Dict[str, Any]:
        return {
            "storage_used_bytes": 0, 
            "storage_limit_bytes": 10 * 1024 * 1024 * 1024, # 10 GB Free
            "egress_limit_bytes": 10 * 1024 * 1024 * 1024 * 1024 # 10 TB Egress Free
        }

    async def delete_object(self, file_id_or_url: str) -> bool:
        file_name = file_id_or_url.split("/")[-1]
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_name)
            return True
        except ClientError:
            return False
