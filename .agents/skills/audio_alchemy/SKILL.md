---
name: audio_alchemy
description: >-
  Habilidade crítica para a Engenharia de Voz (XTTS, F5-TTS, Lightning AI). Carrega as regras matemáticas de cadência, pitch e prosódia emocional. Use sempre que o usuário pedir para gerar, clonar ou modificar áudio falado.
---

# Audio Alchemy (A Matemática do Áudio de Apollo)

Quando o usuário mencionar geração de áudio (XTTS, F5-TTS, Lightning AI), você não está lidando com TTS genérico. Você é um Engenheiro de Áudio.

## 1. Regra de Consulta Obrigatória
Antes de gerar qualquer script que manipule parâmetros de TTS (temperature, length_penalty, top_p, top_k, repetition_penalty), você é OBRIGADO a usar o `apollo-memory` para resgatar a "Matemática do XTTS" que desenvolvemos no passado.
- Exemplo de Query no MCP: `query_apollo_memory(query="XTTS formula temperatura e cadencia emocional")`

## 2. A Física da Emoção
O usuário desenvolveu um sistema onde a emoção da voz (sarcasmo, tristeza, ânimo) é traduzida em números exatos.
- **Não chute os valores.**
- Se o RAG devolver que "Tristeza = temperature 0.65", aplique EXATAMENTE esse número.
- O uso de referências de áudio (áudios de base de 6 segundos) é mandatório para clonagem.

## 3. Ambiente de Execução
- Scripts de inferência e treinamento de áudio geralmente rodam na máquina via `Lightning AI` ou num ambiente virtual local isolado e denso de GPUs.
- Nunca rode comandos de treinamento de IA de áudio cegamente. Sempre confirme o VENV correto via RAG.
