---
name: historias-de-7-dias-micro-battle-sora
description: Use para criar prompts Sora 2/Veo de Micro Battles do Historias de 7 Dias, com JSON cronometrado de 10-15 segundos, acao unica, camera, efeitos, som, titulo curto, descricao e tags.
---

# Micro Battle Sora H7D

## Uso

Use quando o pedido envolver duelo, batalha curta, boss fight, magia, classe de RPG, cena Sora 2, prompt JSON, Veo 3 ou short visual de impacto para o Historias de 7 Dias.

## Entradas esperadas

- Tema do duelo/cena.
- Duracao: 10-15s por padrao.
- Personagens ou classes envolvidos.
- Tipo de magia, arma, ambiente e virada final.
- Plataforma e formato: padrao vertical 1080x1920.

## Regra central

Uma Micro Battle deve ter uma unica promessa visual. Nao tente contar lore completa: mostre preparacao, choque e consequencia.

Duracao preferencial:

- `10-15s` para teste rapido e alto impacto.
- `3 cenas de 8-10s` quando o usuario pedir sequencia ou extensao.

## JSON padrao

Use ingles no prompt visual:

```json
{
  "duration": "15s",
  "format": "1080x1920",
  "style": "dark fantasy anime gothic, cinematic motion, high contrast lighting",
  "scene": [
    {
      "time": "0-3s",
      "camera": "close-up or slow push",
      "action": "one clear setup action",
      "effects": "arcane particles, mist, glow",
      "sound": "low magical hum"
    },
    {
      "time": "3-9s",
      "camera": "tracking shot or cut to opponent",
      "action": "main clash or spell release",
      "effects": "impact, sparks, rune flash",
      "sound": "rising hit"
    },
    {
      "time": "9-15s",
      "camera": "slow motion or dramatic wide shot",
      "action": "consequence and final visual hook",
      "effects": "shockwave, smoke, glowing fragments",
      "sound": "crescendo fading into silence"
    }
  ]
}
```

## Identidade H7D

- Visual: anime dark gothic fantasy, runas, nevoa, particulas, contraste alto.
- Paleta: preto, azul arcano, dourado, roxo profundo, vermelho rubro quando fizer sentido.
- Temas: mago, arqueiro, paladino, necromante, guerreiro, artefato, maldicao, duelo elemental.
- Evite excesso de personagens; para consistencia, no maximo dois personagens centrais por geracao.

## Saida padrao

Entregue:

- Nome/ideia da cena.
- Prompt JSON.
- Titulo de Shorts com ate 50 caracteres quando possivel.
- Descricao curta.
- Hashtags.
- Tags de backend perto de 450-500 caracteres quando pedido.

## Guardrails

- Usar no maximo dois personagens centrais por geracao, salvo pedido explicito.
- Evitar fala longa; para lip sync, usar uma ou duas falas curtas.
- Manter a cena controlavel: acao simples, fundo claro, camera definida.
- Se usar mascotes, consultar a skill `historias-de-7-dias-mascotes-narradores`.
- Se a cena for parte de uma serie, manter continuidade de roupa, paleta e ferimentos.
- Nao declarar que uma ferramenta especifica renderizara perfeitamente; tratar prompt como direcao de producao.

## Checklist

- A acao principal cabe em 15 segundos?
- O primeiro quadro ja comunica conflito?
- O prompt controla camera, movimento, efeitos e som?
- O final tem imagem memoravel para loop ou replay?
- O JSON e facil de colar/ajustar sem reescrever tudo?
