---
name: macaco-driver-veo-dashcam-safe
description: Cria e revisa prompts seguros para Veo, Flow e ferramentas similares em cenas dashcam do Macaco Driver, preservando Moacaco motorista, humanos no banco de tras, banco dianteiro vazio, camera fixa alta, realismo cinematografico, fala PT-BR e sanitizacao anti-bloqueio. Use para prompt blindado, 8 segundos, lip sync, cena interna, erro de assento, erro de camera ou geracao Veo.
---

# Macaco Driver Veo Dashcam Safe

## Quando usar

Use para cenas internas do carro, especialmente prompts de 8 segundos, Veo 3, Flow, VL3, lip sync, audio nativo ou quando modelos erram assento/camera/personagem.

## Entradas esperadas

- Situacao da cena.
- Passageiro/arquetipo.
- Falas desejadas.
- Duracao.
- Ferramenta alvo.
- Nivel de sanitizacao necessario.

## Saida padrao

1. `UNBREAKABLE CORE RULES`
2. `SCENE DESCRIPTION`
3. `CHARACTERS AND POSITIONS`
4. `ACTION TIMELINE`
5. `AUDIO / DIALOGUE`
6. `NEGATIVE PROMPT`
7. `RISK NOTES`

## Regras do canal

- Driver: Moacaco, chimpanze realista de meia-idade, camisa bege amassada.
- Moacaco fica no banco do motorista e controla o volante.
- Passageiros sao humanos e ficam somente no banco de tras.
- Banco dianteiro do passageiro fica vazio.
- Camera fixa, alta, central, perto do retrovisor, estilo dashcam.
- Noite urbana, chuva/neon/asfalto molhado quando fizer sentido.

## Regras de audio

- Falas em portugues brasileiro.
- Visual em ingles.
- Marcar falas com `Character:`.
- Um personagem fala por vez.
- Passageiro geralmente abre o conflito; Moacaco fecha com resposta seca.

## Sanitizacao

Prefira acao neutra:

- `gestures`, `squints`, `raises one hand`, `keeps driving`, `glances at the mirror`.

Evite:

- `slap`, `hit`, `attack`, `blood`, `weapon`, `crash`, `blinded`.

## Checklist de qualidade

- O prompt repete quem dirige?
- O prompt mostra banco traseiro?
- A camera esta fixa e alta?
- As falas estao separadas?
- O visual nao depende de texto pequeno legivel?

## Guardrails

- Nao usar personagem licenciado direto.
- Nao transformar o canal em cartoon 2D.
- Nao fazer Moacaco jovem, limpo, feliz ou heroico.
- Quando um termo bloquear, trocar por descricao visual neutra.
