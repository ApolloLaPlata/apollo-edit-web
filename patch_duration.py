with open('servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_code = 'duration = body.get("duration", 30)'
new_code = '''duration = body.get("duration", 30)
        
        # O usuario solicitou que musicas com letra nao tenham a duracao truncada
        engine = body.get("engine", "acestep")
        if engine in ["acestep", "minimax"] and body.get("lyrics"):
            duration = 180  # Forca um limite alto para a musica terminar naturalmente
'''

code = code.replace(old_code, new_code)

with open('servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(code)
