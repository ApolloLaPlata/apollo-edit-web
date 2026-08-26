from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import requests
import json
import uuid

router = APIRouter()

# O Roteador Zero-Config do Áudio (AGORA USANDO LIGHTNING AI INTERNO - ZERO CUSTO)
@router.post("/api/audio/smart_generate")
async def smart_generate_audio(req: Request, background_tasks: BackgroundTasks):
    data = await req.json()
    user_prompt = data.get("prompt", "")
    
    if not user_prompt:
        return JSONResponse({"error": "Prompt não fornecido"}, status_code=400)
        
    system_prompt = '''You are an expert Audio Intent Router for Apollo Edit Web.
    The user will provide a text prompt requesting some form of audio generation.
    Your job is to classify the intent and route it to the correct AI engine.
    
    ENGINES AVAILABLE:
    1. "sa3" (Stable Audio 3 Medium): Use for instrumentals, trap beats, cinematic scores, sound effects (SFX), background music, and any music WITHOUT vocals.
    2. "minimax": Use for pure voice generation, speech, narration, voice cloning, or monologue.
    3. "ace-step": Use for FULL songs WITH vocals, lyrics, and instruments (e.g., "Faça um rap cantado sobre...", "Uma música pop com letra").
    
    RETURN STRICTLY A JSON OBJECT (no markdown, no extra text):
    {
        "engine": "sa3" | "minimax" | "ace-step",
        "optimized_prompt": "An optimized version of the prompt translated to English (for sa3/ace) or kept in original language for minimax",
        "parameters": {
            "duration": 30
        }
    }'''

    try:
        # CHAMA O LIGHTNING AI PROXY INTERNO (SEM CUSTO DE API EXTERNA)
        proxy_url = "http://127.0.0.1:8080/api/lightning_proxy"
        
        response = requests.post(proxy_url, json={
            # Pode usar o modelo padrão que está configurado no seu Lightning
            "model": "nvidia-nemotron-3-ultra-550b-a55b", 
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }, timeout=30)
        
        if response.status_code == 200:
            data_resp = response.json()
            result_text = data_resp.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Limpar possiveis markdowns
            result_text = result_text.replace("" + "" + "json", "").replace("" + "" + "", "").strip()
            decision = json.loads(result_text)
            
            engine = decision.get("engine")
            optimized_prompt = decision.get("optimized_prompt")
            
            job_id = f"job_smart_audio_{uuid.uuid4().hex[:8]}"
            
            # (A LÓGICA DE WORKER ENTRARÁ AQUI PARA ACORDAR O MODAL)
            
            return JSONResponse({
                "success": True,
                "job_id": job_id,
                "router_decision": decision,
                "message": f"Áudio roteado com sucesso para o motor {engine.upper()} via Lightning AI!"
            })
        else:
             return JSONResponse({"error": "Falha na comunicação com o Lightning Proxy"}, status_code=500)
             
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
