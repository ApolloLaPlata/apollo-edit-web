import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("StateManager")

class ProjectStateManager:
    """
    Gerencia a arquitetura física de diretórios e o estado compartilhado (JSON) 
    para o Swarm de Agentes baseado no fluxograma (Imagem 2 e 3).
    """
    
    def __init__(self, base_dir: str = "projects"):
        self.base_dir = os.path.abspath(base_dir)
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            
    def get_project_dir(self, project_id: str) -> str:
        return os.path.join(self.base_dir, project_id)

    def initialize_project_structure(self, project_id: str) -> str:
        """
        Cria a raiz do projeto e as pastas bases globais:
        - Memoria Cache
        - Videos Prontos Finalizados
        - memoria_coletiva.json
        """
        proj_dir = self.get_project_dir(project_id)
        os.makedirs(proj_dir, exist_ok=True)
        
        # Pastas Base
        os.makedirs(os.path.join(proj_dir, "Memoria Cache"), exist_ok=True)
        os.makedirs(os.path.join(proj_dir, "Videos Prontos Finalizados"), exist_ok=True)
        
        # Memoria Coletiva JSON
        memoria_file = os.path.join(proj_dir, "memoria_coletiva.json")
        if not os.path.exists(memoria_file):
            initial_state = {
                "project_id": project_id,
                "status": "initialized",
                "historia_base": "",
                "personagens": {},
                "dias": {} # A ser populado dinamicamente
            }
            self.write_memory(project_id, initial_state)
            
        logger.info(f"[StateManager] Projeto '{project_id}' inicializado na raiz física.")
        return proj_dir

    def create_day_structure(self, project_id: str, day_number: int, num_scenes: int, characters: List[str]):
        """
        Gera a árvore de diretórios fractais para um Dia específico (ex: 'Dia 1').
        """
        proj_dir = self.get_project_dir(project_id)
        dia_dir = os.path.join(proj_dir, f"Dia {day_number}")
        os.makedirs(dia_dir, exist_ok=True)
        
        # Criação de Cenas
        for i in range(1, num_scenes + 1):
            os.makedirs(os.path.join(dia_dir, f"Cena {i}"), exist_ok=True)
            
        # Criação da pasta de Narração e personagens
        narracao_dir = os.path.join(dia_dir, "narração")
        os.makedirs(narracao_dir, exist_ok=True)
        for char in characters:
            # Ex: dariusfala, hugofala
            os.makedirs(os.path.join(narracao_dir, f"{char.lower()}fala"), exist_ok=True)
            
        logger.info(f"[StateManager] Árvore criada para Dia {day_number} ({num_scenes} cenas, {len(characters)} personagens).")
        return dia_dir

    def write_memory(self, project_id: str, data: Dict[str, Any]):
        """Atualiza a memória coletiva (JSON), garantindo sincronia entre agentes."""
        memoria_file = os.path.join(self.get_project_dir(project_id), "memoria_coletiva.json")
        with open(memoria_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
    def read_memory(self, project_id: str) -> Dict[str, Any]:
        """Lê a memória coletiva atual."""
        memoria_file = os.path.join(self.get_project_dir(project_id), "memoria_coletiva.json")
        if not os.path.exists(memoria_file):
            return {}
        with open(memoria_file, 'r', encoding='utf-8') as f:
            return json.load(f)

# Instância global do gerenciador de estado
state_manager = ProjectStateManager()
