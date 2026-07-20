import os
import json
from typing import Optional
from config_manager import ConfigManager
from gemini_api import GeminiAPI
from openai_compatible_api import OpenAICompatibleAPI

# MODO DE STRESS TEST: 
# Se True, desativa o Gemini completamente (para todos) e força o uso do Groq/OpenRouter.
FORCE_DISABLE_GEMINI = True

class LLMCascade:
    """Gerencia o fallback entre múltiplas APIs de LLM."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        
        # O Plano A é sempre o Gemini
        self.gemini = GeminiAPI(config_manager)
        
        # Inicializa as APIs Secundárias buscando chaves no admin_config.json
        self.fallbacks = []
        self._load_fallbacks()

    def _load_fallbacks(self):
        # Carrega admin_config.json para pegar as chaves globais
        admin_cfg_path = os.path.join(os.path.dirname(__file__), "admin_config.json")
        if not os.path.exists(admin_cfg_path):
            return
            
        try:
            with open(admin_cfg_path, 'r', encoding='utf-8') as f:
                admin_cfg = json.load(f)
                api_config = admin_cfg.get("api_config", {})
                
                # Definir a ordem de prioridade (Plano B, C, D, E, F)
                providers = [
                    ("groq", "Groq"),
                    ("openrouter", "OpenRouter"),
                    ("grok", "Grok"),
                    ("deepseek", "DeepSeek"),
                    ("chatgpt", "ChatGPT")
                ]
                
                for key_name, display_name in providers:
                    provider_data = api_config.get(key_name, {})
                    keys = provider_data.get("api_keys", [])
                    
                    if keys:
                        # Se houver múltiplas chaves (estratégia de rodízio)
                        api_keys_list = provider_data.get("api_keys", [])
                        base_url = provider_data.get("base_url")
                        model = provider_data.get("model")
                        
                        for key_obj in api_keys_list:
                            api_key = key_obj.get("key")
                            if not api_key or "YOUR_API_KEY" in api_key:
                                continue
                                
                            if not model:
                                if key_name == "openrouter":
                                    # Adiciona uma lista rotativa de modelos grátis do OpenRouter
                                    or_free_models = [
                                        "meta-llama/llama-3.3-70b-instruct:free",
                                        "openai/gpt-oss-120b:free",
                                        "z-ai/glm-4.5-air:free",
                                        "nvidia/nemotron-3-nano-30b-a3b:free",
                                        "nvidia/nemotron-nano-9b-v2:free",
                                        "qwen/qwen3-next-80b-a3b-instruct:free"
                                    ]
                                    for free_mod in or_free_models:
                                        client = OpenAICompatibleAPI(
                                            base_url=base_url,
                                            api_key=api_key,
                                            model=free_mod,
                                            name=f"{display_name} ({free_mod})"
                                        )
                                        self.fallbacks.append(client)
                                    continue # Pula o fluxo padrão abaixo
                                elif key_name == "groq": model = "llama-3.3-70b-versatile"
                                elif key_name == "grok": model = "grok-build-0.1"
                                elif key_name == "deepseek": model = "deepseek-chat"
                                elif key_name == "chatgpt": model = "gpt-4o-mini"
                                
                            if base_url:
                                client = OpenAICompatibleAPI(
                                    base_url=base_url,
                                    api_key=api_key,
                                    model=model,
                                    name=f"{display_name} ({key_obj.get('name', 'Key')})"
                                )
                                self.fallbacks.append(client)
                            
        except Exception as e:
            print(f"⚠️ [Cascade] Erro ao carregar fallbacks: {e}")

    def generate_content(self, prompt: str, system_prompt: str = None, is_admin: bool = False) -> Optional[str]:
        # --- PLANO A (Gemini API com 14 chaves rotativas) ---
        # Só executa se for admin E o modo de stress test estiver desligado
        if is_admin and not FORCE_DISABLE_GEMINI:
            print("🤖 [Cascade] Iniciando Plano A (Gemini) para o Admin...")
            response = self.gemini.generate_content(prompt, system_prompt)
            
            if response:
                return response
                
            print("⚠️ [Cascade] Plano A (Gemini) falhou. Iniciando Fallbacks...")
        else:
            if FORCE_DISABLE_GEMINI:
                print("🚧 [Cascade] MODO STRESS TEST ATIVO: Pulando Gemini...")
            else:
                print("👥 [Cascade] Usuário comum detectado: Pulando Gemini...")
        
        # --- PLANOS B, C, D, E (Groq, OpenRouter, Grok, DeepSeek) ---
        for fallback in self.fallbacks:
            response = fallback.generate_content(prompt, system_prompt)
            if response:
                print(f"✅ [Cascade] Fallback executado com sucesso via {fallback.name}!")
                return response
                
        print("❌ [Cascade] TODAS AS APIs FALHARAM! (Gemini + Fallbacks)")
        return None
