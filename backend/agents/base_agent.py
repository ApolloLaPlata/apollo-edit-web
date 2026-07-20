import json
import os
import logging
from typing import Dict, Any

from backend.agents.hive_bus import hive_bus

logger = logging.getLogger("BaseAgent")

class BaseAgent:
    """
    Classe Pai para todos os Agentes Administrativos.
    Fornece o sistema unificado de Memória JSON Persistente e Comunicação via Rádio (Bus).
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.is_running = False
        
        # O Diretório de memórias ficará isolado no backend
        self.memory_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'memories')
        os.makedirs(self.memory_dir, exist_ok=True)
        
        self.memory_file = os.path.join(self.memory_dir, f"memory_{self.agent_name.lower()}.json")
        self.memory_data = self.load_memory()

    async def speak(self, topic: str, payload: Any):
        """O agente fala algo no rádio."""
        await hive_bus.publish(topic, self.agent_name, payload)

    def listen(self, topic: str, callback):
        """O agente liga os ouvidos numa frequência do rádio."""
        hive_bus.subscribe(topic, callback)

    def load_memory(self) -> Dict[str, Any]:
        """Lê a memória do disco, ou cria uma nova se não existir"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[{self.agent_name}] Erro ao ler memória: {e}. Criando nova.")
                return self._default_memory()
        else:
            return self._default_memory()

    def save_memory(self):
        """Salva o estado atual da memória no disco"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"[{self.agent_name}] Erro ao salvar memória: {e}")

    def update_memory(self, key: str, value: Any):
        """Atualiza uma chave específica e salva"""
        self.memory_data[key] = value
        self.save_memory()

    def _default_memory(self) -> Dict[str, Any]:
        """Estrutura base da memória"""
        return {
            "agent_id": self.agent_name,
            "status": "idle",
            "last_action": None,
            "alerts": [],
            "data": {}
        }
