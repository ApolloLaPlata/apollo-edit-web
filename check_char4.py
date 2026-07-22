with open('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\web_ui\\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('ROLETA DA SORTE')
if idx != -1:
    print(repr(text[idx-20:idx+20]))
