import os, glob

for filepath in glob.glob('public/*.html') + glob.glob('web_ui/*.html'):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'modal_ai_studio.html' in content:
            content = content.replace('modal_ai_studio.html?v=3', 'modal_ai_studio.html?v=4')
            content = content.replace("openAppTab('modal_ai_studio.html'", "openAppTab('modal_ai_studio.html?v=4'")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    except:
        pass
