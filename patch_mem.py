import os

memoria_path = 'E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\MEMORIA_ATIVA_SISTEMA.md'
with open(memoria_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_log = '''- **[2026-08-09] BUG DO WEBSOCKET, LOGS E XTTS RESOLVIDOS:** A classe TailLogger (que espelha stdout para o frontend) estava engolindo uma exceção fatal ('reconfigure' inexistente) quando o módulo do ComfyUI importado indiretamente reconfigurava o sys.stdout, travando o event loop ANTES de chamar o LLM e desconectando o cliente do Chat ao Vivo sem logs. Além disso, a chamada do XTTS no socket (modal.Cls...remote.aio) estava travando e dando throw por ser executada fora de um Modal App ativo local. Refatorado para fazer um request HTTP assíncrono transparente direto no Endpoint (https://apollolaplata--apollo-api-xtts.modal.run), estabilizando 100% a pipeline WS e eliminando delays no Event Loop.\n\n'''

content = content + new_log

with open(memoria_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Memoria ativa atualizada")
