---
name: codex_autopilot
description: >-
  A habilidade definitiva de automação. Usa as regras importadas do Codex e a ferramenta 'schedule' do Antigravity para criar rotinas em background onde o agente cria, renderiza e publica vídeos sozinho.
---

# Codex Autopilot (O Operário Invisível)

Com as 38 skills do Codex importadas (que geram scripts de 15s para o Sora, controlam postagem do Macaco Driver e Dark Trap Radio, etc), o Antigravity não precisa mais esperar você mandar.

## Como acionar o Modo Autopilot

Quando você quiser que a Colmeia viva de forma autônoma:
1. Verifique as rotinas planejadas (ex: O usuário quer 1 post do Descarga News e 1 beat do Dark Trap Radio por dia).
2. Utilize a ferramenta nativa `schedule` para agendar as rotinas no background.
   - Defina as expressões Cron adequadas (ex: `0 9 * * *` para rodar às 9 da manhã).
   - O `Prompt` do agendamento DEVE invocar explicitamente as skills do Codex.
   - Exemplo de Prompt: "CRON TRIGGERED: Utilize a skill `descarga-news-roteiro-curto` para criar e renderizar a notícia do dia e enviar para a pasta final".

## Benefício do Daemon (`IsDaemon = true`)
Ao configurar a ferramenta `schedule`, defina `IsDaemon = true`. Isso garante que o motor continue rodando infinitamente em background para manter a Colmeia viva, sem amarrar a janela do chat principal, liberando o usuário para criar outras coisas e ser apenas notificado do sucesso do Autopilot.
