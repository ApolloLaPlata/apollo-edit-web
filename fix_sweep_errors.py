import glob
import re

for filename in glob.glob('*.py'):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    # Remove padding= from CTkFrame or CTkLabelFrame
    content = re.sub(r',\s*padding=\d+', '', content)
    content = re.sub(r',\s*padding=\(.*?\)', '', content)
    content = re.sub(r'\s*padding=\d+,', '', content)
    
    # Fix tk.Text text_color to fg
    # We will just look for tk.Text and text_color and replace it
    def fix_tk_text(match):
        inner = match.group(1)
        inner = inner.replace('text_color', 'fg')
        return f"tk.Text({inner})"
        
    content = re.sub(r'tk\.Text\((.*?)\)', fix_tk_text, content, flags=re.DOTALL)
    
    # Let's also check for tk.Listbox and text_color
    def fix_tk_listbox(match):
        inner = match.group(1)
        inner = inner.replace('text_color', 'fg')
        inner = inner.replace('fg_color', 'bg')
        return f"tk.Listbox({inner})"
    content = re.sub(r'tk\.Listbox\((.*?)\)', fix_tk_listbox, content, flags=re.DOTALL)

    if content != original:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed {filename}')
