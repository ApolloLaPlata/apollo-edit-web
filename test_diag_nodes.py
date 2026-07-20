"""
Script de diagnóstico: verifica quais nodes do workflow img2img estão
registrados no ComfyUI e quais estão faltando.
"""
import modal
import sys
import json

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.flux_engine import Flux2ComfyEngine_V2

# Nodes que o workflow img2img usa
REQUIRED_NODES = [
    "BasicGuider", "CLIPLoader", "CLIPTextEncode", "ComfySwitchNode",
    "EmptyFlux2LatentImage", "Flux2Scheduler", "FluxGuidance",
    "GetImageSize", "ImageScaleToTotalPixels", "KSamplerSelect",
    "LoadImage", "LoraLoaderModelOnly", "PrimitiveBoolean", "PrimitiveInt",
    "RandomNoise", "ReferenceLatent", "SamplerCustomAdvanced",
    "SaveImage", "UNETLoader", "VAEDecode", "VAEEncode", "VAELoader"
]

@app.local_entrypoint()
def main():
    print("[DIAG] Verificando nodes registrados no ComfyUI (img2img)...")
    cls = modal.Cls.from_name('apollo-render-router', 'Flux2ComfyEngine_V2')
    engine = cls()
    result = engine.diagnose_nodes.remote(required_nodes=REQUIRED_NODES)
    
    print("\n=== RESULTADO DO DIAGNÓSTICO ===")
    registered = result.get("registered", [])
    missing = result.get("missing", [])
    
    print(f"✅ Registrados ({len(registered)}): {registered}")
    print(f"❌ Faltando ({len(missing)}): {missing}")
