import requests
import time
import base64
import os

BASE_URL = "https://roxingo--apollo-render-router"

def log(msg):
    print(msg)

def save_b64(b64_str, filename):
    data = base64.b64decode(b64_str)
    out_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_todos_modelos"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "wb") as f:
        f.write(data)
    return path

def testar_todos_os_modelos():
    log("\n[APOLLO] INICIANDO TESTE COMPLETO DOS MODELOS OPEN-SOURCE")
    
    # --- IMAGENS ---
    
    # 1. FLUX SCHNELL
    log("\n[1/5] Testando: FLUX.1-schnell (Imagem Leve/Rápida)...")
    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}-api-generate-image.modal.run",
            json={"model": "flux_schnell", "prompt": "a futuristic racing car, glowing neon tires, synthwave style, 8k resolution"}, timeout=300)
        if r.status_code == 200:
            path = save_b64(r.json()["image_base64"], "1_flux_schnell.png")
            log(f"  ✅ Salvo: {path} ({round(time.time() - t0, 2)}s)")
        else:
            log(f"  ❌ Erro: {r.text}")
    except Exception as e: log(f"  ❌ Falha na conexão: {e}")

    # 2. FLUX DEV
    log("\n[2/5] Testando: FLUX.1-dev (Imagem Pesada/Realista)...")
    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}-api-generate-image.modal.run",
            json={"model": "flux_dev", "prompt": "a highly detailed hyperrealistic portrait of a cyberpunk mechanic working on a robot, neon lighting, cinematic"}, timeout=300)
        if r.status_code == 200:
            path = save_b64(r.json()["image_base64"], "2_flux_dev.png")
            log(f"  ✅ Salvo: {path} ({round(time.time() - t0, 2)}s)")
        else:
            log(f"  ❌ Erro: {r.text}")
    except Exception as e: log(f"  ❌ Falha na conexão: {e}")

    # --- VÍDEOS ---

    # 3. LTX VIDEO
    log("\n[3/5] Testando: LTX-Video (Vídeo Leve/Dinâmico)...")
    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}-api-generate-video.modal.run",
            json={"model": "ltx", "prompt": "A futuristic glowing car drifting around a sharp neon-lit corner, wet road reflections", "num_frames": 121}, timeout=600)
        if r.status_code == 200:
            path = save_b64(r.json()["video_base64"], "3_ltx_video.mp4")
            log(f"  ✅ Salvo: {path} ({round(time.time() - t0, 2)}s)")
        else:
            log(f"  ❌ Erro: {r.text}")
    except Exception as e: log(f"  ❌ Falha na conexão: {e}")

    # 4. WAN 2.1 VIDEO
    log("\n[4/5] Testando: Wan2.1-T2V (Vídeo Pesado/Cinematográfico)...")
    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}-api-generate-video.modal.run",
            json={"model": "wan", "prompt": "Cinematic camera follows a cyberpunk mechanic looking up at a massive futuristic skyscraper, glowing billboards", "num_frames": 41}, timeout=900)
        if r.status_code == 200:
            path = save_b64(r.json()["video_base64"], "4_wan_video.mp4")
            log(f"  ✅ Salvo: {path} ({round(time.time() - t0, 2)}s)")
        else:
            log(f"  ❌ Erro: {r.text}")
    except Exception as e: log(f"  ❌ Falha na conexão: {e}")

    # --- ÁUDIO ---
    
    # 5. STABLE AUDIO
    log("\n[5/5] Testando: Stable Audio Open (Trilha Sonora)...")
    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}-api-generate-audio.modal.run",
            json={"model": "stable_audio", "text": "Cyberpunk racing action music, fast paced synthwave, heavy bass, high energy"}, timeout=300)
        if r.status_code == 200:
            path = save_b64(r.json()["audio_base64"], "5_stable_audio.wav")
            log(f"  ✅ Salvo: {path} ({round(time.time() - t0, 2)}s)")
        else:
            log(f"  ❌ Erro: {r.text}")
    except Exception as e: log(f"  ❌ Falha na conexão: {e}")

    log("\n[APOLLO] TODOS OS TESTES FORAM FINALIZADOS!")

if __name__ == "__main__":
    testar_todos_os_modelos()
