import re

files = [
    'backend/cloud_tools/engines/flux_engine.py',
    'backend/cloud_tools/engines/flux_txt2img_engine.py',
    'backend/cloud_tools/engines/universal_engine.py'
]

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        content = file.read()
    
    new_content = re.sub(
        r'@contextmanager\s+def force_cpu_during_snapshot\(\):[\s\S]*?os\.environ\.pop\("PYTHONPATH", None\)',
        '@contextmanager\ndef force_cpu_during_snapshot():\n    yield',
        content
    )
    with open(f, 'w', encoding='utf-8-sig') as file:
        file.write(new_content)
    print(f"Cleaned {f}!")
