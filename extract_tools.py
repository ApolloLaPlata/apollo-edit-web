import os
import ast
import re

filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\COPIA BACKUP TUTORIAL DAS COISAS\APOLLO_EDIT_WEB 14\temp_restore\aba_ferramentas.py'

with open(filepath, 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

extracted = []
for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name == 'AbaFerramentas':
        for subnode in node.body:
            if isinstance(subnode, ast.FunctionDef) and subnode.name not in ['__init__', 'criar_interface', '_choose_video', '_carregar_info_video', '_aplicar_ferramenta', '_processar_capa']:
                code = ast.unparse(subnode)
                # Cleaning tkinter
                code = re.sub(r'def\s+[a-zA-Z0-9_]+\s*\(\s*self\s*,?\s*', 'def ' + subnode.name + '(', code)
                code = re.sub(r'self\.\w+\.set\(.*?\)', 'pass', code)
                code = re.sub(r'messagebox\.\w+\(.*?\)', 'pass', code)
                code = re.sub(r'self\.\w+\.update_idletasks\(\)', 'pass', code)
                code = re.sub(r'self\.\w+\.configure\(.*?\)', 'pass', code)
                code = code.replace('self.video_path', 'video_path')
                code = code.replace('self.output_dir', 'output_dir')
                
                # Make them static-like functions expecting video_path and output_dir
                extracted.append(code)

final_code = "import os\nimport subprocess\n\nclass ToolEngine:\n"
for func in extracted:
    # indent inside class
    indented = "\n".join("    " + line for line in func.split("\n"))
    final_code += "\n" + indented + "\n"

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\services\tool_engine.py', 'w', encoding='utf-8') as f:
    f.write(final_code)
print("tool_engine.py generated")
