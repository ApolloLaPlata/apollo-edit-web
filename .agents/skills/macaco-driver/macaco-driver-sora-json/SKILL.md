---
name: macaco-driver-sora-json
description: Cria prompts JSON curtos para testes do Macaco Driver em Sora ou ferramentas similares, com cenas de 10 a 15 segundos, personagem @macacodrive quando aceito, visual em ingles, falas em PT-BR, timing, audio, guardrails de seguranca e regras de assento/camera. Use para Sora, JSON, prompt cronometrado, video curto de teste ou cena unica de alta qualidade.
---

# Macaco Driver Sora JSON

## Quando usar

Use para testes curtos, geralmente 10 a 15 segundos, quando o usuario quiser prompt estruturado em JSON, cena unica forte, `@macacodrive` ou controle de tempo por campo.

## Entradas esperadas

- Ideia ou conflito.
- Duracao: 10, 12 ou 15 segundos.
- Formato: 9:16, 16:9 ou 1:1.
- Se `@macacodrive` esta aceito pela ferramenta.
- Se audio nativo sera usado ou se o video deve sair mudo.

## Saida padrao

Entregar JSON-like com:

- `title`
- `duration_seconds`
- `aspect_ratio`
- `style`
- `character_reference`
- `global_rules`
- `scenes`
- `audio`
- `negative_instructions`
- `posting_hint`

## Regras do canal

- Usar `@macacodrive` apenas se o usuario confirmar que a referencia funciona.
- Moacaco dirige; humanos ficam no banco de tras; banco dianteiro vazio.
- Camera dashcam interna, fixa, alta e central.
- Visual em ingles; falas em portugues brasileiro.
- Um speaker por vez; sem fala sobreposta.

## Linguagem segura

Prefira:

- `annoyed`, `deadpan`, `uncomfortable`, `tired`.
- `raises one hand to block the light`.
- `gestures for it to stop`.

Evite:

- violencia fisica direta;
- termos de dano corporal;
- personagens licenciados;
- marcas reais quando desnecessarias.

## Checklist de qualidade

- O JSON tem duracao e aspect ratio?
- A primeira cena fixa a identidade do canal?
- As falas cabem no tempo?
- O prompt evita bloqueios previsiveis?
- Ha alternativa se o audio PT-BR falhar?

## Guardrails

- Se o audio em portugues sair ruim, recomendar video mudo + dublagem externa.
- Se animal dirigindo for bloqueado, reduzir movimento e manter interior de carro/rideshare.
- Se upload de face falhar, substituir por descricao detalhada do Moacaco.
