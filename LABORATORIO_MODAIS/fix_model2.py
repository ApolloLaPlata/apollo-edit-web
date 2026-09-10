with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('"model": "meta-llama/Meta-Llama-3.1-70B-Instruct"', '"model": "nvidia-nemotron-3-ultra-550b-a55b"')

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(code)
