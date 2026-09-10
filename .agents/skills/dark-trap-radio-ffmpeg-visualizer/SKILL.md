---
name: dark-trap-radio-ffmpeg-visualizer
description: Use para planejar ou gerar workflows FFmpeg de visualizers da Dark Trap Radio em 16:9, 9:16, live longa, beat individual, waveform, spectrum, texto, logo e CTA.
---

# Dark Trap Radio FFmpeg Visualizer

## Quando usar

Use quando o pedido envolver video musical, visualizer, live longa, corte vertical, comando FFmpeg, lote de render ou conversao de formato.

## Entradas esperadas

- Audio: MP3 ou WAV.
- Background: imagem/video ou pasta de imagens.
- Titulo da faixa.
- Formato: 16:9, 9:16 ou ambos.
- Duracao alvo.
- Logo/marca e CTA opcional.

## Saida padrao

- Plano de render.
- Comando FFmpeg ou pseudocomando seguro.
- Nomes de arquivo sugeridos.
- Checklist de teste curto antes do render final.

## Regras do canal

- Preferir FFmpeg/Python direto; evitar MoviePy quando possivel.
- Visual dark/purple com waveform ou spectrum roxo/neon.
- Texto curto, legivel e sem poluir o visual.
- CTA discreto: `License / Stems in description`.

## Filtros relevantes

- `drawtext`: texto.
- `showwaves`: waveform.
- `showspectrum`: spectrum.
- `scale`, `crop`, `pad`: formato.
- `overlay`: logo, waveform ou elementos.

## Checklist de qualidade

- O comando foi testado em trecho curto antes de renderizar horas?
- O audio foi validado com `ffprobe`?
- O texto cabe no formato mobile?
- O visual reforca Dark Trap Radio?
- A saida local sera preservada se a live passar de 12h?

## Guardrails

- Videos acima de 12h podem nao ser arquivados automaticamente pelo YouTube; manter copia local.
- Nao renderizar horas sem teste de 20-60s.
- Usar paths entre aspas no Windows.
- Se houver erro de fonte/drawtext, simplificar texto para ASCII.

## Referencias locais

- `G:\YOUTUBE\_CODEX\canais\dark-trap-radio\formatos.md`
- `G:\YOUTUBE\_CODEX\canais\dark-trap-radio\catalogo-inicial.md`

