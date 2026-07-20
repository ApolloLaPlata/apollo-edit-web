import os

files_to_fix = [
    r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\tool_image_gen_flux.py",
    r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\tool_smart_crop.py",
    r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\tool_video_gen_ltx.py",
    r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\flux\main.py",
    r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\ltx\main.py"
]

for file in files_to_fix:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Wrap imports in try/except so they don't crash when imported locally
        # and we don't have to move them all inside functions.
        lines = content.split("\n")
        new_lines = []
        in_try = False
        for line in lines:
            if line.startswith("import torch") or line.startswith("import litserve") or line.startswith("import mediapipe") or line.startswith("from diffusers") or line.startswith("from ltx_video"):
                if not in_try:
                    new_lines.append("try:")
                    in_try = True
                new_lines.append("    " + line)
            elif in_try and not line.strip():
                new_lines.append("    pass")
                new_lines.append("except ImportError:")
                new_lines.append("    pass")
                new_lines.append(line)
                in_try = False
            else:
                if in_try and not (line.startswith("import ") or line.startswith("from ")):
                    new_lines.append("except ImportError:")
                    new_lines.append("    pass")
                    in_try = False
                new_lines.append(line)
                
        if in_try:
            new_lines.append("except ImportError:")
            new_lines.append("    pass")
            
        with open(file, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_lines))
        print(f"Fixed {file}")
