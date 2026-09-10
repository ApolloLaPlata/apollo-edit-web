import datetime

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/MEMORIA_ATIVA_SISTEMA.md"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
log_entry = f"""
- **{now} - [CORREÇÃO DE ROTA - RESTAURAÇÃO DE PARÂMETROS PERFEITOS]**
  - O usuário alertou corretamente que a cloud engine não estava gerando áudios tão bons quanto os testes locais homologados. As engines do site estavam utilizando parâmetros capados/alucinados (SA3 com 8 passos e ACE-Step 1.0 com CFG fritado). 
  - **Correção Aplicada:** Acessei os scripts locais `run_sa3_medium_perfect.py` e `test_ace_perfect_vocal.py` (que entregaram a qualidade máxima exigida pelo usuário dias atrás) e copiei a matemática **exata** para o servidor na nuvem.
  - O Modal Router agora invoca o `AceStep15Engine` (v1.5) nativamente com CFG de 7.0 e 64 steps, e o Stable Audio voltou a gerar em 100 steps usando `dpmpp-3m-sde` (API não inpaint). Qualidade máxima priorizada acima da velocidade.
"""

if "## 4. MEMÓRIA ATIVA (HISTÓRICO)" in content:
    content = content.replace("## 4. MEMÓRIA ATIVA (HISTÓRICO)", "## 4. MEMÓRIA ATIVA (HISTÓRICO)\n" + log_entry)
else:
    content += "\n## 4. MEMÓRIA ATIVA (HISTÓRICO)\n" + log_entry

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Memória atualizada.")
