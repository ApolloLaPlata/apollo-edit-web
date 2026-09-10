import os

with open('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

old = '''    def isatty(self):
        return False'''

new = '''    def isatty(self):
        return False
        
    def reconfigure(self, **kwargs):
        pass'''

code = code.replace(old, new)

with open('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch reconfigure executado")
