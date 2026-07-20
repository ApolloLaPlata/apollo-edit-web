import os
import requests

def truncate_prompt_if_needed(prompt: str, max_chars: int = 8000) -> str:
    """Evita torrar tokens cortando excesso de histórico e logs longos."""
    if len(prompt) > max_chars:
        print(f"[Agent Core] ⚠️ Aviso: Prompt excedeu {max_chars} chars. Truncando para economizar grana.")
        # Mantém o início (prováveis instruções) e o final (últimos logs)
        return prompt[:max_chars//2] + "\n\n[...TRECHO REMOVIDO PARA ECONOMIA DE TOKENS...]\n\n" + prompt[-max_chars//2:]
    return prompt

def call_agent_llm(prompt: str, complexity: str = 'low', premium_key: str = None, fallback_free_key: str = None) -> str:
    """
    Roteador de Inteligência Corporativo.
    - complexity='low': Vai direto pro modelo gratuito. Custo ZERO.
    - complexity='high': Vai no modelo Premium (se tiver chave). Se falhar, usa o gratuito.
    """
    
    # 1. Tesoura de Tokens (Evita input excessivo)
    max_len = 16000 if complexity == 'high' else 4000
    safe_prompt = truncate_prompt_if_needed(prompt, max_chars=max_len)
    
    # 2. Roteamento Inteligente
    if complexity == 'high' and premium_key:
        try:
            print("[Agent Core] Tarefa COMPLEXA. Tentando via API Premium (Gasto Autorizado)...")
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {premium_key}"},
                json={
                    "model": "google/gemini-3.5-pro", # Modelo de altíssima capacidade
                    "messages": [{"role": "user", "content": safe_prompt}]
                },
                timeout=30
            )
            res.raise_for_status()
            print("[Agent Core] Sucesso via API Premium!")
            return res.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"[Agent Core] Falha na API Premium: {e}. Acionando Fallback Gratuito...")

    # 3. Fallback ou Tarefa Simples
    if fallback_free_key or complexity == 'low':
        try:
            motivo = "Tarefa SIMPLES." if complexity == 'low' else "Fallback ativado."
            print(f"[Agent Core] {motivo} Usando Modelo Gratuito de alta qualidade...")
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {fallback_free_key}" if fallback_free_key else ""},
                json={
                    "model": "google/gemini-pro:free", # Custo zero
                    "messages": [{"role": "user", "content": safe_prompt}]
                },
                timeout=30
            )
            res.raise_for_status()
            print("[Agent Core] Sucesso via Modelo Gratuito!")
            return res.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"[Agent Core] Falha no Modelo Gratuito: {e}.")
            return ""
    
    print("[Agent Core] Nenhuma chave fornecida e sem fallback disponível.")
    return ""
