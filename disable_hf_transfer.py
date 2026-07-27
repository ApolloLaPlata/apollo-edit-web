import glob
import re

files = glob.glob("backend/cloud_tools/engines/*.py") + glob.glob("backend/cloud_tools/*.py")

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    if '"HF_HUB_ENABLE_HF_TRANSFER": "1"' in content or "'HF_HUB_ENABLE_HF_TRANSFER': '1'" in content:
        content = content.replace('"HF_HUB_ENABLE_HF_TRANSFER": "1"', '"HF_HUB_ENABLE_HF_TRANSFER": "0"')
        content = content.replace("'HF_HUB_ENABLE_HF_TRANSFER': '1'", "'HF_HUB_ENABLE_HF_TRANSFER': '0'")
        print(f"Disabled HF_TRANSFER in {f}")
        with open(f, 'w', encoding='utf-8-sig') as file:
            file.write(content)
