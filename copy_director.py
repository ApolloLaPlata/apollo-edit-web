import os
import re

source = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\COPIA BACKUP TUTORIAL DAS COISAS\APOLLO_EDIT_WEB 14\temp_restore\ai_director_pipeline.py'
dest = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\services\ai_director.py'

with open(source, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to adapt it slightly for the backend so it doesn't rely on the old config_manager.
# We'll just replace `self.config_manager.get(...)` with a dummy that returns os.environ or None for now.
# Or better, we just provide a dummy config_manager dict to it for the initialization.
content = content.replace("def __init__(self, config_manager, openaifm_api_ref=None, gemini_api_ref=None):", "def __init__(self, config_manager=None):")
content = content.replace("self.config_manager   = config_manager", "self.config_manager = config_manager or {}")
content = content.replace("self.openai_api       = openaifm_api_ref", "")
content = content.replace("self.gemini_api       = gemini_api_ref", "")

with open(dest, 'w', encoding='utf-8') as f:
    f.write(content)
print("ai_director.py created")
