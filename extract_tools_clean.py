import os
import ast
import re

filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\COPIA BACKUP TUTORIAL DAS COISAS\APOLLO_EDIT_WEB 14\temp_restore\aba_ferramentas.py'

with open(filepath, 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

extracted_functions = []

for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name == 'AbaFerramentas':
        for subnode in node.body:
            if isinstance(subnode, ast.FunctionDef):
                name = subnode.name
                if name.startswith('_') and name not in ['__init__', '_carregar_info_video', '_aplicar_ferramenta', '_processar_capa', '_choose_video', '_criar_stories', '_adicionar_capa']:
                    clean_name = name.lstrip('_')
                    # Find where cmd is defined
                    cmd_node = None
                    for stmt in ast.walk(subnode):
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Name) and target.id == 'cmd':
                                    cmd_node = stmt
                                    break
                    
                    if cmd_node:
                        try:
                            # Try to extract the list of arguments if it's a direct list
                            cmd_str = ast.unparse(cmd_node.value)
                            # Replace UI specific vars with function params
                            cmd_str = cmd_str.replace("self.video_path.get()", "video_path")
                            cmd_str = cmd_str.replace("video_path.get()", "video_path")
                            cmd_str = cmd_str.replace("output_path", "output_path")
                            
                            # For some specific tools we need extra params
                            extra_params = ""
                            if "velocidade" in name:
                                extra_params = ", speed_factor"
                                cmd_str = cmd_str.replace("self.velocidade_var.get()", "speed_factor")
                                cmd_str = cmd_str.replace("float(speed_factor)", "float(speed_factor)")
                            elif "compress" in name or "comprimir" in name:
                                extra_params = ", crf='28'"
                                cmd_str = cmd_str.replace("self.compressao_var.get()", "crf")
                            elif "rotacionar" in name:
                                extra_params = ", transpose_code='1'"
                                cmd_str = cmd_str.replace("self.rotacao_var.get()", "transpose_code")
                            elif "brilho_contraste" in name:
                                extra_params = ", brilho='0', contraste='1'"
                                cmd_str = cmd_str.replace("self.brilho_var.get()", "brilho")
                                cmd_str = cmd_str.replace("self.contraste_var.get()", "contraste")

                            func_def = f"def {clean_name}(video_path, output_path{extra_params}):\n"
                            func_def += f"    cmd = {cmd_str}\n"
                            func_def += f"    result = subprocess.run(cmd, capture_output=True, text=True)\n"
                            func_def += f"    if result.returncode != 0:\n"
                            func_def += f"        raise Exception(f'Erro no FFmpeg: {{result.stderr}}')\n"
                            func_def += f"    return output_path\n"
                            
                            extracted_functions.append(func_def)
                        except Exception as e:
                            pass

final_code = "import os\nimport subprocess\n\n"
final_code += "\n".join(extracted_functions)

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\services\audio_video_tools.py', 'w', encoding='utf-8') as f:
    f.write(final_code)
print("audio_video_tools.py generated")
