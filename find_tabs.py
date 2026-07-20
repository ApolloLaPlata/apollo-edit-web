with open(r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias.html', 'r', encoding='latin-1') as f:
    lines = f.readlines()

targets = ['tab-monitor', 'tab-history', 'tab-settings', 'tab-analytics']
for i, l in enumerate(lines):
    for t in targets:
        if 'id="' + t + '"' in l:
            print(f'Line {i+1}: {l.rstrip()[:100]}')
            break
