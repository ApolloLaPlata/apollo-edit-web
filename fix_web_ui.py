import re

with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the bug with fileUrlAbs
html = html.replace('const fileUrlAbs = result.file_url.startsWith(\'http\') ? result.file_url : ${result.file_url};', 
                    'const fileUrlAbs = result.file_url.startsWith(\'http\') ? result.file_url : https://www.apolloedit.com;')

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
