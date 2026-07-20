import os
import json
import time
from typing import Dict, Any, List
from config_manager import ConfigManager
import google.generativeai as genai

class ChatAIManager:
    """Gerenciador de Inteligência Artificial usando Gemini com Memória de Chat e Functions."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.api_key = self.config.get("api_config.gemini.api_key")
        self.api_keys_list = self.config.get("api_config.gemini.api_keys", [])
        
        if not self.api_key and self.api_keys_list:
            self.api_key = self.api_keys_list[0].get("key")
            
        if self.api_key:
            genai.configure(api_key=self.api_key)
        
        self.model_name = self.config.get("api_config.gemini.model", "gemini-2.5-flash")
        
        # Diretório para salvar os cachês de chat
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache_chats")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Modelos carregados na memória
        self.active_chats = {}
        
        # Sistema de prompts por canal
        self.system_prompts = {
            "diretor_central": """Você é o Diretor Central da Plataforma Apollo Edit Web.
Você interage com o usuário para entender o projeto dele. 
SE O USUÁRIO FORNECER O CONTEXTO PARA O PROJETO E INFORMAR A DURAÇÃO E FORMATO (EX: 1 MINUTO VERTICAL), VOCÊ DEVE CRIAR UM ORÇAMENTO.
Para isso, você PODE usar ações de UI enviando comandos JSON na sua resposta (sem quebrar o diálogo).
Se você quiser criar um orçamento na interface, adicione ao final da sua resposta o seguinte JSON dentro de um bloco de código `json_action`:
```json_action
{
  "action": "create_budget",
  "budget_data": {
    "slot_roteiro": 10,
    "slot_arte": 10,
    "slot_voz": 15
  }
}
```
Lembre-se: não exiba esse json bruto para o usuário fora do bloco json_action. Seja direto e muito carismático.""",
            "mini_roteirista": "Você é um roteirista profissional. Escreva os roteiros e seja direto. Sempre responda com roteiros excelentes.",
            "agente_financeiro": "Você é o Agente Financeiro da plataforma Apollo. Sua função é receber dados de receita e custos, e emitir um breve diagnóstico em 1 parágrafo focado na lucratividade e na eficiência das APIs. Se a lucratividade estiver ruim, recomende pausar algumas chaves."
        }

    def _get_history_file(self, channel_id: str) -> str:
        # Sanitizar nome
        clean_name = "".join(c for c in channel_id if c.isalnum() or c in ('_', '-'))
        return os.path.join(self.cache_dir, f"history_{clean_name}.json")

    def load_history(self, channel_id: str) -> List[Dict]:
        path = self._get_history_file(channel_id)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self, channel_id: str, history: List[Dict]):
        path = self._get_history_file(channel_id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def send_message(self, channel_id: str, message: str) -> Dict[str, Any]:
        """
        Envia uma mensagem para um canal específico, mantendo contexto e salvando em cache.
        Sistema de Roteamento em 3 Camadas (Trindade Arquitetural):
        1. TIER 1 (Principal): Contas Lightning AI (vLLM / Llama)
        2. TIER 2 (Fallback 1): Chaves Gemini Gratuitas
        3. TIER 3 (Fallback 2): Chaves OpenRouter (Pagos)
        """
        system_prompt = self.system_prompts.get(channel_id, "Você é um assistente prestativo da plataforma Apollo Edit Web.")
        raw_history = self.load_history(channel_id)
        
        import random
        import requests
        import re
        
        # ------------------------------------------------------------------
        # TIER 1: LIGHTNING AI (FOCO PRINCIPAL)
        # ------------------------------------------------------------------
        print(f"[Gateway LLM] Iniciando roteamento. Buscando contas Lightning...")
        try:
            from backend.cloud_tools import account_manager
            cloud_accounts = account_manager.load_accounts()
            # Pega as contas lightning ativas, com saldo positivo, e que têm a URL salva no workspace
            lightning_accounts = [
                acc for acc in cloud_accounts 
                if acc.get("provider") == "lightning" 
                and acc.get("is_active") 
                and float(acc.get("last_balance", 0)) > 0
                and acc.get("workspace")
            ]
        except Exception as e:
            print(f"[Gateway LLM] Erro ao ler banco de nuvem: {e}")
            lightning_accounts = []
            
        random.shuffle(lightning_accounts)
        
        last_error_lightning = ""
        lightning_success = False
        text_response = ""
        
        for acc in lightning_accounts:
            # A URL do workspace deve ser a URL completa da porta 8000 (ex: https://8000-roxingo-xxxx.projects.lightning.ai)
            base_url = acc.get("workspace").rstrip('/')
            url = f"{base_url}/api/v1/chat/completions"
            
            # Formata histórico no padrão OpenAI para nosso servidor FastAPI Lightning
            lt_history = [{"role": "system", "content": system_prompt}]
            for msg in raw_history:
                lt_history.append({"role": msg["role"], "content": msg["content"]})
            lt_history.append({"role": "user", "content": message})
            
            payload = {
                "messages": lt_history,
                "max_tokens": 2048,
                "temperature": 0.7
            }
            
            print(f"  -> Tentando Cérebro Lightning: {base_url[:30]}...")
            try:
                # Timeout de conexão curto (5s) para pular rápido se a máquina estiver desligada
                resp = requests.post(url, json=payload, timeout=(5, 120))
                if resp.status_code == 200:
                    data = resp.json()
                    text_response = data["choices"][0]["message"]["content"]
                    lightning_success = True
                    print(f"  [OK] Sucesso no motor Lightning!")
                    break
                else:
                    last_error_lightning = f"Erro HTTP {resp.status_code}: {resp.text}"
            except Exception as e:
                last_error_lightning = str(e)
                print(f"  [X] Maquina Offline ou Inacessivel.")
                continue

        # Processa a resposta se o Lightning deu certo, e retorna
        if lightning_success:
            # Deduz um pequeno custo estimado da conta Lightning ativa
            try:
                from backend.cloud_tools import account_manager
                account_manager.deduct_balance(acc["id"], 0.005)
            except Exception as e:
                print(f"[Gateway LLM] Erro ao deduzir saldo Lightning: {e}")
                
            raw_history.append({"role": "user", "content": message})
            raw_history.append({"role": "model", "content": text_response})
            self.save_history(channel_id, raw_history)
            
            actions = []
            action_blocks = re.findall(r'```json_action\n(.*?)\n```', text_response, re.DOTALL)
            for block in action_blocks:
                try: actions.append(json.loads(block))
                except: pass
                    
            clean_text = re.sub(r'```json_action\n.*?\n```', '', text_response, flags=re.DOTALL).strip()
            return {"text": clean_text, "actions": actions}
            
            
        # ------------------------------------------------------------------
        # TIER 2: GEMINI (FALLBACK 1)
        # ------------------------------------------------------------------
        print(f"[Gateway LLM] Lightning indisponível (Erro: {last_error_lightning}). Tentando Fallback 1: Gemini...")
        
        all_keys = self.config.get("api_config.gemini.api_keys", [])
        active_keys = [k for k in all_keys if k.get("status", "active") != "exhausted"]
        if not active_keys and self.api_key:
             active_keys = [{"key": self.api_key, "status": "active"}]
             
        history_gemini = []
        for msg in raw_history:
            history_gemini.append({"role": msg["role"], "parts": [msg["content"]]})
            
        random.shuffle(active_keys)
        last_error_gemini = ""
        
        for key_obj in active_keys:
            current_key = key_obj.get("key")
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel(model_name=self.model_name, system_instruction=system_prompt)
            try:
                chat = model.start_chat(history=history_gemini)
                response = chat.send_message(message)
                
                new_history = []
                for h in chat.history:
                    role = "user" if h.role == "user" else "model"
                    part_text = h.parts[0].text if len(h.parts) > 0 else ""
                    new_history.append({"role": role, "content": part_text})
                    
                self.save_history(channel_id, new_history)
                self.config.update_api_key_spend("gemini", current_key, 0.005)
                text_response = response.text
                
                actions = []
                action_blocks = re.findall(r'```json_action\n(.*?)\n```', text_response, re.DOTALL)
                for block in action_blocks:
                    try: actions.append(json.loads(block))
                    except: pass
                clean_text = re.sub(r'```json_action\n.*?\n```', '', text_response, flags=re.DOTALL).strip()
                return {"text": "[FALLBACK GEMINI] " + clean_text, "actions": actions}
                
            except Exception as e:
                err_msg = str(e).lower()
                print(f"[Gemini] Falha na chave {current_key[:6]}... Erro: {err_msg}")
                if "429" in err_msg or "quota" in err_msg or "402" in err_msg or "exhausted" in err_msg or "payment" in err_msg or "billing" in err_msg:
                    self.config.mark_api_key_exhausted("gemini", current_key)
                last_error_gemini = str(e)
                continue

        # ------------------------------------------------------------------
        # TIER 3: OPENROUTER (FALLBACK SUPREMO)
        # ------------------------------------------------------------------
        print(f"[Gateway LLM] Gemini indisponível. Tentando Fallback 2: OpenRouter...")
        openrouter_keys = self.config.get("api_config.openrouter.api_keys", [])
        active_or_keys = [k for k in openrouter_keys if k.get("status", "active") != "exhausted"]
        
        if not active_or_keys:
            return {
                "text": f"⚠️ Colapso Sistêmico das IAs. Lightning, Gemini e OpenRouter falharam. (Erros L={last_error_lightning} | G={last_error_gemini}). Configure novas chaves.",
                "actions": []
            }
            
        random.shuffle(active_or_keys)
        
        or_history = [{"role": "system", "content": system_prompt}]
        for msg in raw_history:
            or_history.append({"role": msg["role"], "content": msg["content"]})
        or_history.append({"role": "user", "content": message})
        
        last_error_or = ""
        for key_obj in active_or_keys:
            current_or_key = key_obj.get("key")
            try:
                headers = {
                    "Authorization": f"Bearer {current_or_key}",
                    "HTTP-Referer": "https://apollo-edit.web",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "google/gemini-2.5-flash-1m", 
                    "messages": or_history
                }
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    text_response = data["choices"][0]["message"]["content"]
                    
                    raw_history.append({"role": "user", "content": message})
                    raw_history.append({"role": "model", "content": text_response})
                    self.save_history(channel_id, raw_history)
                    self.config.update_api_key_spend("openrouter", current_or_key, 0.005)
                    
                    actions = []
                    action_blocks = re.findall(r'```json_action\n(.*?)\n```', text_response, re.DOTALL)
                    for block in action_blocks:
                        try: actions.append(json.loads(block))
                        except: pass
                            
                    clean_text = re.sub(r'```json_action\n.*?\n```', '', text_response, flags=re.DOTALL).strip()
                    return {"text": "[FALLBACK SUPREMO TIER 3] " + clean_text, "actions": actions}
                else:
                    err_msg = str(resp.text).lower()
                    if "402" in err_msg or "quota" in err_msg or "payment" in err_msg:
                        self.config.mark_api_key_exhausted("openrouter", current_or_key)
                    last_error_or = err_msg
            except Exception as e:
                last_error_or = str(e)
                
        return {
            "text": f"Ocorreu um erro crônico na Trindade das IAs. Nenhuma IA respondeu. Último erro OpenRouter: {last_error_or}",
            "actions": []
        }

    def clear_memory(self, channel_id: str):
        path = self._get_history_file(channel_id)
        if os.path.exists(path):
            os.remove(path)
