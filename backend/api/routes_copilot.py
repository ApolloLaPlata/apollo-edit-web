import os
import requests
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Copiloto"])

class ChatRequest(BaseModel):
    message: str
    timeline: Dict[str, Any]
    history: Optional[List[Dict[str, str]]] = None

class BrollRequest(BaseModel):
    prompt: str

@router.post("/api/chat_copilot")
def api_chat_copilot(req: ChatRequest):
    try:
        logging.info(f"Copilot Msg: {req.message}")
        # Build prompt for LLM
        prompt = f'''
        Voce e o Copiloto de Edicao do Apollo Edit. O usuario te pediu: "{req.message}"
        Aqui esta o estado da timeline (clipes atuais): {req.timeline}
        Retorne um JSON estrito contendo:
        {{
            "message": "Mensagem amigavel de confirmacao",
            "operations": [
                // se pediu para cortar algo, insira a operacao de corte
            ]
        }}
        Mantenha as operacoes compativeis com o timeline.js
        '''
        
        # Chama a API Central da V5 Apollo Holding
        resp = requests.post("https://api.v5apollo.com/api/generate/llm", json={
            "prompt": prompt,
            "provider": "gemini" # ou openai, etc
        }, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            # The central API returns the generated text in 'text' or 'response'
            ai_text = data.get('text', data.get('response', '{"message": "Ok, entendi!", "operations": []}'))
            
            import json, re
            # Extract JSON block
            json_str = re.sub(r'`(?:json)?\s*|\s*`', '', ai_text).strip()
            try:
                parsed = json.loads(json_str)
                return {"status": "success", "response": parsed}
            except:
                return {"status": "success", "response": {"message": ai_text, "operations": []}}
        else:
            return {"status": "success", "response": {"message": "Simulacao (API Central offline): Comando recebido.", "operations": []}}

    except Exception as e:
        logging.error(f"Erro no chat_copilot: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/api/generate_broll")
def api_generate_broll(req: BrollRequest):
    try:
        logging.info(f"Copilot Broll: {req.prompt}")
        
        # Chama a API Central para Imagem
        resp = requests.post("https://api.v5apollo.com/api/generate/multi_pass", json={
            "script": {
                "etapas": [{"prompt": req.prompt, "tipo": "base_generation"}]
            }
        }, timeout=60)
        
        if resp.status_code == 200:
            data = resp.json()
            if data and data.get("image_base64"):
                # Save base64 to local media folder
                import base64
                import uuid
                img_data = base64.b64decode(data["image_base64"])
                filename = f"broll_{uuid.uuid4().hex[:8]}.jpg"
                filepath = os.path.join("media", filename)
                os.makedirs("media", exist_ok=True)
                with open(filepath, "wb") as f:
                    f.write(img_data)
                
                return {"status": "success", "image_path": f"/media/{filename}"}
                
        # Fallback if Central is not returning image yet
        return {"status": "success", "image_path": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=1200"}
        
    except Exception as e:
        logging.error(f"Erro no generate_broll: {e}")
        return {"status": "error", "message": str(e)}