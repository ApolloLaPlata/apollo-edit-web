import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

old_func = '''async def audio_lab_test(
    model: str = Form(...),
    prompt: str = Form(...),
    lyrics: str = Form(None),
    ref_audio: UploadFile = File(None)
):'''
new_func = '''async def audio_lab_test(
    model: str = Form(...),
    prompt: str = Form(...),
    lyrics: str = Form(None),
    duration: int = Form(30),
    ref_audio: UploadFile = File(None)
):'''

if old_func in content:
    content = content.replace(old_func, new_func)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Backend atualizado com duração.")
else:
    print("Não achou a string no backend.")
