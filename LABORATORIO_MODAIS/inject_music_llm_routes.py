import os

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_routes = '''
# =====================================================================
# ROTAS INTELIGENTES PARA MÚSICA (LLM)
# =====================================================================

@app.post("/api/music/auto_tag_lyrics")
async def music_auto_tag_lyrics(req: Request):
    try:
        body = await req.json()
        raw_lyrics = body.get("lyrics", "")
        if not raw_lyrics:
            return {"success": False, "error": "Letra vazia"}
            
        import httpx
        system_prompt = """Você é um especialista em estruturação musical (Suno AI, Stable Audio).
A tarefa é ler a letra fornecida pelo usuário e adicionar TAGS DE ESTRUTURA, como [Intro], [Verse], [Chorus], [Bridge], [Guitar Solo], [Drop], [Outro].
Não modifique as palavras originais da letra. Apenas insira as tags (entre colchetes) antes de cada estrofe ou seção.
Retorne APENAS a letra estruturada."""

        proxy_url = "http://127.0.0.1:8080/api/lightning_proxy"
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(proxy_url, json={
                "model": "meta-llama/Llama-3-70b-chat-hf",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_lyrics}
                ]
            })
            
            if resp.status_code == 200:
                data = resp.json()
                processed = data.get("choices", [{}])[0].get("message", {}).get("content", raw_lyrics)
                return {"success": True, "structured_lyrics": processed.strip()}
            else:
                return {"success": False, "error": f"Erro do LLM: {resp.status_code}"}
                
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/music/generate_batch_ideas")
async def music_generate_batch_ideas(req: Request):
    try:
        body = await req.json()
        theme = body.get("theme", "músicas épicas")
        count = body.get("count", 3)
        
        import httpx
        import json
        
        system_prompt = f"""Você é um produtor musical criativo especializado em prompts para geradores de áudio AI (Suno, ACE-Step).
O usuário quer gerar {count} ideias de músicas baseadas neste tema: "{theme}".

Retorne EXATAMENTE UM JSON VÁLIDO contendo um array 'tracks' onde cada item tem:
- 'style': Um prompt em inglês descrevendo o estilo (ex: 'Epic cyberpunk synthwave, 120bpm, heavy bass'). MÁXIMO 100 caracteres.
- 'lyrics': A letra completa com tags [Verse], [Chorus]. Em português se o tema pedir, ou inglês se pedir.

O formato deve ser ESTRITAMENTE:
{{
  "tracks": [
    {{"style": "...", "lyrics": "..."}},
    {{"style": "...", "lyrics": "..."}}
  ]
}}
NÃO USE crases de formatação Markdown. Retorne puramente o texto JSON.
"""

        proxy_url = "http://127.0.0.1:8080/api/lightning_proxy"
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(proxy_url, json={
                "model": "meta-llama/Llama-3-70b-chat-hf",
                "messages": [
                    {"role": "system", "content": system_prompt}
                ]
            })
            
            if resp.status_code == 200:
                data = resp.json()
                raw_content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Cleanup markdown formatting if present
                clean_json = raw_content.replace('`json', '').replace('`', '').strip()
                
                try:
                    parsed = json.loads(clean_json)
                    return {"success": True, "tracks": parsed.get("tracks", [])}
                except Exception as json_err:
                    return {"success": False, "error": f"Falha no parse JSON do LLM: {json_err}", "raw": raw_content}
            else:
                return {"success": False, "error": f"Erro do LLM: {resp.status_code}"}
                
    except Exception as e:
        return {"success": False, "error": str(e)}

'''

if '/api/music/auto_tag_lyrics' not in code:
    # Append to the end of the file or before the bottom
    # Assuming standard FastAPI structure
    code += '\n' + new_routes + '\n'
    with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Rotas de LLM para música injetadas no servidor_web.py.")
else:
    print("As rotas de LLM já existem.")
