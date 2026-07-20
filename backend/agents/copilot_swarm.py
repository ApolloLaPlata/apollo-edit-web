import os
import json
import time
import requests
import asyncio
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# Configuracao da API Groq
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

class CopilotAgent:
    def __init__(self, name: str, system_prompt: str, user_id: str = "default_user"):
        self.name = name
        self.system_prompt = system_prompt
        self.user_id = user_id
        self.status = "IDLE"
        self.mission_id = f"mission_{int(time.time())}"
        self.logs = []
        
    def _log(self, msg: str):
        stamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{stamp}] [{self.name}] {msg}"
        print(entry)
        self.logs.append(entry)
        
    def _ask_llm_json(self, prompt: str) -> dict:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        full_system = f"{self.system_prompt}\nVocê DEVE responder exclusivamente em formato JSON com o seguinte schema:\n"
        full_system += """{
            "title": "Titulo do Video",
            "voiceover_script": "Texto corrido para narracao",
            "scenes": [
                {"visual_prompt": "prompt visual detalhado para o gerador de imagem/video", "duration": 5}
            ]
        }"""
        
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": full_system},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        
        self._log("Processando raciocínio com Llama 3 70B (Groq)...")
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def run_mission(self, topic: str):
        """ Inicia a missão principal do Agente """
        self.status = "PLANNING"
        self._log(f"Iniciando Missão: Tema '{topic}'")
        
        # 1. Roteirização
        try:
            script_json = self._ask_llm_json(f"Crie um roteiro altamente engajante e viral sobre o tema: {topic}")
            script_data = json.loads(script_json)
        except Exception as e:
            self._log(f"Falha na Roteirização: {e}")
            self.status = "FAILED"
            return
            
        title = script_data.get("title", "Video")
        scenes = script_data.get("scenes", [])
        self._log(f"Roteiro finalizado: '{title}' com {len(scenes)} cenas planejadas.")
        
        # 2. Execução (Compra de Mídias via API local)
        self.status = "EXECUTING"
        generated_job_ids = []
        
        for idx, scene in enumerate(scenes):
            v_prompt = scene.get("visual_prompt")
            self._log(f"Comprando geração para Cena {idx+1}: {v_prompt[:30]}...")
            
            # Chama a própria API do servidor
            local_url = "http://127.0.0.1:8000/api/studio/generate"
            payload = {
                "type": "video", # Vamos gerar videos diretos por padrão
                "prompt": v_prompt,
                "model": "wan2.1",
                "aspect_ratio": "16:9",
                "cfg_scale": 7.0,
                "steps": 25,
                "motion_scale": 5.0,
                "negative_prompt": "ugly, low quality, distorted"
            }
            
            try:
                r = requests.post(local_url, json=payload, timeout=10)
                res_data = r.json()
                if res_data.get("success"):
                    j_id = res_data.get("job_id")
                    self._log(f"Cena {idx+1} enviada para Modal Cloud. Job: {j_id}")
                    generated_job_ids.append(j_id)
                else:
                    err = res_data.get("error", "Erro desconhecido")
                    self._log(f"Falha ao comprar Cena {idx+1}: {err}")
                    if "Saldo Insuficiente" in err:
                        self._log("O Agente declarou falência. Missão abortada por falta de fundos.")
                        self.status = "BANKRUPT"
                        return
            except Exception as e:
                self._log(f"Erro de conexão com Estúdio: {e}")
                
            # Evita sobrecarregar o endpoint local num burst só
            time.sleep(2)
            
        self.status = "COMPLETED"
        self._log("Todas as cenas despachadas. O Agente encerrou a missão de compra.")
        return generated_job_ids
