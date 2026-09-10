import sys

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/MEMORIA_ATIVA_SISTEMA.md', 'r', encoding='utf-8') as f:
    text = f.read()

novo_registro = '''
- **[2026-08-26] ARCH UPDATE - AUDIO LAB VIA VERCEL STREAMING & MEDIA MOUNT:** O endpoint udio_lab sofria de 2 problemas fatais na arquitetura Cloud: 1. Timeout do Vercel por silêncio prolongado na geração (Modal demorava 45s+). 2. Vercel abortava o proxying por limitação de 4.5MB devido ao payload de 7MB (Base64) de áudio de 30s. SOLUÇÃO APLICADA: Criada a pasta /media/ no Oracle e montada pelo FastAPI (StaticFiles). O interceptor no modal_proxy da Oracle agora *intercepta* chamadas de áudio, mantém a conexão Vercel viva através de StreamingResponse (yield processing), decodifica o b64 de 7MB, salva um .wav na /media/ e repassa apenas um JSON leve com a udio_url. Frontend refeito para ler o chunk NDJSON do áudio.
'''

if 'ARCH UPDATE - AUDIO LAB VIA VERCEL' not in text:
    text = text.replace('### 4. MEMÓRIA ATIVA (HISTÓRICO)', '### 4. MEMÓRIA ATIVA (HISTÓRICO)\n' + novo_registro)
    with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/MEMORIA_ATIVA_SISTEMA.md', 'w', encoding='utf-8') as f:
        f.write(text)
