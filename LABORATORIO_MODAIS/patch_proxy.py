with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('if response.status_code != 402:', 'if response.status_code not in (401, 402, 403, 429, 500, 502, 503):')
code = code.replace('print("[Proxy] Erro 402 (Saldo Esgotado) detectado. Trocando de chave...")', 'print(f"[Proxy] Erro {response.status_code} detectado. Trocando de chave...")')

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(code)
