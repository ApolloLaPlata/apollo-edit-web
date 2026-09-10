---
name: historias-de-7-dias-mascotes-narradores
description: Use para manter Darius, Hugo, Joye e Ephy do Historias de 7 Dias consistentes em funcao narrativa, voz/TTS, aparencia visual, prompts e falas separadas por personagem.
---

# Mascotes Narradores H7D

## Uso

Use quando o pedido envolver os mascotes, narradores, vozes, TTS, fala por personagem, apresentacao do canal, imagem com mascotes, lip sync ou consistencia visual do Historias de 7 Dias.

## Entradas esperadas

- Mascote ou narrador desejado.
- Uso: fala, roteiro, imagem, lip sync, post, abertura, encerramento ou TTS.
- Emocao/cena.
- Limite de tempo ou caracteres, quando houver.
- Referencia visual local, se o usuario apontar uma imagem especifica.

## Funcoes narrativas

- Darius: narrador principal. Abre, encerra, traz misterio, peso tragico e atmosfera.
- Hugo: narrador de grimorio. Explica lore, ambiente, combate e consequencias com autoridade.
- Joye: comentarista. Reage, provoca, quebra a rigidez com energia e surpresa.
- Ephy: quarto mascote em validacao. Nao tratar como oficial pleno sem confirmacao de papel e voz.

## Vozes

- Darius: Verse; calmo, profundo, mistico, enigmatico, cadenciado.
- Hugo: Fable; serio, sabio, grave, autoritario e solene.
- Joye: Coral; infantil, curiosa, animada, reflexiva e brincalhona.

## Aparencia

- Darius: mascote gotico escuro, chifres, asas de sombra, olhos azuis brilhantes, orbe azul.
- Hugo: dragao sabio azul, olhos dourados, manto escuro/dourado, tomo arcano.
- Joye: fada pequena azul/ciano, asas luminosas, cabelo azul, olhos azuis.
- Ephy: coruja arcana/alquimista, manto verde e caldeirao, ainda em validacao.

## Saida padrao

Quando criar roteiro com mascotes, separe as falas:

```text
Darius:
Hugo:
Joye:
```

Quando criar imagem/video, inclua:

- referencia visual do mascote;
- estilo dark fantasy anime gothic;
- formato desejado;
- proibicao de alterar roupa, proporcao, rosto e paleta sem pedido.

## Referencias locais

Consultar quando a tarefa exigir fidelidade visual/voz:

- `G:\YOUTUBE\HISTORIA DE 7 DIAS\Mascotes`
- `G:\YOUTUBE\HISTORIA DE 7 DIAS\MATERIAIS OBRIGATORIOS`
- `G:\YOUTUBE\HISTORIA DE 7 DIAS\CLONAGEM DE VOZ H7D` e a subpasta local de predefinicoes de voz.

## Guardrails

- Nao trocar funcao dos narradores sem pedido.
- Nao usar Ephy como oficial pleno sem confirmacao.
- Nao inventar roupa, idade, paleta ou proporcao quando houver referencia local.
- Em cenas com lip sync, manter falas curtas e naturais.
- Se o pedido misturar varios mascotes em video, reduzir acao e fundo para preservar consistencia.

## Checklist

- A fala de cada mascote corresponde a funcao dele?
- As vozes escolhidas estao coerentes com os presets locais?
- Ephy foi sinalizada como validacao quando necessario?
- A imagem respeita os arquivos de `Mascotes` e `MATERIAIS OBRIGATORIOS`?
- O prompt evita variacao visual desnecessaria?
