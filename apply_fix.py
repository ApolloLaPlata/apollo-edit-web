import re
file_path = "/home/ubuntu/apollo_edit/servidor_web.py"
code_path = "/home/ubuntu/apollo_edit/audio_interceptor_code.txt"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()
    
with open(code_path, "r", encoding="utf-8") as f:
    new_code = f.read()

pattern = re.compile(r'            async def audio_interceptor\(\):.*?return StreamingResponse\(audio_interceptor\(\)\)', re.DOTALL)
if pattern.search(content):
    content = pattern.sub(new_code, content)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("FIX APLICADO!")
else:
    print("Padrao nao encontrado!")
