import os
import subprocess
import sys

try:
    import ftfy
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'ftfy'])
    import ftfy

filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\MEMORIA_ATIVA_SISTEMA.md'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

fixed_text = ftfy.fix_text(text)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(fixed_text)
print("FTFY applied successfully!")
