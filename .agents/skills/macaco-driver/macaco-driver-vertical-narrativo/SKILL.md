---
name: macaco-driver-vertical-narrativo
description: Cria videos verticais do Macaco Driver em estilo 2026 para Shorts, Reels e TikTok, com voz off do Moacaco, roteiro TTS, mapeamento original, prompts de imagem para CORTA, prompts de animacao CORTA/CONTINUA, observacoes de edicao e kit de postagem. Use quando o pedido envolver vertical, retomada, narracao, historia curta, perrengue, Bananada ou producao ate 60 segundos.
---

# Macaco Driver Vertical Narrativo

## Quando usar

Use para videos verticais de 10 a 60 segundos, principalmente quando a historia for narrada pelo Moacaco e a montagem depender de blocos `original:` e prompts `[CORTA]/[CONTINUA]`.

## Entradas esperadas

- Tema, dor real, noticia, relato ou ideia.
- Duracao alvo.
- Plataforma: Shorts, Reels, TikTok ou todas.
- Nivel de caos: rotina, conexao ou caos total.
- Ferramenta alvo, se houver: Veo, Flow, Meta, Sora ou outra.

## Saida padrao

1. `FORMATO E PREMISSA`
2. `ROTEIRO TTS`
3. `MAPEAMENTO ORIGINAL`
4. `PROMPTS DE IMAGEM`
5. `PROMPTS DE ANIMACAO`
6. `KIT DE POSTAGEM`
7. `OBSERVACOES DE EDICAO`

## Processo

1. Escolher uma dor real de motorista/passageiro.
2. Converter em situacao absurda dentro do carro.
3. Escrever voz off curta, rouca e cansada do Moacaco.
4. Criar uma linha `original:` por bloco narrativo.
5. Definir quais blocos iniciam cena com `[CORTA]`.
6. Usar `[CONTINUA]` apenas para estender o ultimo frame.
7. Criar imagem somente para `[CORTA]`.
8. Fechar com postagem e observacoes de ritmo.

## Regras do canal

- Visual em ingles; fala/narracao em portugues brasileiro.
- Moacaco e cinico, lento, grave, cansado, nunca animadinho.
- Primeiro visual precisa sinalizar canal: Moacaco, HB20, dashcam, passageiro, app ou banana.
- A dor real vem antes do absurdo.

## Regras CORTA/CONTINUA

- Prompt de animacao deve comecar exatamente com `[CORTA]` ou `[CONTINUA]`.
- Separar prompts por uma linha em branco.
- `[CORTA]` precisa de prompt de imagem correspondente.
- `[CONTINUA]` nao recebe nova imagem.
- Bloco `original:` de `[CONTINUA]` precisa de texto suficiente para cobrir duracao.

## Checklist de qualidade

- O hook aparece nos primeiros segundos?
- A promessa visual e clara sem explicacao longa?
- O `original:` combina com a duracao pretendida?
- Ha punchline seca do Moacaco?
- Os prompts preservam banco de tras e dashcam?

## Guardrails

- Nao colocar humano dirigindo.
- Nao colocar passageiro no banco da frente por erro.
- Evitar violencia fisica explicita em prompt visual.
- Se cigarro/Derby bloquear, remover o objeto e manter o cansaco visual.
