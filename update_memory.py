import os
from datetime import datetime

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/MEMORIA_ATIVA_SISTEMA.md"

novo_log = """
### [TESTE DE ESTRUTURA E ARQUITETURA] - {date}
- **Fase 1 (SaaS "Caixa Fechada"):** O usurio validou o modelo de negcios (Vdeos genericos financiados por anuncios/creditos). A interface atual em Next.js e uma placa de ensaio descartavel e sera totalmente reescrita (Mobile-First, simples) apois os testes.
- **Homologacao de Audio (Motores):** 
  - **ACE-Step:** Consagrado para Vozes (Rap, Vocais em PT-BR) devido  sua superioridade no sotaque brasileiro e suporte a Audio de Referencia (Voice Cloning).
  - **MiniMax-Music3:** Consagrado para Instrumentais (EDM, Acustico, Beats Longos) devido sua qualidade cristalina e capacidade nativa de longa duracao (com bypass de letras vazias). O Vocal PT-BR dele sofre de instabilidade de sotaque (influencia luso-africana).
- **Proximos Passos (Audio):** Desenvolver a rota /lab-audio na placa de ensaio Next.js para unificar os motores visualmente. Em seguida, testar Stable Audio 3 para SFX.
""".format(date=datetime.now().strftime("%Y-%m-%d"))

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Inserindo no topo do historico
if "## 4. MEM" in content:
    content = content.replace("## 4. MEM", "## 4. MEMORIA ATIVA (HISTORICO)\n" + novo_log + "\n", 1)
else:
    content += "\n## 4. MEMORIA ATIVA (HISTORICO)\n" + novo_log

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Memoria central atualizada com sucesso.")
