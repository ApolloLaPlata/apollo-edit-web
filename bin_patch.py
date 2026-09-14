import os

for path in ['public/hub.html', 'web_ui/hub.html', 'public/index.html', 'web_ui/index.html']:
    try:
        with open(path, 'rb') as f:
            b = f.read()
        b = b.replace(b'modal_ai_studio.html?v=3', b'modal_ai_studio.html?v=5')
        b = b.replace(b"openAppTab('modal_ai_studio.html'", b"openAppTab('modal_ai_studio.html?v=5'")
        with open(path, 'wb') as f:
            f.write(b)
    except:
        pass
