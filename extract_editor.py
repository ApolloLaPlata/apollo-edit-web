import os
import ast
import re

filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\COPIA BACKUP TUTORIAL DAS COISAS\APOLLO_EDIT_WEB 14\temp_restore\aba_edicao_basica.py'

with open(filepath, 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

extracted = []

for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name == 'AbaEdicaoBasica':
        for subnode in node.body:
            if isinstance(subnode, ast.FunctionDef) and subnode.name in ['_gerar_video', '_probe_duration']:
                code = ast.unparse(subnode)
                
                # Cleaning tkinter references and messagebox
                code = code.replace("def _gerar_video(self):", "def gerar_video(payload: dict, callback=None):")
                code = code.replace("def _probe_duration(self, file_path)", "def probe_duration(file_path):")
                code = re.sub(r'self\.status_label\.config\([^)]+\)', 'if callback: callback("status")', code)
                code = re.sub(r'self\.update\(\)', '', code)
                code = re.sub(r'messagebox\.[a-z]+\([^)]+\)', 'raise Exception("Validation Error")', code)
                code = code.replace("self.audio_narrador.get()", "payload.get('audio_narrador')")
                code = code.replace("self.video_paths", "payload.get('videos', [])")
                code = code.replace("self.saida_dir.get()", "payload.get('saida_dir')")
                code = code.replace("self.nome_final.get()", "payload.get('nome_final', 'output.mp4')")
                code = code.replace("self.capa.get()", "payload.get('capa')")
                code = code.replace("self.logo.get()", "payload.get('logo')")
                code = code.replace("self.musica.get()", "payload.get('musica')")
                code = code.replace("self.vinhetas_dir.get()", "payload.get('vinhetas_dir')")
                code = code.replace("self.efeito_zoom.get()", "payload.get('efeito_zoom', False)")
                code = code.replace("self.formato_video.get()", "payload.get('formato_video', '16:9')")
                code = code.replace("self.vol_narrador.get()", "payload.get('vol_narrador', 1.0)")
                code = code.replace("self.vol_musica.get()", "payload.get('vol_musica', 0.1)")
                
                # Replace self property accesses with payload dict access for general vars
                code = re.sub(r'self\.([a-zA-Z0-9_]+)\.get\(\)', r"payload.get('\1')", code)
                code = re.sub(r'self\.([a-zA-Z0-9_]+)', r"payload.get('\1')", code)
                
                extracted.append(code)

final_code = "import os\nimport subprocess\nimport json\nimport uuid\nimport tempfile\n\n"
for func in extracted:
    final_code += func + "\n\n"

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\services\basic_editor.py', 'w', encoding='utf-8') as f:
    f.write(final_code)
print("basic_editor.py generated")
