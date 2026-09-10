import os

with open('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

old = '''    def flush(self):
        self.terminal.flush()'''

new = '''    def flush(self):
        self.terminal.flush()
        
    def isatty(self):
        return False'''

code = code.replace(old, new)

with open('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch isatty executado")
