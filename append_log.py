import os

mem_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\MEMORIA_ATIVA_SISTEMA.md"
bus_path = r"C:\Users\v5est\.gemini\antigravity\brain\9270dd65-160e-47e8-aea2-6a92fd50cfc6\antigravity_hive_bus.md"

mem_entry = "\n- **[2026-08-15] [ROADMAP SAAS B2C]**: O Mestre definiu a estratégia final do Apollo: empacotar a nossa pipeline de vídeo gerado por IA (ComfyUI + Qwen) como um SaaS B2C (concorrente direto do AutoShorts.ai) voltado ao mercado brasileiro, aceitando Pix/Bitcoin. O objetivo de curto prazo é estabilizar a orquestração (Voz -> Música -> Imagem -> Edição) num fluxo contínuo. Assim que a esteira genérica estiver sólida (estilo CapCut), a plataforma será lançada comercialmente e, em seguida, features avançadas (clonagem emocional) serão oferecidas como diferencial matador.\n"

bus_entry = "\n- **[2026-08-15] [CROSS-CHANNEL STRATEGY] PIVOT COMERCIAL**: A Colmeia vai empacotar toda a pipeline autônoma em um SaaS voltado para automação de vídeos genéricos (estilo AutoShorts.ai) monetizado via Pix. Todos os testes atuais (Modal, YuE, Qwen) convergem para orquestrar e polir essa esteira comercial.\n"

with open(mem_path, "a", encoding="utf-8") as f:
    f.write(mem_entry)
    
with open(bus_path, "a", encoding="utf-8") as f:
    f.write(bus_entry)

print("Memória atualizada.")
