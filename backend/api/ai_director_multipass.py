import os
import sys
import base64
import requests
import json
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional

# Adicionar backend ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.api.lightning_client import LightningClient

class AIDirectorMultipass:
    def __init__(self, api_key: str, modal_base_url: str):
        self.client = LightningClient(api_key=api_key)
        self.modal_base_url = modal_base_url
        self.system_prompt = """You are an expert AI image generation prompt engineer.
Your task is to take a base scene and a list of characters, and construct a highly detailed, perfectly composed prompt for FLUX.1.
To prevent character distortion, you MUST explicitly describe where each character is placed and isolate their physical descriptions.
Return ONLY the final prompt in English."""

    def break_down_prompt(self, global_prompt: str, characters: List[dict]) -> tuple[str, List[str]]:
        current_prompt = f"Base Scenario: {global_prompt}\nCreate an initial highly detailed, photorealistic prompt for FLUX.1. Do not add any characters yet, just the environment."
        base_prompt = self.client.generate_text(prompt=current_prompt, system_prompt=self.system_prompt, model="openai/gpt-4o")
        
        regional_prompts = []
        final_flux_prompt = base_prompt
        
        for char in characters:
            iterative_prompt = f"Current Scene Prompt:\n{final_flux_prompt}\n\nNow, integrate the following new character naturally, WITHOUT altering the fundamental lighting, and WITHOUT blending features. Ensure spatial isolation.\nNew Character: {char.get('name', 'Unknown')}\nDescription: {char.get('details', '')}\nRewrite the full prompt to include this new character seamlessly."
            
            final_flux_prompt = self.client.generate_text(prompt=iterative_prompt, system_prompt=self.system_prompt, model="openai/gpt-4o")
            regional_prompts.append(final_flux_prompt)
            
        return base_prompt, regional_prompts

    def generate_base_image(self, base_prompt: str, seed: int = 42) -> str:
        payload = {
            "prompt": base_prompt,
            "model": "flux2-universal",
            "format": "horizontal",
            "seed": seed
        }
        resp = requests.post(f"{self.modal_base_url}/generate/image", json=payload)
        if resp.status_code != 200:
            raise Exception(f"Erro Base Image: {resp.text}")
            
        for line in resp.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                if data.get("status") == "success":
                    return data.get("image_base64")
        raise Exception("Nenhum base64 retornado para a imagem base.")

    def run_multipass(self, workflow, base_prompt: str, regional_prompts: List[str], base_img_b64: str, character_images_b64: List[str], seed: int = 42) -> str:
        if isinstance(workflow, str):
            with open(workflow, "r") as f:
                workflow_data = json.load(f)
        else:
            workflow_data = workflow
            
        payload = {
            "workflow": workflow_data,
            "base_prompt": base_prompt,
            "regional_prompts": regional_prompts,
            "input_images_b64": [base_img_b64] + character_images_b64,
            "seed": seed
        }
        
        resp = requests.post(f"{self.modal_base_url}/generate/multipass", json=payload)
        if resp.status_code != 200:
            raise Exception(f"Erro no Multipass: {resp.text}")
            
        for line in resp.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                if data.get("status") == "success":
                    return data.get("image_base64")
                elif data.get("status") == "error":
                    raise Exception(f"Modal retornou erro: {data}")
                    
        raise Exception("Nenhum resultado retornado pelo Multipass.")

    def orchestrate(self, global_prompt: str, characters: List[dict], character_images_b64: List[str], workflow_path: str) -> str:
        # 1. Planejamento (LLM)
        print("[AIDirectorMultipass] Planejando etapas...")
        base_prompt, regional_prompts = self.break_down_prompt(global_prompt, characters)
        
        # 2. Gerar Base
        print("[AIDirectorMultipass] Gerando cenario base...")
        base_img_b64 = self.generate_base_image(base_prompt)
        
        # 3. Multipass
        print(f"[AIDirectorMultipass] Iniciando Inpaint Sequencial para {len(characters)} personagens...")
        final_b64 = self.run_multipass(workflow_path, base_prompt, regional_prompts, base_img_b64, character_images_b64)
        print("[AIDirectorMultipass] Concluido com sucesso!")
        
        return final_b64
