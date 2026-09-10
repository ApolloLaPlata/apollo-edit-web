import shutil

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/stable_audio_engine.py"
bak_path = file_path + ".bak"

shutil.copy(bak_path, file_path)

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('sampler_type="pingpong"', 'sampler_type="dpmpp-3m-sde"')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Restaurado .bak do SA3 e trocado sampler para dpmpp-3m-sde!")
