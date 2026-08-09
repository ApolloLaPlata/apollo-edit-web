import time
import requests
import json
import logging
import threading

logging.basicConfig(level=logging.INFO, format="[CloudSync] %(asctime)s - %(message)s")

class CloudSyncWorker(threading.Thread):
    def __init__(self, endpoint_url="http://127.0.0.1:8000/api/mobile/pending_approvals", interval=15):
        super().__init__(daemon=True)
        self.endpoint_url = endpoint_url
        self.interval = interval
        self.running = True

    def run(self):
        logging.info(f"Iniciando Cloud Sync Worker. Polling a cada {self.interval}s no endpoint {self.endpoint_url}")
        while self.running:
            try:
                # Simula o Polling na nuvem para buscar jobs aprovados pelo Pocket Director
                # O PWA/Mobile deixará os jobs com status='approved' prontos para render
                # No futuro, aqui fará GET em um VPS ou Pocket Director Backend real.
                
                # Exemplo: Buscando localmente só para provar o conceito de polling
                response = requests.get(self.endpoint_url)
                if response.status_code == 200:
                    data = response.json()
                    pending = data.get("data", [])
                    if len(pending) > 0:
                        logging.info(f"⚠️ {len(pending)} tarefas de roteiro aguardando APROVAÇÃO BIOMÉTRICA no Pocket Director.")
                        # Aqui poderia encaminhar via WebSocket ou Push Notification pro celular do usuário.
            except requests.exceptions.ConnectionError:
                pass # Ignora erro silenciosamente se o servidor estiver offline
            except Exception as e:
                logging.error(f"Erro no Cloud Sync Worker: {e}")
            
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        logging.info("Parando Cloud Sync Worker.")

if __name__ == "__main__":
    worker = CloudSyncWorker()
    worker.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        worker.stop()
