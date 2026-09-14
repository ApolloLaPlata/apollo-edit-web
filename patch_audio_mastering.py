import sys

with open("servidor_web.py", "r", encoding="utf-8") as f:
    text = f.read()

replacement = """        model_mapped = model_map.get(engine, engine)
        
        # --- INJEÇÃO DE MASTERIZAÇÃO E IDIOMA (O SEGREDO DO "PERFEITO") ---
        # Garantir que as tags de linguagem estejam presentes para PT-BR se o usuário não colocou
        final_prompt = prompt
        final_lyrics = lyrics
        
        if model_mapped == "ace-step":
            if final_lyrics and "[pt]" not in final_lyrics.lower() and "[en]" not in final_lyrics.lower():
                final_lyrics = "[pt]\\n\\n" + final_lyrics
            if "high quality" not in final_prompt.lower():
                final_prompt += ", high quality, studio mix, masterpiece, hi-fi, wide stereo"
                
        elif model_mapped == "minimax":
            if "language:" not in final_prompt.lower():
                final_prompt = "[Language: Portuguese (Brazil)] [Accent: Brazilian] " + final_prompt
                if final_lyrics and "[pt-br]" not in final_lyrics.lower():
                    # Adiciona a tag de lingua no inicio
                    final_lyrics = "[PT-BR]\\n" + final_lyrics
            if "studio mix" not in final_prompt.lower():
                final_prompt += ", high quality studio mix, cinematic"
                
        elif model_mapped == "sa3":
            if "masterpiece" not in final_prompt.lower():
                final_prompt += ", high quality, 4k audio, high fidelity, clean, sharp, stereo, masterpiece"

        payload = {
            "model": model_mapped,
            "prompt": final_prompt,
            "lyrics": final_lyrics,
            "duration": float(duration)
        }"""

if 'model_mapped = model_map.get(engine, engine)' not in text:
    old_code = """        lyrics = body.get("lyrics", "")
        payload = {
            "model": model_map.get(engine, engine),
            "prompt": prompt,
            "lyrics": lyrics,
            "duration": float(duration)
        }"""
    text = text.replace(old_code, old_code.replace('payload = {', replacement.split('payload = {')[0] + 'payload = {'))
    
    with open("servidor_web.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("PATCH_APPLIED")
else:
    print("ALREADY_PATCHED")
