import json
import sys

# Dicionário de Preços e Modificadores de Prompt
PARTS_DB = {
    "chassi": {
        "enferrujado": {"cost": 0, "prompt": "rusty chassis, broken parts, duct tape"},
        "esportivo": {"cost": 5000, "prompt": "sleek sports chassis, aerodynamic, racing profile"},
        "blindado": {"cost": 10000, "prompt": "heavy armored chassis, military grade, tank-like, bulletproof"}
    },
    "motor": {
        "v4": {"cost": 0, "prompt": "small basic engine, exhaust smoke"},
        "v8": {"cost": 8000, "prompt": "massive V8 engine sticking out of hood, fire exhaust, glowing pipes"},
        "antigravidade": {"cost": 25000, "prompt": "hovering anti-gravity thrusters, sci-fi blue energy glowing from underneath"}
    },
    "pintura": {
        "desgastada": {"cost": 0, "prompt": "faded paint, scratched surface, matte finish, dirty"},
        "neon": {"cost": 3000, "prompt": "bright cyberpunk neon glowing paint, highly reflective, vaporwave aesthetics"},
        "ouro": {"cost": 15000, "prompt": "solid gold plated finish, highly reflective luxury, sparkling, rich"}
    }
}

def generate_forge_prompt(chassi, motor, pintura):
    """
    Calcula o custo total em Gasolina e gera o Prompt Dinâmico de Imagem (SDXL / Midjourney)
    """
    total_cost = 0
    prompts = []

    # Calculate Costs & Collect Prompts
    for category, choice in [("chassi", chassi), ("motor", motor), ("pintura", pintura)]:
        if choice in PARTS_DB[category]:
            part = PARTS_DB[category][choice]
            total_cost += part["cost"]
            prompts.append(part["prompt"])

    # Base Prompt logic based on "Score" (Liters spent)
    base_style = "8-bit pixel art style, isometric view, car game sprite, isolated on solid background, "
    
    if total_cost <= 5000:
        tier_prompt = "a pathetic cheap jalopy car, garbage quality, post-apocalyptic scavenger vehicle, "
        tier_name = "CARROÇA (Baixo Custo)"
        img_ref = "assets/car_level1.png"
    elif total_cost <= 20000:
        tier_prompt = "a customized street racer car, decent quality, heavily modded vehicle, "
        tier_name = "TUNADO (Custo Médio)"
        img_ref = "assets/car_level2.png"
    else:
        tier_prompt = "an ultra luxury futuristic hypercar, elite premium quality, flawless design, masterpiece, "
        tier_name = "LUXO (Alto Custo)"
        img_ref = "assets/car_level3.png"

    # Final Image-to-Image Prompt Composition
    final_prompt = base_style + tier_prompt + ", ".join(prompts) + " --v 6.0 --ar 1:1"

    # Mock Pipeline Response
    response = {
        "total_cost": total_cost,
        "tier": tier_name,
        "final_prompt": final_prompt,
        "recommended_api": "Local ComfyUI (Free) or HuggingFace SDXL",
        "reference_image": img_ref
    }

    return response

if __name__ == "__main__":
    # Teste Rápido no CLI
    if len(sys.argv) == 4:
        chassi = sys.argv[1]
        motor = sys.argv[2]
        pintura = sys.argv[3]
    else:
        # Default test
        chassi = "blindado"
        motor = "antigravidade"
        pintura = "ouro"

    result = generate_forge_prompt(chassi, motor, pintura)
    print(json.dumps(result, indent=4, ensure_ascii=False))
