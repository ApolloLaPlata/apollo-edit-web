import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger("HiveBus")

class HiveBus:
    """
    O Rádio da Colmeia (Event-Driven Message Broker).
    Permite que os agentes enviem e escutem mensagens de forma assíncrona,
    sem precisarem conhecer um ao outro diretamente.
    """
    def __init__(self):
        # topic -> list of callback functions
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, topic: str, callback: Callable):
        """Um agente liga o rádio numa frequência específica para escutar."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        logger.debug(f"[HiveBus] Novo ouvinte na frequência '{topic}'")

    async def publish(self, topic: str, sender: str, payload: Any):
        """Um agente grita no rádio para quem quiser escutar."""
        logger.info(f"📻 [HiveBus] {sender} publicou em '{topic}'")
        
        # Envia para os ouvintes do tópico específico
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                asyncio.create_task(callback(sender, topic, payload))
                
        # Envia para quem ouve TUDO (Ex: O Maestro com o tópico "*")
        if "*" in self.subscribers and topic != "*":
            for callback in self.subscribers["*"]:
                asyncio.create_task(callback(sender, topic, payload))

# Instância Global do Rádio
hive_bus = HiveBus()
