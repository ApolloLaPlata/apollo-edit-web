# coding=utf-8
import sys

with open('servidor_web_patched.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """          if req.engine.lower() == "moss":
              params["_modelo_override"] = 2"""
              
replacement = """          if req.engine.lower() == "moss":
              params["_modelo_override"] = 2
          elif req.engine.lower() == "qwen":
              params["_modelo_override"] = 5
          elif req.engine.lower() == "xtts":
              params["_modelo_override"] = 6"""

if target in code:
    code = code.replace(target, replacement)
    with open('servidor_web_patched.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Patched servidor_web_patched.py!")
else:
    print("Target not found in servidor_web_patched.py!")

with open('servidor_web_vps.py', 'r', encoding='utf-8') as f:
    code2 = f.read()

if target in code2:
    code2 = code2.replace(target, replacement)
    with open('servidor_web_vps.py', 'w', encoding='utf-8') as f:
        f.write(code2)
    print("Patched servidor_web_vps.py!")
else:
    print("Target not found in servidor_web_vps.py!")
