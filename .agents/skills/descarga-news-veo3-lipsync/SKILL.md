---
name: descarga-news-veo3-lipsync
description: Use para criar blocos VEO 3/lip sync do Descarga News, com cenas de 8s, prompt visual em ingles, fala em portugues, extensoes e cortes para Shorts.
---

# Descarga News VEO 3 Lip Sync

## Uso

Use quando o pedido envolver VEO 3, lip sync, personagem falando direto, cena cinematografica, jornal horizontal premium ou blocos de video com audio embutido.

## Matematica

- Take base: 8 segundos.
- 15-20 palavras por take de 8s.
- Mais de 20 palavras: `Take Base + 1 Extensao`.
- Mais de 40 palavras: `Take Base + 2 Extensoes`.
- Monologo forte de 30-50 palavras pode receber `[ALERTA DE CORTE PARA SHORT]`.

## Bloco padrao

```text
[CENA VISUAL]
Tipo: Gancho Inicial | Bancada | B-Roll de Noticia | Comercial Falso
Acao/Duracao: Take Unico de 8s | Take Base + 1 Extensao | Take Base + 2 Extensoes
Prompt para IA de Video (em ingles): ...

[AUDIO E DIALOGO]
Personagem: ...
[Estado Emocional TTS]: English acting direction...
Fala (Portugues): ...
```

## Regras visuais

- Bancada = privada, microfone improvisado, esgoto, azulejo sujo, papel higienico, neon de noticiario barato.
- Gancho inicial = caos em tela cheia antes da bancada.
- Usar camera shake, zoom rapido, sirene, documento molhado, dinheiro voando e agua de esgoto quando o tema pedir impacto.
- Para politica sensivel, usar descricoes genericas: powerful politician, bald judge, corrupt official, wealthy banker.

## Regras narrativas

- Nao transformar VEO em leitura parada.
- Cada cena precisa ter acao visual clara.
- Alternar bancada, B-roll, falso comercial e interrupcao tecnica.
- Em horizontal longo, marcar pelo menos dois cortes fortes para Shorts.
