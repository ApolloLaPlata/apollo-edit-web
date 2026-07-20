import os

file = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\api\routes_ai_director.py'
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add get_api_config to DummyConfig
content = content.replace("    def get(self, key, default=None):\n        return os.environ.get(key, default)\n", "    def get(self, key, default=None):\n        return os.environ.get(key, default)\n    def get_api_config(self, provider):\n        return None\n")

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)
