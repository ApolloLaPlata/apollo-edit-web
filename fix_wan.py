import re
with open('backend/cloud_tools/engines/wan_engine.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace enable_memory_snapshot=True
text = text.replace('enable_memory_snapshot=True, experimental_options={"enable_gpu_snapshot": True}', 'enable_memory_snapshot=False')

with open('backend/cloud_tools/engines/wan_engine.py', 'w', encoding='utf-8') as f:
    f.write(text)
