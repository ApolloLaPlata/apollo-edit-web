with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded_2.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('yield json.dumps({"status": "processing", "message": "Iniciando geração de áudio no Modal..."}).encode(\'utf-8\') + b"\n', 'yield json.dumps({"status": "processing", "message": "Iniciando geração de áudio no Modal..."}).encode(\'utf-8\') + b"\\n"')

text = text.replace('yield json.dumps({"status": "processing", "message": "Processando áudio na nuvem..."}).encode(\'utf-8\') + b"\n', 'yield json.dumps({"status": "processing", "message": "Processando áudio na nuvem..."}).encode(\'utf-8\') + b"\\n"')

text = text.replace('yield json.dumps(data).encode(\'utf-8\') + b"\n', 'yield json.dumps(data).encode(\'utf-8\') + b"\\n"')
text = text.replace('yield response.content + b"\n', 'yield response.content + b"\\n"')
text = text.replace('yield json.dumps({"status": "error", "message": f"Erro proxy interceptor: {str(e)}"}).encode(\'utf-8\') + b"\n', 'yield json.dumps({"status": "error", "message": f"Erro proxy interceptor: {str(e)}"}).encode(\'utf-8\') + b"\\n"')

text = text.replace('b"\\n""', 'b"\\n"')
text = text.replace('b"\\n"', 'b"\\n"') # Just to be safe, any double replacement can be ignored, wait no.

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded_2.py', 'w', encoding='utf-8') as f:
    f.write(text)

import py_compile
try:
    py_compile.compile('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded_2.py', doraise=True)
    print("Sintaxe Python Correta!")
except Exception as e:
    print(f"Erro de sintaxe: {e}")
