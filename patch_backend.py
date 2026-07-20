import re

filepath = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\servidor_web.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

new_prompts = """
    elif req.prompt_type == 'gerar-shorts':
        sys_prompt = "Você é um roteirista de YouTube Shorts focado em retenção. Crie um roteiro EXTREMAMENTE DINÂMICO e RÁPIDO (menos de 60 segundos) com base na notícia/texto fornecido. Retorne em formato Markdown com as seções: # 📱 Opções de Título (3 opções), # 📜 Roteiro do Vídeo Curto."
        user_prompt = f"Gere um roteiro curto para: {req.input_text}"

    elif req.prompt_type == 'ideias-thumbnails':
        sys_prompt = "Você é um designer de thumbnails de YouTube focado em CTR (Click-Through Rate). Analise o roteiro ou contexto fornecido e sugira 3 ideias brilhantes de thumbnails que despertem alta curiosidade. Descreva os elementos visuais, a composição, e o texto exato na imagem para cada uma. Retorne em formato Markdown."
        user_prompt = f"Sugira 3 thumbnails para:\n\n{req.input_text}"

    elif req.prompt_type == 'deep-dive':
        sys_prompt = "Você é um jornalista investigativo e analista geopolítico/econômico. Aprofunde-se no contexto da notícia fornecida, explicando o pano de fundo, os interesses envolvidos, os desdobramentos futuros e o que a grande mídia pode estar omitindo. Retorne em formato Markdown."
        user_prompt = f"Aprofunde esta notícia:\n\n{req.input_text}"
"""

# Inject before "try:\n        payload = {" which starts the actual request
if "elif req.prompt_type == 'deep-dive':" not in content:
    content = content.replace("    try:\n        payload = {", new_prompts + "\n    try:\n        payload = {")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Backend patched successfully!")
else:
    print("Backend already patched!")
