import re

files = [
    'backend/cloud_tools/engines/universal_engine.py',
    'backend/cloud_tools/engines/flux_engine.py',
    'backend/cloud_tools/engines/flux_txt2img_engine.py'
]

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    # Replace 'if not os.path.exists("/tmp/modal_snapshot_done"):\n        return True' with return False in both places
    content, count = re.subn(
        r'if not os\.path\.exists\("/tmp/modal_snapshot_done"\):\s*\n\s*return True',
        'if not os.path.exists("/tmp/modal_snapshot_done"):\n            return False',
        content
    )
    # also handle indentation difference between inside sitecustomize string and python code
    # let's do a more generic replacement
    print(f"Updated safe_is_available in {f} ({count} matches)")

    with open(f, 'w', encoding='utf-8-sig') as file:
        file.write(content)
