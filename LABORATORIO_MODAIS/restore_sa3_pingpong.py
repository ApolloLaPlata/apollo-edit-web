import shutil

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/stable_audio_engine.py"
bak_path = file_path + ".bak"

shutil.copy(bak_path, file_path)

print("Restaurado .bak do SA3 mantendo o pingpong!")
