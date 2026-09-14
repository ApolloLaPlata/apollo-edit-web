import os

with open("LABORATORIO_MODAIS/run_sa3_medium_perfect.py", "r", encoding="utf-8") as f:
    perfect_code = f.read()

# Extrair as funcoes setup e generate
setup_start = perfect_code.find("    @modal.enter()")
generate_start = perfect_code.find("    @modal.method()")
test_start = perfect_code.find("@app.local_entrypoint()")

methods = perfect_code[setup_start:test_start]
# Agora vou sobrescrever a classe StableAudioEngine em stable_audio_engine.py

with open("backend/cloud_tools/engines/stable_audio_engine.py", "r", encoding="utf-8") as f:
    sa3_code = f.read()

class_start = sa3_code.find("class StableAudioEngine:")
sa3_top = sa3_code[:class_start + len("class StableAudioEngine:\n")]

# Trocar generate_audio por generate_audio no methods
methods = methods.replace("def generate(self", "def generate_audio(self")

with open("backend/cloud_tools/engines/stable_audio_engine.py", "w", encoding="utf-8") as f:
    f.write(sa3_top + methods)

print("STABLE AUDIO PATCHED TO PERFECT")
