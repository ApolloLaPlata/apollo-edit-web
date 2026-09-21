import time
import requests
import datetime
import sys

# Configuracoes
HF_URL = "https://roxingo-apollo-edit-web.hf.space"
INTERVALO_MINUTOS = 30
MAX_TENTATIVAS = 3

def ping_huggingface():
    tentativas = 0
    while tentativas < MAX_TENTATIVAS:
        try:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Enviando Ping para o Motor Central (Hugging Face)...")
            
            # Request simples GET
            response = requests.get(HF_URL, timeout=15)
            
            if response.status_code == 200:
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Sucesso! Hugging Face acordado. (Status: {response.status_code})")
                return True
            else:
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Alerta: HF retornou status {response.status_code}")
                return False
                
        except Exception as e:
            tentativas += 1
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro ao conectar (Tentativa {tentativas}/{MAX_TENTATIVAS}): {e}")
            time.sleep(5)
            
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚨 FALHA CRÍTICA: Não foi possível acordar o Hugging Face!")
    return False

if __name__ == "__main__":
    print("=====================================================")
    print("🤖 APOLLO DESPERTADOR (PING SCRIPT) INICIADO 🤖")
    print(f"Alvo: {HF_URL}")
    print(f"Frequência: A cada {INTERVALO_MINUTOS} minutos")
    print("=====================================================\n")
    
    ping_huggingface()
    
    while True:
        try:
            time.sleep(INTERVALO_MINUTOS * 60)
            ping_huggingface()
        except KeyboardInterrupt:
            print("\nDespertador desligado. Encerrando.")
            sys.exit(0)
