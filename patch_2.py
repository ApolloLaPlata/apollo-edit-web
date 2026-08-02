import os
path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\engines\universal_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('scaledown_window=1,', 'scaledown_window=2,')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated scaledown_window to 2")
