---
name: backend_orchestration
description: Habilidade para orquestrar o motor multi-pass de IA para ComfyUI via back-end. Use sempre que o usuário pedir para rodar testes de consistência, criar imagens com múltiplos personagens ou editar scripts como test_multipass_autonomous.py
---

# Standard Operating Procedure (SOP): Orquestração Back-End (O Motor de Consistência)

## Visão Geral
A arquitetura do Apollo Edit Web para gerar imagens de múltiplos personagens NÃO DEPENDE do ComfyUI para separar os personagens. Ela depende inteiramente do **Back-End (Python)** para gerar um prompt altamente descritivo iterativamente (Text-Locking).

## Regras de Execução

1. **A Regra de Ouro (Não Tocar no Workflow):**
   - Sob NENHUMA circunstância altere os JSONs da pasta \Comfyui Workflow API\ para adicionar lógicas novas de inpaint regional. O workflow já faz o inpaint sequencial corretamente baseado puramente no prompt de entrada (usando ReferenceLatent + EmptyLatent).

2. **Geração de Prompt Iterativa (O LLM é o Herói):**
   - O processo possui 4 etapas (ou mais, dependendo do número de atores):
     - Etapa 1: O LLM gera o cenário vazio (Base Scenario).
     - Etapa 2: O LLM reinsere a primeira personagem (ex: Jinx) isolando a sua localização (ex: Left) e travando as características de suas roupas perfeitamente para evitar que o Flux redesenhe ela mal.
     - Etapa 3+: O processo se repete, acumulando os prompts e adicionando novos atores no cenário com as mesmas travas descritivas.

3. **Uso Exclusivo da Lightning AI:**
   - O orquestrador usa a classe \LightningClient\.
   - SEMPRE certifique-se de que o \model\ chamado pela API está mapeado no arquivo \ackend/cloud_tools/lightning_models_catalog.json\. 
   - Modelos recomendados: \openai/gpt-4o\, \openai/o3-mini\, \nthropic/claude-3.5-sonnet\.
   - NUNCA use modelos antigos descontinuados da Lightning (ex: Llama-3-70b).

4. **Tratamento de Custo na Modal:**
   - O Motor roda em Modal e gasta créditos. Nunca rode o endpoint final para gerar imagens aleatórias enquanto estiver no meio do desenvolvimento de código, a menos que o usuário explicitamente dê o comando 'gere a imagem'.
