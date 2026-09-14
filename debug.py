with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('preview.innerHTML =')
if idx != -1:
    print("FOUND!")
    print(repr(content[idx:idx+150]))
else:
    print("NOT FOUND")
