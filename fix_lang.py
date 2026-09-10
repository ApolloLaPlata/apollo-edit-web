import re

path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\apollo_modal_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('\"fastapi[standard]\", \"pydantic\", \"requests\"', '\"fastapi[standard]\", \"pydantic\", \"requests\", \"langdetect\"')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed langdetect!')
