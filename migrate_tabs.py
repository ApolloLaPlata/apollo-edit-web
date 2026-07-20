import customtkinter as ctk
import re
import sys

def convert_to_ctk(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Widget substitutions
    content = content.replace('ctk.CTkFrame', 'ctk.CTkFrame')
    content = content.replace('ctk.CTkFrame', 'ctk.CTkFrame')
    content = content.replace('ctk.CTkLabelFrame', 'ctk.CTkLabelFrame')
    content = content.replace('ctk.CTkLabelFrame', 'ctk.CTkLabelFrame')
    content = content.replace('ctk.CTkLabel', 'ctk.CTkLabel')
    content = content.replace('ctk.CTkLabel', 'ctk.CTkLabel')
    content = content.replace('ctk.CTkButton', 'ctk.CTkButton')
    content = content.replace('ctk.CTkButton', 'ctk.CTkButton')
    content = content.replace('ctk.CTkEntry', 'ctk.CTkEntry')
    content = content.replace('ctk.CTkEntry', 'ctk.CTkEntry')
    content = content.replace('ctk.CTkSwitch', 'ctk.CTkSwitch')
    content = content.replace('ctk.CTkSwitch', 'ctk.CTkSwitch')
    content = content.replace('ctk.CTkOptionMenu', 'ctk.CTkOptionMenu')
    
    # Fix textvariable -> variable for OptionMenu and Switch
    content = re.sub(r'(CTkOptionMenu[^>]*?)textvariable=', r'\1variable=', content)
    content = re.sub(r'(CTkSwitch[^>]*?)textvariable=', r'\1variable=', content)
    
    # Strip invalid kwargs
    kwargs_to_strip = [
        r',\s*bd=\d+',
        r',\s*borderwidth=\d+',
        r',\s*relief=[\'"]\w+[\'"]',
        r',\s*highlightthickness=\d+',
        r',\s*wraplength=\d+',
        r',\s*bg=[\'"]#?[a-zA-Z0-9]+[\'"]',
        r',\s*fg=[\'"]#?[a-zA-Z0-9]+[\'"]'
    ]
    
    for pattern in kwargs_to_strip:
        content = re.sub(pattern, '', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Migrated {filepath}")

for f in ['aba_configuracoes.py', 'aba_criador_templates.py']:
    convert_to_ctk(f)

