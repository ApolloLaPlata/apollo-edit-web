---
name: perplexity_researcher
description: "Use para delegar pesquisas profundas de arquitetura, parâmetros obscuros ou best-practices ao Perplexity Pro do usuário."
---

# Perplexity Researcher Workflow

O usuário possui acesso ao **Perplexity Pro**, que é a nossa principal arma para investigar caixas-pretas (como documentações não-oficiais de modelos open-source, dicas de comunidade no HuggingFace/Reddit e fóruns de áudio/IA).

Quando você se deparar com uma barreira técnica, falta de documentação ou precisar de "Workarounds da Comunidade" para problemas complexos, **NÃO ADIVINHE E NÃO TENTE ALUCINAR A SOLUÇÃO**.

Em vez disso, ative esta habilidade seguindo o protocolo abaixo:

1. Reconheça a limitação ou a necessidade de "Deep Research".
2. Escreva um bloco de prompt de pesquisa de alta qualidade, isolado em um bloco de código `text`, para que o usuário copie e cole no Perplexity.
3. Peça explicitamente para o usuário trazer a resposta de volta para o chat.

## Como estruturar o Prompt para o Perplexity

O prompt que você vai gerar para o usuário copiar deve conter:
- **Papel e Contexto:** "Atue como um Engenheiro Senior de [Área]..."
- **O Problema Específico:** Detalhe o gargalo técnico exato, mencionando bibliotecas, versões (ex: XTTSv2, Python 3.10) e sintomas.
- **As Perguntas Focadas:** Liste de 2 a 3 perguntas muito específicas que exigem varredura de fóruns e repositórios.
- **Exigência de Solução Prática:** Peça que a resposta traga "Workarounds da comunidade", código aplicável ou parâmetros matemáticos exatos.

## Exemplo de Aplicação
*Usuário:* "O áudio do XTTS está com ruído e cortando no final, como consertar?"
*Agente:* Percebe que não tem a resposta exata e gera o prompt: "Por favor, rode este prompt no Perplexity Pro para investigarmos os parâmetros exatos da comunidade..." (entrega o bloco de texto).
