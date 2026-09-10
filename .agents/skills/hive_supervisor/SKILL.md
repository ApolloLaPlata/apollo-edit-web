---
name: hive_supervisor
description: >-
  Habilidade estratégica para supervisionar a Colmeia de Projetos do Apollo (Dark Trap Radio, Descarga News, Auto-blog). Acione ao lidar com cross-channel, postagens automatizadas e rotinas de múltiplos repositórios.
---

# Hive Supervisor (Controle da Colmeia)

O Apollo Edit Web não é uma ilha. Ele é o cérebro maestro de uma "Colmeia" de projetos (satélites), rodando muitas vezes através de tarefas em background e daemones.

## Canais e Personalidades
1. **Dark Trap Radio:** O foco é música subcultural (Trap). A comunicação, áudio (XTTS) e scripts automatizados aqui devem transpirar uma pegada underground, misteriosa e noturna.
2. **Descarga News:** O foco é jornalismo e notícias. Scripts e gerações devem seguir cadência jornalística, formalidade, e objetividade.
3. **Auto-blog / Broadcast:** Robôs que interagem e postam na web automaticamente. Precisam ser monitorados e alimentados por tarefas assíncronas (Cron Jobs).

## Diretrizes do Supervisor
- **Nunca cruze os fios:** Se estiver trabalhando num script para o Descarga News, não aplique a persona do Dark Trap Radio.
- **RAG Setorial:** O banco de dados (ChromaDB via `apollo-memory`) armazena logs de **todos** os canais. Ao usar `query_apollo_memory`, certifique-se de perguntar o contexto específico, ex: `query="estratégia atual de postagem do Dark Trap Radio"`.
- **Automatização Assíncrona:** A Colmeia vive de cronjobs. Se precisar rodar algo periodicamente, use o comando interno `schedule` (cron) para orquestrar as tarefas nos canais.
