---
name: prompt-cenas-video-ia
description: Cria prompts de cenas para IA de video, como Veo, Sora, Runway e ferramentas similares, com camera, sujeito, acao, ambiente, iluminacao, estilo, duracao e formato. Use em qualquer canal que precise transformar roteiro em cenas visuais, clipes de apoio, motion graphics, lip sync, cena horizontal ou vertical.
---

# Prompt Cenas Video IA

## Quando usar

Use para transformar roteiro ou ideia em prompts de video.

## Entradas esperadas

- Canal e estilo visual.
- Trecho do roteiro.
- Formato: 16:9, 9:16 ou 1:1.
- Duracao.
- Ferramenta alvo, se houver.
- Imagem ou frame de referencia, se houver.

## Saida padrao

- Numero da cena.
- Objetivo narrativo.
- Descricao em portugues.
- Prompt em ingles.
- Duracao.
- Formato.
- Observacoes de continuidade.

## Formula

```text
[Style/Technique] of [Subject/Scene], [Action/Movement], [Camera angle/composition], [Aesthetic/Atmosphere], [Technical specs].
```

## Guardrails

- Usar a identidade visual do canal.
- Evitar texto legivel falso, salvo quando solicitado.
- Evitar poluicao visual.
- Para lip sync, separar fala e prompt visual.

## Checklist

- Prompt esta em ingles quando a ferramenta pede ingles.
- Camera, acao e ambiente estao claros.
- Formato e duracao aparecem.
- Cena comunica a ideia do roteiro.
