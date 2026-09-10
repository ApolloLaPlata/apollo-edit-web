import os
import sys

with open('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Inject logger at the top
logger_code = '''
import sys
import logging
import os
from collections import deque

class TailLogger:
    def __init__(self, filename, max_lines=200):
        self.filename = filename
        self.max_lines = max_lines
        self.terminal = sys.stdout
        # clear file on startup
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("")
            
    def write(self, message):
        self.terminal.write(message)
        try:
            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(message)
        except:
            pass
            
    def flush(self):
        self.terminal.flush()

sys.stdout = TailLogger("colmeia_execution.log")
sys.stderr = sys.stdout
'''

# Find the place to inject
import re
code = code.replace("from fastapi import FastAPI", logger_code + "\nfrom fastapi import FastAPI")

# Change /api/colmeia/logs endpoint
old_endpoint = '''@app.get("/api/colmeia/logs")
async def colmeia_logs():
    """Lê a memória ativa para exibir no painel esquerdo."""
    mem_path = os.path.join(BASE_DIR, "MEMORIA_ATIVA_SISTEMA.md")
    try:
        with open(mem_path, "r", encoding="utf-8") as f:
            return PlainTextResponse(f.read())
    except Exception as e:
        return PlainTextResponse(f"Erro ao ler a memória: {e}", status_code=500)'''

new_endpoint = '''@app.get("/api/colmeia/logs")
async def colmeia_logs():
    """Lê o log de execução em tempo real para exibir no painel esquerdo."""
    log_path = "colmeia_execution.log"
    try:
        if not os.path.exists(log_path):
            return PlainTextResponse("Aguardando logs de execução...")
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return PlainTextResponse("".join(lines[-100:]))
    except Exception as e:
        return PlainTextResponse(f"Erro ao ler logs de execução: {e}", status_code=500)'''

code = code.replace(old_endpoint, new_endpoint)

with open('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch log engine executado")
