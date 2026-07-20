import re

filepath = r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix duplicates
clean_scripts = '''    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="noticias_core.js"></script>
    <script src="scripts_logic.js"></script>
    <script src="strategy_logic.js"></script>
    <script src="dashboard_logic.js"></script>
    <script src="radar_logic.js"></script>
    <script src="studio_logic.js"></script>
</body>'''

content = re.sub(r'    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/.*</body>', clean_scripts, content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed scripts!')
