with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace preview.innerHTML = \n <div
code = code.replace('preview.innerHTML = \n                <div', 'preview.innerHTML = \n                <div')
code = code.replace('preview.innerHTML = \r\n                <div', 'preview.innerHTML = \r\n                <div')

code = code.replace('</div>\n            ;', '</div>\n            ;')
code = code.replace('</div>\r\n            ;', '</div>\r\n            ;')

# Replace const trackHtml
code = code.replace('const trackHtml = \n                            <div', 'const trackHtml = \n                            <div')
code = code.replace('const trackHtml = \r\n                            <div', 'const trackHtml = \r\n                            <div')

code = code.replace('</a>\n                            </div>\n                        ;', '</a>\n                            </div>\n                        ;')
code = code.replace('</a>\r\n                            </div>\r\n                        ;', '</a>\r\n                            </div>\r\n                        ;')

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(code)
