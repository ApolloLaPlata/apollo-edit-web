import re
import shutil

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/apollo_modal_engine.py"
shutil.copy(file_path, file_path + ".bak")

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Trocar ace_step_python_engine por ace_step_15_engine
# E AceStepPythonEngine por AceStep15Engine
old_ace = """        elif model == "ace-step":
            from backend.cloud_tools.engines.ace_step_python_engine import AceStepPythonEngine
            engine = AceStepPythonEngine()
            print(f"[Router] Spawning AceStepPythonEngine")
            fc = engine.generate.spawn(style_tags=req.prompt, lyrics=req.lyrics or "", length_seconds=req.duration)"""

new_ace = """        elif model == "ace-step":
            from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine
            engine = AceStep15Engine()
            print(f"[Router] Spawning AceStep15Engine")
            # AceStep 1.5 tem parametros fixos melhores q foram testados
            fc = engine.generate.spawn(style_tags=req.prompt, lyrics=req.lyrics or "", length_seconds=req.duration, steps=64)"""

if old_ace in content:
    content = content.replace(old_ace, new_ace)
else:
    print("WARNING: Ace-Step snippet not exactly matching, attempting regex")
    content = re.sub(
        r'elif model == "ace-step":\n\s+from backend\.cloud_tools\.engines\.ace_step_python_engine import AceStepPythonEngine\n\s+engine = AceStepPythonEngine\(\)\n\s+print\(f"\[Router\] Spawning AceStepPythonEngine"\)\n\s+fc = engine\.generate\.spawn\(style_tags=req\.prompt, lyrics=req\.lyrics or "", length_seconds=req\.duration\)',
        new_ace,
        content
    )

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("apollo_modal_engine.py ACE-Step route patched!")
