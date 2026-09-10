import os
import sys
import glob
import asyncio
from pathlib import Path
from google.antigravity import Agent, LocalAgentConfig

def get_latest_transcript(brain_dir: str) -> str:
    search_pattern = os.path.join(brain_dir, '*', '.system_generated', 'logs', 'transcript_full.jsonl')
    files = glob.glob(search_pattern)
    if not files:
        raise FileNotFoundError("Nenhum transcript encontrado.")
    
    latest_file = max(files, key=os.path.getmtime)
    print(f"[Compressor] Lendo transcript bruto de: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

async def main():
    # O SDK standalone requer uma API Key do Gemini (gratuita no Google AI Studio)
    # Verifique se a variável de ambiente está definida.
    if not os.environ.get("GEMINI_API_KEY"):
        print("\n" + "="*60)
        print("🚨 ERRO FATAL: GEMINI_API_KEY não encontrada!")
        print("Para que o Compressor processe 8 horas de chat em background, ele precisa de uma chave de API própria.")
        print("1. Acesse: https://aistudio.google.com/app/apikey")
        print("2. Crie uma chave grátis.")
        print("3. No PowerShell, rode: $env:GEMINI_API_KEY='SUA_CHAVE'")
        print("4. Tente o comando /clone novamente.")
        print("="*60 + "\n")
        return

    brain_dir = r"C:\Users\v5est\.gemini\antigravity\brain"
    output_file = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\INFINITE_CORE.md"
    
    try:
        print("[Compressor] Iniciando extração cirúrgica de memória (Limite de 2M Tokens)...")
        transcript = get_latest_transcript(brain_dir)
        
        system_prompt = """Você é o Apollo Infinite Memory Compressor, um agente especializado em retenção de estado arquitetural de altíssima precisão.
Seu objetivo é analisar o log bruto (JSONL) de um chat de programação exaustivo e extrair a ESSÊNCIA TÉCNICA E A PERSONA IMUTÁVEL para que o agente no próximo chat possa continuar exatamente do mesmo ponto.

Você DEVE extrair e organizar detalhadamente:
1. DIRETRIZES DA PERSONA: O tom exato e as regras comportamentais que o usuário impôs.
2. MATEMÁTICA E LÓGICA SAGRADA: O usuário mencionou "matemática exata de calcular o áudio" e "novo sistema referente ao estado emocional da voz". Extraia todas as fórmulas, variáveis, scripts e lógica condicional associados a esses sistemas de forma VERBATIM.
3. CONTEXTO ATUAL E DIRETRIZES ABERTAS: O que estava sendo feito no final do chat? Quais os próximos passos imediatos?

Não crie resumos genéricos ("Eles falaram sobre áudio"). Você deve atuar como um clonador de memória técnica, injetando o código, a matemática e as regras. O formato final deve ser estritamente Markdown e deve iniciar com '# 🧠 APOLLO INFINITE CORE'."""

        config = LocalAgentConfig(
            system_instructions=system_prompt,
        )
        
        print("[Compressor] Invocando rede neural do Gemini 1.5 Pro via SDK...")
        async with Agent(config) as agent:
            # Pegamos os últimos 1 milhão de caracteres (suficiente para as últimas horas intensas)
            prompt = f"Analise este log bruto e gere o INFINITE_CORE.md denso com toda a matemática e arquitetura:\n\n{transcript[-1000000:]}"
            response = await agent.chat(prompt)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
                
            print(f"[Compressor] 🚀 Sucesso Absoluto! A memória sagrada foi clonada e salva em: {output_file}")
            print(f"[Compressor] Pode abrir o novo chat, a Regra AGENTS.md fará o Boot automático.")
            
    except Exception as e:
        print(f"[Compressor] Erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())
