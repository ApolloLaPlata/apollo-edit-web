import math
from typing import Dict, Any

class CheckoutEngine:
    """
    Motor Financeiro de Checkout do Apollo.
    Responsável por calcular o Custo (em Moedas e Cristais) e a Estimativa de Tempo (ETA).
    Ele gera as ofertas de "Gamificação de Nitro" para induzir o usuário ao upgrade.
    """

    def __init__(self):
        # Constantes de Performance (Multiplicadores de tempo baseados na máquina)
        self.MACHINE_SPEED_FACTORS = {
            "free_cpu": 1.0,     # Lento (Base 100%)
            "gpu_t4": 0.5,       # 2x mais rápido (Corta o tempo pela metade)
            "gpu_a100": 0.25     # 4x mais rápido (Corta o tempo para 25%)
        }

        # Constantes de Precificação Base
        self.COST_PER_MINUTE_COINS = 100  # Custo base em Apollo Coins
        self.NITRO_T4_CRYSTALS_PER_MIN = 5  # Cristais por minuto de processamento na T4
        self.NITRO_A100_CRYSTALS_PER_MIN = 12 # Cristais por minuto na A100

    def calculate_budget(self, job_type: str, job_duration_seconds: int, complexity_score: float) -> Dict[str, Any]:
        """
        Recebe os detalhes do job de render e devolve um Orçamento Completo com as opções de Nitro.
        """
        
        # 1. Cálculo Base (Estimativa Crua na Free CPU)
        # Ex: Um vídeo de 60 segundos com complexidade 1.5 demora cerca de 60 * 1.5 * 3 = 270 segundos na CPU.
        base_eta_seconds = (job_duration_seconds * complexity_score * 3.0)
        base_eta_minutes = math.ceil(base_eta_seconds / 60.0)

        # Custo Grátis (Pago com tempo de vida e Moedas)
        base_cost_coins = base_eta_minutes * self.COST_PER_MINUTE_COINS

        # 2. Cálculo do Nitro (T4 - 2x Rápido)
        t4_eta_seconds = base_eta_seconds * self.MACHINE_SPEED_FACTORS["gpu_t4"]
        t4_eta_minutes = math.ceil(t4_eta_seconds / 60.0)
        t4_cost_crystals = t4_eta_minutes * self.NITRO_T4_CRYSTALS_PER_MIN

        # 3. Cálculo do Nitro Master (A100 - 4x Rápido)
        a100_eta_seconds = base_eta_seconds * self.MACHINE_SPEED_FACTORS["gpu_a100"]
        a100_eta_minutes = math.ceil(a100_eta_seconds / 60.0)
        a100_cost_crystals = a100_eta_minutes * self.NITRO_A100_CRYSTALS_PER_MIN

        # 4. Construir Oferta (Upsell)
        return {
            "job_type": job_type,
            "base_eta_seconds": int(base_eta_seconds),
            "options": {
                "free_tier": {
                    "title": "Render Padrão (Free CPU)",
                    "eta_formatted": self._format_eta(base_eta_seconds),
                    "eta_seconds": int(base_eta_seconds),
                    "cost_currency": "apollo_coins",
                    "cost_value": base_cost_coins,
                    "marketing_tag": "Econômico, porém demorado."
                },
                "nitro_tier": {
                    "title": "Turbo (GPU T4)",
                    "eta_formatted": self._format_eta(t4_eta_seconds),
                    "eta_seconds": int(t4_eta_seconds),
                    "cost_currency": "crystals",
                    "cost_value": t4_cost_crystals,
                    "marketing_tag": "2x Mais Rápido!"
                },
                "nitro_master_tier": {
                    "title": "Turbo Master (GPU Ultra)",
                    "eta_formatted": self._format_eta(a100_eta_seconds),
                    "eta_seconds": int(a100_eta_seconds),
                    "cost_currency": "crystals",
                    "cost_value": a100_cost_crystals,
                    "marketing_tag": "4x Mais Rápido (Velocidade Torpedo)!"
                }
            }
        }

    def _format_eta(self, total_seconds: float) -> str:
        """Formata os segundos para uma string amigável ao usuário (ex: 2h 45m)."""
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        
        if minutes >= 60:
            hours = minutes // 60
            remaining_mins = minutes % 60
            return f"{hours}h {remaining_mins}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

# Exemplo de teste da Engine
if __name__ == "__main__":
    engine = CheckoutEngine()
    # Job: Render de 120s de video bruto com complexidade 1.2
    budget = engine.calculate_budget("video_render", 120, 1.2)
    print(budget)
