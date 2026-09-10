import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\apollo_modal_engine.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('return {"status": "error", "error_type": "exception", "message": str(e)}', 'return {"status": "error", "error_type": "exception", "message": str(e), "traceback": traceback.format_exc()}')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Traceback adicionado!")
