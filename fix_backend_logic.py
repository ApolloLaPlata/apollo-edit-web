import sys
import re

filepath = r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\servidor_web.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

channel_logic = '''
    elif req.prompt_type == 'analisar-canal':
        sys_prompt = f"""Atue como um estrategista de YouTube. Analise os seguintes vídeos salvos pelo criador de conteúdo. Com base nesses vídeos, forneça:
1. Uma análise geral do nicho e do interesse do público (quais temas geram mais interesse).
2. 5 ideias de vídeos inéditos inspirados nesse conteúdo, mas com um ângulo único ou aprofundado.
3. Dicas de palavras-chave e estratégias de thumbnail para esse nicho.
Responda em Markdown, de forma clara e estruturada."""
        user_prompt = f"Vídeos salvos:\\n{req.input_text}"
'''

monitor_logic = '''
    elif req.prompt_type == 'monitorar-perfil':
        sys_prompt = f"""Extraia SOMENTE os dados reais e públicos referentes à página solicitada. Se não conseguir ler, retorne JSON com erro.
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
}}"""
        user_prompt = f"Dados extraídos da página / URL:\\n{req.input_text}"
'''

if 'analisar-canal' not in content:
    content = content.replace("    elif req.prompt_type == 'gerar-estrategia':", channel_logic + "\n    elif req.prompt_type == 'gerar-estrategia':")
    
if 'monitorar-perfil' not in content:
    content = content.replace("    elif req.prompt_type == 'gerar-estrategia':", monitor_logic + "\n    elif req.prompt_type == 'gerar-estrategia':")

# And we also need to parse the response if it's JSON for monitorar-perfil
json_parse_logic = '''
        elif req.prompt_type == 'monitorar-perfil':
            import json
            try:
                clean_content = content.replace("```json", "").replace("```", "").strip()
                data_parsed = json.loads(clean_content)
                return JSONResponse({"status": "success", "data": data_parsed})
            except Exception as e:
                return JSONResponse({"status": "error", "message": f"Erro parse json: {str(e)}"}, status_code=500)
'''
if "elif req.prompt_type == 'monitorar-perfil':" not in content.split('if req.prompt_type == \'images\':')[1]:
    content = content.replace("        elif req.prompt_type == 'seo':", json_parse_logic.lstrip() + "        elif req.prompt_type == 'seo':")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed backend logic successfully!')
