import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# Diretriz de Arquitetura do Apollo Edit: BACKGROUND BOTS NUNCA USAM OPENROUTER.
# O OpenRouter é sagrado e restrito ao uso direto do CEO.
# Todos os Agentes de Redação devem bater exclusivamente no Lightning AI (Pool Gratuito).
LIGHTNING_KEY = os.getenv("LIGHTNING_API_KEY")

if not LIGHTNING_KEY:
    print("[WRITER] ALERTA CRÍTICO: LIGHTNING_API_KEY não encontrada no ambiente!")
    print("[WRITER] Abortando inicialização do motor de escrita para proteger o cofre do OpenRouter.")
    # Falha seca para não onerar
    client = None
else:
    client = OpenAI(
        api_key=LIGHTNING_KEY,
        base_url="https://api.lightning.ai/v1"
    )

def escrever_artigo(pauta, persona_prompt):
    if not client:
        return {"markdown": "# Erro de Sistema\nAPI Lightning não configurada.", "image_prompt": "Error", "audio_script": "Error"}

    print(f"[WRITER] Escrevendo artigo baseado em: {pauta['title']}")
    
    prompt = f"""
    Você é um jornalista expert. Escreva um artigo completo sobre: {pauta['title']}.
    Siga o estilo da persona: {persona_prompt}.
    O artigo deve ser denso, ter introdução, desenvolvimento, subtítulos em H2 e conclusão.
    Use formatação Markdown.
    
    REGRA DE MONETIZAÇÃO (OBRIGATÓRIA):
    Exatamente na metade do texto (após uns 3 ou 4 parágrafos), você DEVE inserir a tag exata: [PAYWALL]
    Isso vai bloquear o resto do conteúdo para não-assinantes. Todo o texto depois dessa tag será borrado no site.
    
    No final da resposta, adicione uma linha EXATA separada por "|||" no seguinte formato:
    [ARTIGO MARKDOWN]|||[PROMPT DE IMAGEM CURTO, EM INGLÊS, CINEMÁTICO]|||[TEXTO LIMPO PARA O NARRADOR LER (RESUMO PARA RÁDIO/PODCAST)]
    
    Exemplo:
    # Título
    Texto inicial...
    
    [PAYWALL]
    
    Resto do texto muito aprofundado...
    |||
    A detailed cinematic photograph of a bear on wall street, 8k, photorealistic
    |||
    Olá, seja bem-vindo. Hoje vamos falar sobre como os ursos invadiram Wall Street!
    """

    try:
        # Usa o modelo Qwen (ou similar robusto) estritamente hospedado na Lightning AI
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=[
                {"role": "system", "content": "Você é um jornalista de alto nível focado em SEO."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        
        if "|||" in content:
            parts = content.split("|||")
            markdown = parts[0].strip()
            image_prompt = parts[1].strip()
            audio_script = parts[2].strip() if len(parts) > 2 else "Resumo não gerado."
        else:
            markdown = content.strip()
            image_prompt = "A generic placeholder image for a blog post, 4k"
            audio_script = "Resumo da notícia."
            
        print("[WRITER] [ OK ] Texto gerado com sucesso via OpenAI SDK Compatível!")
        return {
            "markdown": markdown,
            "image_prompt": image_prompt,
            "audio_script": audio_script
        }
    except Exception as e:
        print(f"[WRITER] [ERRO] Falha ao gerar texto: {e}")
        return {
            "markdown": f"# {pauta['title']}\nErro na API do LLM.",
            "image_prompt": "Error",
            "audio_script": "Error"
        }

def gerar_comentarios_fantasmas(titulo, quantidade=5):
    print(f"[WRITER] Gerando {quantidade} comentários fantasmas para: {titulo}")
    prompt = f"""
    Crie uma lista de {quantidade} comentários realistas para um artigo com o título: "{titulo}".
    Aja como pessoas diferentes da internet. Alguns devem concordar, outros discordar, fazer perguntas ou contar pequenas experiências pessoais.
    Retorne EXATAMENTE UM JSON ARRAY válido com a seguinte estrutura e NADA MAIS:
    [
      {{"authorName": "Nome Realista", "content": "Texto do comentário bem natural"}},
      ...
    ]
    """
    if not client: return []
    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=[
                {"role": "system", "content": "Você é um gerador de dados JSON. Retorne APENAS o JSON solicitado, sem blocos de markdown ou texto adicional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85
        )
        content = response.choices[0].message.content.strip()
        # Limpa blocos de código se a IA mandar
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        comentarios = json.loads(content.strip())
        return comentarios
    except Exception as e:
        print(f"[WRITER] [ERRO] Falha ao gerar comentários: {e}")
        return []
