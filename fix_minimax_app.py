import os

path = 'E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\backend\\cloud_tools\\engines\\minimax_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('app = modal.App("apollo-minimax-engine")', 'from backend.cloud_tools.modal_app import app')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
