---
name: observador-economico-notebooklm-prompt
description: Cria prompts mestres para NotebookLM gerar videos-base do canal Observador Economico. Use quando a tarefa pedir prompt para NotebookLM, video-base, aula a partir de PDF/DOC/PPT, materiais SENAC, roteiro de 5000 caracteres, instrucao em PT-BR, ou transformar documentos em aula educacional sobria.
---

# Observador Economico - Prompt NotebookLM

## Objetivo

Criar prompt mestre que controle idioma, tom, estrutura e profundidade para videos-base do NotebookLM.

## Quando usar

Use quando o usuario pedir prompt mestre, video-base, aula por NotebookLM, transformar PDF/DOC/PPT em video, ou preparar material para a ferramenta gerar narracao/slides.

## Entradas esperadas

- Tema.
- Lista de fontes ou documentos.
- Duracao aproximada.
- Conceitos obrigatorios.
- Restricoes de atualidade, se houver.

## Regras criticas

- Exigir portugues do Brasil em narracao, textos e estrutura.
- Definir persona: consultor financeiro/professor universitario.
- Manter tom sobrio, didatico, claro e profissional.
- Pedir exemplos praticos.
- Proibir sensacionalismo e promessa financeira.
- Avisar para nao inventar dados atuais.

## Template curto

```text
INSTRUCAO CRITICA: gere todo o video em portugues do Brasil (PT-BR).

Tema:
[tema]

Papel:
Atue como professor universitario e consultor financeiro senior, com tom sobrio, claro e didatico.

Publico:
Estudantes e profissionais iniciantes de administracao, economia, contabilidade, financas e gestao.

Objetivo:
Ao final, a pessoa deve entender [aprendizado] e aplicar [uso pratico].

Estrutura:
1. Abertura com pergunta realista.
2. Definicao do conceito.
3. Explicacao em blocos.
4. Exemplo pratico.
5. Erro comum.
6. Resumo com 3 pontos.
7. Fechamento discreto.

Incluir:
- [conceito 1]
- [conceito 2]
- [documento/exemplo]

Evitar:
- dados sem fonte;
- promessas financeiras;
- linguagem casual;
- alarmismo;
- invencao de norma, numero ou lei.
```

## Pos-processo

Depois do video-base, gere tambem:

- roteiro de cenas adicionais;
- lista de termos para destaque visual;
- possiveis shorts derivados.

## Saida padrao

- Prompt mestre pronto para colar.
- Observacoes sobre fontes usadas.
- Alertas de checagem atual, se houver.
- Lista de proximos passos de edicao.

## Checklist de qualidade

- PT-BR aparece como instrucao critica.
- Persona vocal esta clara.
- Estrutura esta em blocos.
- Inclui exemplo pratico.
- Proibe inventar dados atuais.
- Nao passa de tamanho inutilmente longo.
