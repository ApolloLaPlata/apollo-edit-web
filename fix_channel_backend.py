import sys

filepath = r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\servidor_web.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = '''    elif prompt_type == 'analisar-canal':
        videos = dados.get('videos', [])
        videos_str = '\\n'.join([f"- {v.get('title')} (Canal: {v.get('channel', 'N/A')})" for v in videos])
        instrucao_base = f"""Atue como um estrategista de YouTube.
Analise os seguintes vídeos salvos pelo criador de conteúdo:
{videos_str}

Com base nesses vídeos, forneça:
1. Uma análise geral do nicho e do interesse do público (quais temas geram mais interesse).
2. 5 ideias de vídeos inéditos inspirados nesse conteúdo, mas com um ângulo único ou aprofundado.
3. Dicas de palavras-chave e estratégias de thumbnail para esse nicho.

Responda em Markdown, de forma clara e estruturada.
"""
'''

if 'analisar-canal' not in content:
    content = content.replace("    elif prompt_type == 'gerar-estrategia':", new_logic + "\n    elif prompt_type == 'gerar-estrategia':")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added analisar-canal')
else:
    print('Already exists')
