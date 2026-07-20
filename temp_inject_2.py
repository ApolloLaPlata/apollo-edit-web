import os
import glob

html_files = glob.glob('web_ui/*.html') + ['hub.html']
scripts_to_inject = [
    '<script src="apollo_notifications.js"></script>',
    '<script src="apollo_quests.js"></script>'
]

for file_path in html_files:
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    injected = False
    for script in scripts_to_inject:
        if script not in content:
            content = content.replace('</body>', f'    {script}\n</body>')
            injected = True
            
    if injected:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Injetado em: {os.path.basename(file_path)}')
