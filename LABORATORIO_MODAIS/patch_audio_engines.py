import re

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/ace_step_python_engine.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix ace-step CFG from 18.0 to 4.5
content = content.replace("guidance_scale=18.0,", "guidance_scale=4.5,")
# Also infer_steps to 50 instead of 100 for better dynamics vs robot
content = content.replace("infer_step=100,", "infer_step=50,")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

file_path2 = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/stable_audio_engine.py"
with open(file_path2, "r", encoding="utf-8") as f:
    content2 = f.read()

# Injetar prompt de mastering
old_cond = 'conditioning = [{"prompt": prompt, "seconds_start": 0, "seconds_total": duration_s}]'
new_cond = 'master_prompt = prompt + ", high quality, 4k audio, high fidelity, clean, sharp, stereo, masterpiece"\n        conditioning = [{"prompt": master_prompt, "seconds_start": 0, "seconds_total": duration_s}]'

content2 = content2.replace(old_cond, new_cond)

with open(file_path2, "w", encoding="utf-8") as f:
    f.write(content2)

print("Audio engines updated!")
