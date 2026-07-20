import json
import base64
import logging
import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from openai import OpenAI

logger = logging.getLogger("AIDirector")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger.setLevel(logging.INFO)

app = FastAPI(title="Apollo AI Director API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerationRequest(BaseModel):
    global_prompt: str
    images_b64: List[str]
    api_key: str = None

class AIDirector:
    def __init__(self, endpoint_url: str = None, model_name: str = "openai/gpt-4o-mini"):
        self.endpoint_url = endpoint_url or "https://openrouter.ai/api/v1"
        self.model_name = model_name

    def analyze_and_script(self, global_prompt: str, images_b64: List[str], api_key: str) -> Dict[str, Any]:
        logger.info(f"[AIDirector] Analisando {len(images_b64)} imagens para o prompt: '{global_prompt}'")
        
        if not api_key:
            raise ValueError("OpenRouter API Key not provided.")

        client = OpenAI(
            base_url=self.endpoint_url,
            api_key=api_key,
        )
        
        # Build the message content with images
        content = [
            {"type": "text", "text": f"You are a movie director. The user wants to generate an image with this prompt: '{global_prompt}'. I am attaching {len(images_b64)} images of characters. You must assign each character a description, and return a JSON array containing the accumulative steps to generate them one by one. The JSON format must be strictly: {{\"etapas\": [{{\"character_id\": 1, \"character_description\": \"description\", \"prompt\": \"accumulative prompt\"}}]}}. Start with character 1, then character 1 and 2, etc."}
        ]
        
        for img_b64 in images_b64:
            # Assumes base64 string includes 'data:image/jpeg;base64,' prefix. If not, we might need to add it, but OpenRouter usually handles URLs.
            # We'll construct standard data URIs if they are raw.
            if not img_b64.startswith("data:"):
                img_b64 = f"data:image/jpeg;base64,{img_b64}"
            
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": img_b64
                }
            })

        logger.info("[AIDirector] Chamando OpenRouter API (Qwen-VL)...")
        
        try:
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            
            result_text = completion.choices[0].message.content
            logger.info(f"[AIDirector] Resposta do LLM: {result_text}")
            
            # Extract JSON from the text
            # A very simple extraction (assumes LLM outputs valid JSON block)
            start_idx = result_text.find("{")
            end_idx = result_text.rfind("}")
            if start_idx != -1 and end_idx != -1:
                json_str = result_text[start_idx:end_idx+1]
                etapas_data = json.loads(json_str)
            else:
                raise ValueError("Nenhum JSON encontrado na resposta do LLM")
            
            # Mix the image references back into the array
            etapas = etapas_data.get("etapas", [])
            for i, etapa in enumerate(etapas):
                if i < len(images_b64):
                    etapa["image_b64"] = images_b64[i]
                    
            return {
                "status": "success",
                "global_prompt": global_prompt,
                "etapas": etapas
            }
            
        except Exception as e:
            logger.error(f"[AIDirector] Erro na API OpenRouter: {e}")
            raise e

director = AIDirector()

@app.post("/api/generate")
async def generate_multipass(req: GenerationRequest):
    try:
        # 1. AI Director analisa o roteiro
        script = director.analyze_and_script(req.global_prompt, req.images_b64, req.api_key)
        
        # 2. Chama a engine do Modal
        import modal
        cls = modal.Cls.from_name("apollo-render-router", "UniversalComfyEngine")
        engine = cls()
        
        # Load the base KLEIN workflow (which the engine needs)
        # We need a default workflow JSON for the engine to execute. 
        # For now, we will pass a placeholder string or attempt to load from a file if it exists.
        workflow_json_string = "{}"
        workflow_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/FLUX.2 [KLEIN] 4B/FLUX.2 [KLEIN] 4B Edição de imagem/workflow_multipass_klein.json"
        if os.path.exists(workflow_path):
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_json_string = f.read()
                
        script["workflow_json_string"] = workflow_json_string
        
        logger.info("[AIDirector] Chamando Universal Engine no Modal...")
        result = await engine.multi_pass_generation.remote.aio(script)
        
        if result.get("status") == "success":
            return {"status": "success", "image_b64": result.get("image_base64")}
        else:
            raise HTTPException(status_code=500, detail=result.get("message"))
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        logger.error(f"[AIDirector] Erro no Modal: {err}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Iniciando AI Director API na porta 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
