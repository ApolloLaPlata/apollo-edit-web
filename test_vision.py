import sys
import os
import json
import asyncio
import httpx
from unittest.mock import AsyncMock

# Vamos simular um request para routes_studio.py
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from backend.api.routes_studio import proxy_to_modal

class MockRequest:
    def __init__(self, json_data):
        self.method = "POST"
        self._json = json_data
        self.headers = {
            "content-type": "application/json",
            "x-apollo-lock": os.environ.get("APOLLO_SECRET_LOCK", "apollo-beta-key-2026")
        }
    
    async def body(self):
        return json.dumps(self._json).encode("utf-8")

async def test():
    print("[TEST] Criando Mock Request...")
    # 2 imagens pequenas em base64 falso para simular
    fake_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    
    req_data = {
        "model": "qwen-image",
        "prompt": "Create an awesome cinematic scene with two people",
        "reference_images_base64": [fake_b64, fake_b64]
    }
    
    request = MockRequest(req_data)
    
    print("[TEST] Acionando proxy_to_modal...")
    try:
        class MockTasks:
            def add_task(self, *args, **kwargs): pass
            
        await proxy_to_modal("generate_image", request, MockTasks())
    except Exception as e:
        print(f"[TEST FINISHED/ABORTED] {e}")

if __name__ == "__main__":
    asyncio.run(test())
