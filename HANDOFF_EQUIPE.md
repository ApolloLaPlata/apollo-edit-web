# DOCUMENTO DE REPASSE ARQUITETURAL (HANDOFF)
**Gerado por:** Arquiteto Chefe (Apollo Edit Web)
**Para:** Equipe de Agentes Secundários (Autoblog & Broadcaster)
**Data:** 2026-09-21

## DIRETRIZES FUNDAMENTAIS DE ARQUITETURA
1. **Política de LLM (A Regra de Ouro):** Os Agentes de Background (como TrendResearcher, Concierge, Zelador) estão **PROIBIDOS** de usar a API do OpenRouter. O Roteador Central (Account Pool) só deve encaminhar tarefas de patrulha para a Lightning AI. Se a cota esgotar, os agentes hibernam. O OpenRouter é sagrado e restrito à geração direta feita pelo CEO. 
2. **Hugging Face (Motor Central):** O Apollo Backend foi migrado para o Hugging Face (ZeroGPU). O tráfego do Autoblog está sendo roteado no mesmo servidor via Proxy Reverso. O Hugging Face é o Orquestrador Central de IA.

---

## MISSÃO 1: MIGRAÇÃO DO AUTOBLOG PARA O VERCEL (Agente CMS)
O CEO determinou que o Frontend do Autoblog (Next.js) não residirá mais no Oracle nem debaixo do Proxy do Hugging Face. Ele será hospedado de forma nativa no **Vercel** para ganharmos controle sobre domínios e escalabilidade global.
* **O Problema:** Atualmente o código em `/autoblog` utiliza `better-sqlite3` para acessar um banco local (`dev.db`). No Vercel (arquitetura Serverless), isso não funciona pois o disco é efêmero e limpo após cada execução.
* **Seu Objetivo (Agente CMS):** 
  1. Refatorar o acesso ao banco de dados do `/autoblog/src/...`.
  2. Substituir `better-sqlite3` pelo **Supabase** (usando `@supabase/supabase-js` ou Prisma conectado a um pool PostgreSQL da Nuvem).
  3. Instruir o usuário na criação do projeto Vercel (que já está conectado no Github).
  4. Testar o site Vercel para garantir que posts estão sendo lidos/escritos perfeitamente.

---

## MISSÃO 2: A ANTENA DA RÁDIO NO ORACLE (Agente Broadcaster)
O CEO determinou que o servidor Oracle Cloud (ARM, 1GB/12GB RAM) agora é o "Cofre e Transmissor". O servidor Oracle deve ficar "zeradinho" de processos pesados da API Apollo para focar exclusivamente em duas tarefas vitais:
* **Seu Objetivo (Agente Broadcaster):**
  1. Limpar a poluição de rotinas antigas do Oracle e deixá-lo focado em rede/transmissão.
  2. Implementar a **Rádio Dark Trap (Transmissão RTMP via FFmpeg 24/7)** direto da Oracle Cloud. O servidor tem internet veloz e será ideal para live infinita no YouTube sem consumir o PC local do usuário.
  3. Implantar o script auxiliar `ping_despertador.py` no Oracle Cloud. Esse script (já criado pelo Arquiteto) tem a função de bater na porta do Hugging Face a cada 30 minutos, impedindo que o Motor Central hiberne por inatividade.

---
**STATUS:** O terreno está preparado. A base da fundação foi forjada em aço. Executem suas tarefas seguindo este plano.
