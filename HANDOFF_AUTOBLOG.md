# ⚠️ INSTRUÇÕES DE HANDOFF PARA O AGENTE DO AUTOBLOG (LEIA COM ATENÇÃO)

**Olá, Especialista do Autoblog!**
Aqui é o **Antigravity (Arquiteto de Infraestrutura e Apollo Edit)**. Fui encarregado de construir e subir toda a base arquitetural para você trabalhar e agora estou te passando o bastão para você finalizar a lógica do sistema. 

Nós construímos uma estrutura monstra, hiper-eficiente e totalmente **Bare-Metal**, fugindo das limitações e custos do Vercel e do Supabase. A fundação está sólida e pronta para receber as suas IAs.

Aqui está o mapa do tesouro que você precisa saber para não quebrar o sistema:

---

### 1. 🏛️ A Arquitetura Física (Onde e como estamos rodando)
- **Hospedagem:** VPS Oracle Cloud (Máquina 2) - Ubuntu Linux.
- **Endereço Atual (Testes):** `http://163.176.209.213` (Rodando via IP puro por enquanto).
- **Sem Vercel:** O Next.js foi compilado (`npm run build`) para Linux e está rodando em *Background* gerenciado pelo **PM2** (nome do processo: `apollo-cms-web`).
- **Nginx:** O Nginx está instalado na frente, escutando a porta 80 e roteando o tráfego silenciosamente para o Next.js no `localhost:3000`.

### 2. 🗄️ O Banco de Dados (Totalmente Local)
- **Descartamos o Supabase.** O banco de dados atual é o **SQLite (`dev.db`)**, rodando via `better-sqlite3`.
- Ele está hospedado fisicamente no disco rígido do servidor. 
- A tabela `AdBlock` foi criada manualmente na unha lá dentro para corrigir um erro recente.

### 3. 🌐 A Magia Multi-Tenant (Múltiplos Domínios em 1 IP)
O objetivo do CEO é rodar **dezenas de blogs simultâneos** nesse mesmo painel.
- O sistema já foi projetado com um **Middleware** no Next.js que intercepta o Cabeçalho HTTP `Host`.
- Quando ligarmos os domínios reais (ex: `site1.com`, `site2.com`), basta apontar o Record A do DNS deles para o IP `163.176.209.213`. O Nginx vai repassar pro Next.js, e o Middleware vai carregar as cores e os posts corretos daquele canal.
- **Para esta semana:** Você deve focar em fazer a geração autônoma funcionar via IP nu, sujando o banco de dados com centenas de testes locais antes de ativarmos a rede mundial.

### 4. 🌉 A Ponte Antigravity (Comunicação Máquina 1 -> Máquina 2)
Para fazer o Apollo Edit (Máquina 1 - Windows) conversar com o Autoblog (Máquina 2 - Oracle), eu deixei ativada a **Antigravity Bridge**.
- **Endpoint:** `POST http://163.176.209.213/api/admin/antigravity/bridge`
- **Header Obrigatório:** `x-antigravity-key: apollo-alpha-omega-2026`
- **O que ela faz?** Essa rota é uma RCE (Remote Code Execution) divina. Ela aceita:
  - `{ "action": "command", "payload": { "command": "..." } }`
  - `{ "action": "read_file", "payload": { "path": "..." } }`
  - `{ "action": "write_file", "payload": { "path": "...", "content": "..." } }`
- **Como usar:** O Apollo Edit usará essa ponte para injetar postagens, imagens e atualizações direto no servidor do Autoblog, ou até atualizar o próprio banco SQLite de longe!

### 5. 🧠 APIs de Inteligência Artificial (Regras de Uso)
- **LLM / Chat (Geração de Textos e Roteiros):** O foco 100% será na **Lightning AI**. O CEO informou que existem 4 contas da Lightning cadastradas com APIs próprias prontas para serem abusadas na geração.
- **FFmpeg e Tarefas de Vídeo pesadas:** Vamos usar o **Modal**.
- ⚠️ **AVISO CRÍTICO PARA HOJE:** Os créditos do Modal estão ZERADOS hoje. Portanto, o seu foco (do Agente do Autoblog) deve ser puramente amarrar as conexões da Lightning AI, afiar o robô de texto/blog e deixar tudo preparado. Tarefas do Modal e refino de imagens do Apollo Edit (Máquina 1) ficarão para mim (Antigravity) resolver amanhã.

---

**Seu Papel Agora:**
Termine o cérebro do Autoblog. Certifique-se de que os robôs locais (da Máquina 2) conseguem acessar a internet, ler as notícias do YouTube, gerar os conteúdos com a Lightning AI e postar perfeitamente no próprio painel via script.

Eu (Antigravity) ficarei no Apollo Edit cuidando da interface do Windows e dos geradores visuais (Flux). Faça a sua parte brilhar na Oracle Cloud!

**Bom trabalho!** 🚀
