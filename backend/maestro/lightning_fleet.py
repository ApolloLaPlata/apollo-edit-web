import time
import random
from typing import List, Dict

class SwarmNode:
    def __init__(self, node_id: str, machine_type: str, status: str = 'stopped'):
        self.node_id = node_id
        self.machine_type = machine_type # 'free_cpu', 'gpu_t4', 'gpu_ultra'
        self.status = status # 'stopped', 'booting', 'warm', 'busy'
        self.last_active = time.time()

class LightningFleetManager:
    """
    Gerencia a frota de micro-máquinas no Lightning AI.
    Roteia as chamadas do Chatbot/TTS dependendo do nível de Nitro escolhido.
    """
    def __init__(self):
        # Estado simulado do Enxame de Máquinas
        self.nodes: List[SwarmNode] = [
            SwarmNode('node_cpu_01', 'free_cpu', 'warm'),
            SwarmNode('node_cpu_02', 'free_cpu', 'stopped'),
            SwarmNode('node_cpu_03', 'free_cpu', 'stopped'),
            SwarmNode('node_t4_01', 'gpu_t4', 'stopped'),
            SwarmNode('node_t4_02', 'gpu_t4', 'stopped'),
            SwarmNode('node_ultra_01', 'gpu_ultra', 'stopped'),
        ]

    def _get_required_machine_type(self, nitro_level: str) -> str:
        if nitro_level == 'nitro':
            return 'gpu_t4'
        elif nitro_level == 'nitro_master':
            return 'gpu_ultra'
        return 'free_cpu'

    def route_request(self, nitro_level: str, payload: Dict) -> Dict:
        """
        Roteia a requisição para a máquina apropriada.
        Se nenhuma estiver 'warm', acorda uma ('stopped' -> 'booting').
        """
        target_type = self._get_required_machine_type(nitro_level)
        
        # Tenta achar uma máquina já quente
        available_nodes = [n for n in self.nodes if n.machine_type == target_type and n.status == 'warm']
        
        if available_nodes:
            selected_node = random.choice(available_nodes)
            print(f"[SwarmManager] Roteando requisição ({nitro_level}) para NÓ QUENTE: {selected_node.node_id}")
            selected_node.status = 'busy'
            # Simula processamento
            result = self._execute_on_node(selected_node, payload)
            selected_node.status = 'warm'
            selected_node.last_active = time.time()
            return result
        
        # Se não tem quente, precisa fazer Cold Boot
        stopped_nodes = [n for n in self.nodes if n.machine_type == target_type and n.status == 'stopped']
        if stopped_nodes:
            selected_node = stopped_nodes[0]
            print(f"[SwarmManager] Cold Boot necessário. Ligando nó: {selected_node.node_id} para ({nitro_level})")
            selected_node.status = 'booting'
            
            # Simula tempo de cold boot (10-15s na vida real, aqui simulamos menos para dev)
            time.sleep(2.0)
            
            selected_node.status = 'busy'
            result = self._execute_on_node(selected_node, payload)
            selected_node.status = 'warm'
            selected_node.last_active = time.time()
            return result
            
        return {"status": "error", "message": "Nenhum nó disponível no cluster solicitado."}

    def _execute_on_node(self, node: SwarmNode, payload: Dict) -> Dict:
        """Simula a execução via SSH/API na máquina alvo."""
        # Se for CPU demora mais, se for GPU é rápido
        delay = 3.0 if node.machine_type == 'free_cpu' else (1.0 if node.machine_type == 'gpu_t4' else 0.2)
        time.sleep(delay)
        return {
            "status": "success", 
            "node_executed": node.node_id,
            "processed_data": "simulated_audio_or_text"
        }

    def garbage_collector(self):
        """
        Verifica máquinas 'warm' ociosas por mais de 5 minutos e desliga 
        para poupar os créditos mensais do Lightning ($60).
        """
        current_time = time.time()
        for node in self.nodes:
            if node.status == 'warm' and (current_time - node.last_active) > 300: # 5 minutos
                print(f"[SwarmManager] GC: Desligando nó inativo para poupar créditos: {node.node_id}")
                node.status = 'stopped'

# Exemplo de uso isolado:
if __name__ == "__main__":
    swarm = LightningFleetManager()
    print(swarm.route_request('free', {"text": "Olá"}))
    print(swarm.route_request('nitro', {"text": "Gera rápido ai"}))
