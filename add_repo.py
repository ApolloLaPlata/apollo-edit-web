import re

path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\engines\universal_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# I need to insert it inside a run_commands list
# Let's just find the end of the first run_commands and insert another run_commands block
if "ComfyUi-TextEncodeQwenImageEditAdvanced" not in content:
    content = content.replace('.env({', '.run_commands(["git clone https://github.com/BigStationW/ComfyUi-TextEncodeQwenImageEditAdvanced.git /comfyui/custom_nodes/ComfyUi-TextEncodeQwenImageEditAdvanced && cd /comfyui/custom_nodes/ComfyUi-TextEncodeQwenImageEditAdvanced && pip install -r requirements.txt || true"]).env({')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added back TextEncodeQwenImageEditAdvanced!")
else:
    print("Already there!")
