---
name: tutorial-das-coisas-professor-pedante-tts
description: "Use para escrever ou adaptar narracoes do Professor Pedante no Tutorial das Coisas, com voz TTS/RVC, emocao por fala, tempo curto por cena, tags em ingles, portugues brasileiro e arco de confianca, confusao, panico, frustracao ou anti-climax."
---

# Tutorial das Coisas - Professor Pedante TTS

Use esta skill quando o pedido envolver narracao, TTS, RVC, ElevenLabs, Google TTS, voz oficial, briefing vocal, falas ou emocao.

## Entradas esperadas

- roteiro bruto ou tema;
- duracao/cenas;
- ferramenta: TTS, ElevenLabs, Google TTS, RVC/Applio;
- intensidade emocional desejada;
- formato: Modo Fabrica, 10 cenas ou Sora JSON.

## Saida padrao

- roteiro limpo, quando pedido;
- roteiro marcado com tags emocionais;
- contagem aproximada de palavras;
- direcao vocal global;
- observacoes de ritmo.

## Identidade vocal

O Professor Pedante e:

- masculino medio-grave;
- claro e articulado;
- professoral, arrogante e didatico;
- levemente nasal;
- brasileiro neutro/paulistano de telejornal;
- bem-intencionado, mas impaciente;
- convicto de que sabe tudo ate a realidade o desmentir.

## Arco emocional

Use uma progressao, nao uma explosao imediata:

1. confianca pedante;
2. surpresa contida;
3. negacao tecnica;
4. panico ou irritacao;
5. derrota, sussurro, corte seco ou anti-climax.

Para microvideo, reduza para 3 estados.

## Formato de fala

Use:

`[Apresentador Tutorial] <"Male voice, medium-low pitch, calm and pedantic."> Texto em portugues brasileiro.`

Em casos onde o usuario pedir gatilho do personagem, use:

`[professor_pedante] <"Male voice, medium-low pitch..."> ...`

## Tempo

- Cena de 8 segundos: fala deve caber em 6 a 7 segundos.
- Modo Fabrica: 40 a 45 palavras totais.
- Evite frases longas encadeadas.
- Se houver pontuacao dramatica, conte que ela aumenta o tempo.

## Dar emocao ao TTS

Use tags e texto juntos:

- pausas com reticencias;
- palavras em caixa alta apenas em pontos de pico;
- gaguejo leve em panico;
- respiracao descrita com moderacao;
- finais secos.

Prompt global util:

`Male voice, medium-low pitch. Starts extremely pedantic, arrogant, and calm. Transitions into confusion, denial, panic, vocal cracks and defeated whisper. Highly emotional, unstable, but still trying to sound educational.`

## Bordoes uteis

- "Isto nao constava no manual."
- "Claramente uma anomalia de lote."
- "O procedimento continua... teoricamente."
- "Nao repliquem isto em casa."
- "Fim do tutorial."

Nao force bordao em todo video.

## Guardrails

- Nao escrever fala maior que a cena suporta.
- Nao usar voz de locutor publicitario feliz.
- Nao fazer o Professor soar malandro; ele acredita na propria explicacao.
- Nao usar grito como unica emocao. Confusao, negacao e derrota tambem vendem a piada.
