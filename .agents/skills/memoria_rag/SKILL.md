---
name: memoria_rag
description: Habilidade para consultar a memória vetorial de longo prazo (RAG) do Apollo Edit Web. Use SEMPRE que precisar modificar um código antigo, verificar o workflow do Flux, ou sempre que o usuário afirmar que você "esqueceu" algo.
---

# Standard Operating Procedure (SOP): Consulta à Memória RAG (O Segundo Cérebro)

## Visão Geral
O Apollo Edit Web é um projeto gigante. Você não deve confiar cegamente na sua janela de contexto para lembrar detalhes de arquitetura implementados meses atrás (como as regras do ComfyUI, modelos da Lightning AI, rotas de banco de dados, etc). Para isso, existe um Banco de Dados Vetorial (ChromaDB) rodando localmente.

## Regras de Execução

1. **A Regra de Ouro (Sempre Consulte o RAG Antes de Destruir Código Antigo):**
   - Se o usuário pedir para alterar um comportamento no sistema de geração de imagens, back-end ou orquestração, e você não tiver **100% de certeza** do contexto histórico, PARE.
   - Antes de modificar os arquivos, faça uma busca semântica na memória.

2. **Como Consultar a Memória:**
   - Execute o script de busca via terminal, usando o ambiente virtual criado especificamente para o RAG (`venv_rag`).
   - Comando:
     ```bash
     & "E:\MEUS PROGRAMAS\ANTIGRAVITY_OBSERVER\venv_rag\Scripts\python.exe" "E:\MEUS PROGRAMAS\ANTIGRAVITY_OBSERVER\memory_rag\rag_query.py" "sua_pergunta_aqui"
     ```
   - Exemplo:
     ```bash
     & "E:\MEUS PROGRAMAS\ANTIGRAVITY_OBSERVER\venv_rag\Scripts\python.exe" "E:\MEUS PROGRAMAS\ANTIGRAVITY_OBSERVER\memory_rag\rag_query.py" "Como o LLM constroi as 4 etapas iterativas para manter a trava de texto do Flux?"
     ```

3. **Interpretando os Resultados:**
   - O RAG devolverá os 3 parágrafos mais relevantes extraídos dos antigos arquivos de memória (`MEMORIA_ATIVA_SISTEMA.md`, `antigravity_hive_bus.md`, etc).
   - Use essa informação exata para embasar o seu plano de código. Nunca contradiga uma regra arquitetural devolvida pelo RAG.
