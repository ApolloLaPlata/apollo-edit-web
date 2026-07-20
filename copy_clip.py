import os
import re

source = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\COPIA BACKUP TUTORIAL DAS COISAS\APOLLO_EDIT_WEB 14\temp_restore\music_video_engine.py'
dest = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\services\clip_factory.py'

with open(source, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace config_manager dependency
content = content.replace("def __init__(self, config_manager=None, logger=None):", "def __init__(self, configs=None, logger=None):")
content = content.replace("self.config_manager = config_manager", "self.configs = configs or {}")

with open(dest, 'w', encoding='utf-8') as f:
    f.write(content)
print("clip_factory.py created")
