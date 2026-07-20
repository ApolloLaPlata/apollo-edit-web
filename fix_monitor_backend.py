import sys

filepath = r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\servidor_web.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = '''    elif prompt_type == 'monitorar-perfil':
        url = dados.get('url', '')
        instrucao_base = f"""Extraia SOMENTE os dados reais e públicos referentes à página solicitada: {url}.
Se você não conseguir encontrar a lista de vídeos na página, retorne um array vazio [] para recentVideos. NUNCA invente títulos de vídeos.

Responda ESTRITAMENTE em formato JSON com o seguinte schema:
{{
  "username": "Nome de usuário",
  "followers": "Número de seguidores (ex: 1.2M)",
  "likes": "Número total de curtidas",
  "videos": "Número total de vídeos",
  "recentVideos": [
    {{
      "title": "Título do vídeo",
      "views": "100K",
      "likes": "5K",
      "date": "Data se houver"
    }}
  ]
}}
"""
        response_format = "json_object"
'''

if 'monitorar-perfil' not in content:
    content = content.replace("    elif prompt_type == 'analisar-canal':", new_logic + "\n    elif prompt_type == 'analisar-canal':")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added monitorar-perfil')
else:
    print('Already exists')
