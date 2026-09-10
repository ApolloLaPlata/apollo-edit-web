import re
with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    code = f.read()

code = re.sub(r'preview\.innerHTML\s*=\s*\n\s*<div', 'preview.innerHTML = \n                <div', code)
code = re.sub(r'</div>\n\s*;', '</div>\n              ;', code)

code = re.sub(r'const trackHtml\s*=\s*\n\s*<div', 'const trackHtml = \n                            <div', code)
code = re.sub(r'</a>\n\s*</div>\n\s*;', '</a>\n                            </div>\n                        ;', code)

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(code)
