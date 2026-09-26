import time
import datetime
import sys
import os

# Adiciona a raiz para poder importar o autoblog_main sem problemas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.bots import autoblog_main

# Frequência do loop em segundos. Ex: 4 horas = 14400 segundos
# Ajustável via Variável de Ambiente
INTERVALO_SEGUNDOS = int(os.getenv("AUTOBLOG_LOOP_INTERVAL", 14400))

def start_daemon():
    print("="*60)
    print("🤖 [AUTO-BLOG DAEMON] Iniciando Moto-Contínuo do Lobo Solitário...")
    print(f"⏱️ [AUTO-BLOG DAEMON] Ciclo de geração: A cada {INTERVALO_SEGUNDOS / 3600:.1f} horas.")
    print("="*60)
    
    while True:
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{agora}] Acordando... Iniciando geração de uma nova pauta e rascunho completo.")
        
        try:
            # Chama o orquestrador principal
            autoblog_main.main()
            print(f"[{agora}] ✅ Geração concluída com sucesso! Rascunho enviado para Fila de Aprovação (approval_queue.db).")
        except Exception as e:
            print(f"[{agora}] ❌ [ERRO CRÍTICO] Falha na iteração do AutoBlog: {e}")
        
        proxima_rodada = datetime.datetime.now() + datetime.timedelta(seconds=INTERVALO_SEGUNDOS)
        print(f"💤 [AUTO-BLOG DAEMON] Dormindo... Próxima geração autônoma agendada para: {proxima_rodada.strftime('%Y-%m-%d %H:%M:%S')}")
        
        time.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    start_daemon()
