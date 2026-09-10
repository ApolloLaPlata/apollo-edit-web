---
name: tutorial-das-coisas-sora-json-15s
description: "Use para criar prompts JSON de 10 a 15 segundos para microvideos do Tutorial das Coisas no Sora ou ferramenta similar, com cenas cronometradas, POV fotorrealista, audio em portugues brasileiro, consistencia visual/sonora e dados de postagem."
---

# Tutorial das Coisas - Sora JSON 15s

Use esta skill quando o pedido mencionar Sora, Sora 2, JSON, video de 15 segundos, cenas cronometradas ou microvideo vertical com prompt estruturado.

## Entradas esperadas

- tema pesquisavel;
- duracao: 10s ou 15s;
- ambiente/objeto principal;
- se existe personagem registrado no Sora;
- se precisa de voz interna ou TTS externo;
- restricoes da ferramenta.

## Saida

Entregue:

1. Conceito curto.
2. Prompt JSON.
3. Dados de postagem.
4. Observacoes de consistencia.

## JSON base

Campos recomendados:

- `duration`: `"15s"`
- `format`: `"1080x1920"`
- `style`: `"first-person POV, photorealistic, cinematic, realistic tutorial turning into absurd domestic anomaly"`
- `audio_language`: `"Portuguese (Brazil)"`
- `voice_identity`: descricao curta do Professor Pedante
- `visual_continuity`: ambiente, objeto ancora, maos, iluminacao
- `scene`: lista de blocos com `time`, `camera`, `action`, `effects`, `sound`

## Estrutura de tempo

- `0-3s`: tutorial real e promessa clara.
- `3-7s`: primeira anomalia ligada ao objeto.
- `7-12s`: escalada visual.
- `12-15s`: anti-climax, corte seco ou frase memoravel.

## Regras do canal

- Portugues brasileiro deve estar explicito no audio.
- Evitar rosto fixo do Professor.
- Usar maos, objetos e ambiente como identidade visual.
- A voz precisa soar como o Professor Pedante.
- A anomalia deve nascer da tarefa.
- Nao repetir a virada do video anterior.

## Dados de postagem

Gerar:

- titulo com primeiros 50 caracteres fortes;
- descricao curta com aviso de humor/parodia;
- tags de backend sem `#`, separadas por virgula, perto de 450 caracteres.

## Cuidados

- Se a ferramenta censurar rosto humano, manter POV sem rosto.
- Se a voz sair em outro idioma, reforcar `audio_language` e repetir `Brazilian Portuguese voiceover` nos campos `sound`.
- Se houver personagem registrado pelo usuario, usar a referencia exatamente como ele informar.

## Guardrails

- Nao usar JSON generico de fantasia ou acao; adaptar sempre para tutorial POV realista.
- Nao depender de rosto humano para continuidade.
- Nao repetir estrutura visual de microvideo anterior sem uma nova anomalia.
- Nao colocar musica se o foco for som diegetico e voz do Professor.
