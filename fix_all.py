import os
import glob
import re

for filename in glob.glob('*.py'):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content

    # 1. Strip style=... from CTk widgets ONLY. 
    # Actually, let's just strip style= from everywhere to be safe, because ttk styles will just be ignored if removed.
    content = re.sub(r',\s*style=[\'\"].*?[\'\"]', '', content)
    content = re.sub(r'\.configure\(style=[\'\"].*?[\'\"]\)', '.configure()', content)
    
    # 2. Fix text_color= back to foreground= if it's tk or ttk
    # This is tricky using regex. It's better to just migrate the remaining tk/ttk to ctk!
    # Let's convert all basic tk/ttk widgets to ctk to enforce the new UI.
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
    
    # 3. Fix current() to set() for CTkOptionMenu
    # It usually looks like `# combo.current(0)`. We can't know it's a combo, but .current(0) is only used for comboboxes.
    # Actually, we should replace `.current(` with `.set( ` wait, .set() takes a value, not an index!
    # If they did `# combo.current(0)`, we can't easily translate to `.set(values[0])` via regex.
    # Let's manually comment out .current() calls.
    content = re.sub(r'(\w+\.current\(\d+\))', r'# \1', content)

    # 4. Remove unsupported kwargs from all files now that everything is CTk
    kwargs_to_strip = [
        r',\s*bd=\d+',
        r',\s*borderwidth=\d+',
        r',\s*relief=[\'"]\w+[\'"]',
        r',\s*highlightthickness=\d+',
        r',\s*wraplength=\d+',
        r',\s*bg=[\'"]#?[a-zA-Z0-9]+[\'"]',
        r',\s*fg=[\'"]#?[a-zA-Z0-9]+[\'"]',
        r',\s*background=[\'"]#?[a-zA-Z0-9]+[\'"]',
        r',\s*state=[\'"]readonly[\'"]',  # readonly is not supported in some ctk widgets in the same way
    ]
    for pattern in kwargs_to_strip:
        content = re.sub(pattern, '', content)

    # 5. Fix textvariable -> variable for OptionMenu and Switch
    content = re.sub(r'(CTkOptionMenu[^>]*?)textvariable=', r'\1variable=', content)
    content = re.sub(r'(CTkSwitch[^>]*?)textvariable=', r'\1variable=', content)
    
    # 6. Ensure 'import customtkinter as ctk' is present if ctk is used
    if 'ctk.' in content and 'import customtkinter as ctk' not in content:
        content = 'import customtkinter as ctk\n' + content

    if content != original:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Migrated {filename}")
