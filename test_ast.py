import ast
import os

filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\COPIA BACKUP TUTORIAL DAS COISAS\APOLLO_EDIT_WEB 14\temp_restore\gerador_podcast.py'
with open(filepath, 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
print("Classes:", classes)
print("Functions:", functions)
