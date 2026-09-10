# coding: utf-8
import datetime
path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\MEMORIA_ATIVA_SISTEMA.md'
with open(path, 'a', encoding='utf-8') as f:
    f.write("\n\n### DIRETRIZES ESTRATEGICAS E TECNICAS (Sessao Atual)\n")
    f.write("- **O Manifesto Anti-Censura (Descarga News):** O motivo definitivo para a construcao dessa arquitetura na Modal (Qwen 2.5 para imagens, Minimax H3/LTX para video) e a fuga da censura comercial. A infraestrutura DEVE garantir a liberdade criativa para gerar figuras politicas (Trump, Bolsonaro, etc.) e conteudos sensiveis do Descarga News sem os bloqueios das APIs padrao.\n")
    f.write("- **Visao Apollo Flow (Chat UI):** O objetivo do frontend e evoluir para um painel semelhante ao Google Flow. Havera um 'Robo de Livre Criacao' lateral. O usuario conversara em linguagem natural (ex: 'Gere 10 variacoes'), e o robo orquestrara todo o pipeline de Visao, LLM e Qwen automaticamente de forma invisivel.\n")
    f.write("- **Bypass Inteligente de T2I (Text-to-Image):** A arquitetura do Proxy foi desenhada para diferenciar chamadas Text-to-Image de Image-to-Image. Se o usuario NAO enviar imagem de referencia (num_imgs == 0), a chamada ignora o Florence-2 e o Nemotron por completo, garantindo zero latencia para prompts puros.\n")
    f.write("- **Resolucao do 'Dependency Hell' do Florence-2 na Modal:** Para evitar a necessidade de compilar o flash-attn no debian-slim da Modal (o que exige nvcc e cuda-toolkit pesados), cravamos a versao 'transformers==4.40.1'. Isso garante que a Vision Engine suba em segundos sem travar a VRAM ou estourar tempo de build.\n")
    f.write("- **Isolamento de Servidor (Oracle VPS vs Modal):** Foi consolidado que a maquina Oracle (163.176.135.59) opera ESTRITAMENTE como um Nginx/FastAPI Proxy. Processamentos pesados de VRAM sao absolutamente delegados a Modal.\n")
