import os
import time
import requests
from dotenv import load_dotenv

# Caso a pessoa não tenha instalado a sdk, evitamos crash
try:
    from lightning_sdk import Studio
except ImportError:
    Studio = None

load_dotenv()

class LightningWatchdog:
    """
    O Cão de Guarda do Apollo.
    Responsável por gerenciar as instâncias da Lightning AI (Acordar, Checar, Desligar).
    """
    def __init__(self):
        self.user_id = os.getenv("LIGHTNING_USER_ID", "")
        self.api_key = os.getenv("LIGHTNING_API_KEY", "")
        self.teamspace = os.getenv("LIGHTNING_TEAMSPACE", "v5est") # Default do username provável
        
        # O SDK da Lightning puxa as vars de ambiente automaticamente se estiverem setadas
        os.environ["LIGHTNING_USER_ID"] = self.user_id
        os.environ["LIGHTNING_API_KEY"] = self.api_key

    def is_sdk_available(self):
        return Studio is not None and self.api_key != ""

    def wake_up(self, studio_name: str) -> bool:
        """
        Envia o sinal de Start para a máquina e aguarda ela reportar que ligou.
        Retorna True se estiver ligada/ligou com sucesso, False em erro.
        """
        if not self.is_sdk_available():
            print("[Watchdog] ❌ SDK da Lightning não instalado ou API KEY não configurada.")
            return False
            
        try:
            print(f"[Watchdog] 🌩️ Invocando estúdio '{studio_name}' no teamspace '{self.teamspace}'...")
            
            s = Studio(name=studio_name, teamspace=self.teamspace)
            
            if s.status.name == "Running":
                print(f"[Watchdog] 🟢 O estúdio '{studio_name}' já estava rodando e quente!")
                return True
                
            print(f"[Watchdog] ⏳ O estúdio está dormindo. Iniciando a ignição do hardware...")
            s.start()
            print(f"[Watchdog] 🚀 Ignição concluída. Aguardando servidor de IA responder...")
            return True
            
        except Exception as e:
            print(f"[Watchdog] 🔴 Falha crítica ao tentar acordar a máquina '{studio_name}': {e}")
            print(f"[Dica] Verifique se a variável LIGHTNING_TEAMSPACE está correta no seu .env")
            return False

    def shutdown(self, studio_name: str) -> bool:
        """
        Envia o sinal de Stop para a máquina para interromper as cobranças em Dólar.
        """
        if not self.is_sdk_available():
            return False
            
        try:
            print(f"[Watchdog] 🛑 Enviando comando de desligamento para '{studio_name}'...")
            s = Studio(name=studio_name, teamspace=self.teamspace)
            if s.status.name != "Stopped":
                s.stop()
                print(f"[Watchdog] 💤 Estúdio '{studio_name}' foi dormir. Taxímetro pausado.")
            return True
        except Exception as e:
            print(f"[Watchdog] 🔴 Falha ao desligar a máquina '{studio_name}': {e}")
            return False

# Instância Singleton
watchdog = LightningWatchdog()

if __name__ == "__main__":
    # Teste rápido
    print("Testando o Watchdog...")
    watchdog.wake_up("delicious-tan-kkiu")
