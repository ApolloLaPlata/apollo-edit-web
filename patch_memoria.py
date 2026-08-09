# -*- coding: utf-8 -*-
import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\MEMORIA_ATIVA_SISTEMA.md'

with open(file_path, 'a', encoding='utf-8') as f:
    f.write('\n\n### 💡 Registro Estratégico (06 de Agosto de 2026)\n\n- **Arquitetura de Voz Unificada (Kokoro + XTTS):** Implementada a rota `/api/voice/catalog` e `/api/voice/generate` no servidor principal, permitindo que qualquer parte do site escolha vozes híbridas através de um menu Dropdown.\n- **Estabilização do Chat ao Vivo:** O problema de 1006 no WebSocket do Moshi/VoiceChat foi mitigado ao subir a rota `/ws/voice` diretamente no `servidor_web.py` e ensinando o frontend `pocket_app.js` a consumir Blobs binários nativamente pelo WebSocket, sem fechar a conexão.\n')

print('Memoria Atualizada!')
