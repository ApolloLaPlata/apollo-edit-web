---
name: tutorial-das-coisas-veo-corta-continua
description: "Use para escrever ou revisar prompts de video do Tutorial das Coisas com tags [CORTA] e [CONTINUA], continuidade por ultimo frame, SFX diegeticos, ausencia de musica, sanitizacao e consistencia POV fotorrealista."
---

# Tutorial das Coisas - Veo Corta Continua

Use esta skill quando o pedido envolver Veo, VL3, Google Vids, prompts de animacao, automacao de cenas, continuidade ou ultimo frame.

## Entradas esperadas

- tema/cena;
- quantidade de blocos;
- se existe imagem inicial;
- ferramenta alvo: Veo, VL3, Google Vids ou similar;
- se a voz sera TTS externo ou audio nativo;
- proibicoes visuais.

## Saida padrao

- prompt de imagem inicial para cada `[CORTA]`;
- blocos de video separados por linha em branco;
- inputs globais;
- prompt negativo/sanitizacao;
- notas de continuidade.

## Sintaxe

- `[CORTA]`: inicia cena nova e exige imagem/frame base.
- `[CONTINUA]`: continua a partir do ultimo frame gerado.
- Blocos separados por uma linha em branco.
- Padrao do canal: 1 `[CORTA]` + varias `[CONTINUA]`.

Se houver mais de um `[CORTA]`, o numero de prompts de imagem inicial deve bater exatamente com o numero de cortes.

## Conteudo do prompt

Cada bloco deve incluir:

- POV first-person camera;
- ambiente comum e reconhecivel;
- objeto principal centralizado;
- acao visual clara;
- progressao da anomalia;
- SFX diegetico;
- estilo fotorrealista.

Nao inclua musica quando a trilha sera adicionada na edicao.

## Continuidade

Preserve:

- posicao do objeto principal;
- bancada, pia, mesa, fogao ou tela como ancora;
- iluminacao;
- orientacao das maos;
- estado acumulado da anomalia.

Use novo `[CORTA]` somente quando:

- mudar angulo de verdade;
- trocar ambiente;
- iniciar nova referencia visual;
- corrigir ritmo lento com novo impacto visual.

## Sanitizacao

Evite termos que possam soar como dano humano real:

- "person struggles";
- "terrifying";
- "rage and terror";
- "panicked grunt";
- sofrimento fisico explicito.

Prefira:

- "reacting in alarm";
- "dramatic camera shake";
- "quick startled reaction";
- "nearby objects move";
- "environment reacts";
- "the hand pulls back quickly".

## Checklist

- Zero musica?
- Foco em visual e SFX?
- Rosto do Professor fora de quadro?
- Primeiro bloco parece tutorial real?
- O caos nasce do objeto?
- `[CONTINUA]` realmente continua o ultimo frame?

## Guardrails tecnicos

- Nao incluir musica quando o usuario vai editar a trilha depois.
- Nao colocar falas se o fluxo for TTS externo, salvo pedido.
- Nao alternar angulos sem motivo; tutorial real costuma manter camera estavel.
- Nao depender de texto pequeno legivel dentro do video, porque IA pode distorcer letras.
