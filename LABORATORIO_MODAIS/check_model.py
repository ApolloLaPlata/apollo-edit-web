with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    for line in f:
        if 'nvidia' in line.lower() or 'llama' in line.lower():
            print(line.strip())
