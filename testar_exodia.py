import requests
import time
import base64
import os

# Ajuste conforme o subdominio da sua Modal
BASE_URL = "https://roxingo--apollo-render-router"

def log(msg):
    print(msg)

def save_b64(b64_str, filename):
    data = base64.b64decode(b64_str)
    out_dir = "testes_exodia"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "wb") as f:
        f.write(data)
    return path

def testar_tudo():
    log("\n[EXODIA] INICIANDO TESTE DE INTEGRAÇÃO EM MASSA (CAMADA 1)")
    
    # 1. IMAGEM (FLUX SCHNELL)
    log("\n[1/3] Gerando Imagem (FLUX Schnell)...")
    t0 = time.time()
    try:
        r_img = requests.post(
            f"{BASE_URL}-api-generate-image.modal.run",
            json={"model": "flux_schnell", "prompt": "a cinematic portrait of a cyberpunk hacker, neon lights, highly detailed, 8k"},
            timeout=300
        )
        if r_img.status_code == 200:
            res = r_img.json()
            path = save_b64(res["image_base64"], "exodia_img.png")
            log(f"  ✅ Sucesso! Imagem salva em {path} ({round(time.time() - t0, 2)}s)")
        else:
            log(f"  ❌ Erro: {r_img.text}")
    except Exception as e:
        log(f"  ❌ Erro de conexão: {e}")

    # 2. VÍDEO (LTX)
    log("\n[2/3] Gerando Vídeo (LTX Video - 2 segundos)...")
    t0 = time.time()
    try:
        r_vid = requests.post(
            f"{BASE_URL}-api-generate-video.modal.run",
            json={
                "model": "ltx",
                "prompt": "a drone flying through a futuristic city at night, rain, neon signs",
                "num_frames": 65 # Mais leve para o teste rápido
            },
            timeout=600
        )
        if r_vid.status_code == 200:
            res = r_vid.json()
            path = save_b64(res["video_base64"], "exodia_vid.mp4")
            log(f"  ✅ Sucesso! Vídeo salvo em {path} ({round(time.time() - t0, 2)}s)")
        else:
            log(f"  ❌ Erro: {r_vid.text}")
    except Exception as e:
        log(f"  ❌ Erro de conexão: {e}")

    # 3. MÚSICA/SFX (STABLE AUDIO)
    log("\n[3/3] Gerando Trilha Sonora (Stable Audio Open)...")
    t0 = time.time()
    try:
        r_aud = requests.post(
            f"{BASE_URL}-api-generate-audio.modal.run",
            json={"model": "stable_audio", "text": "Cyberpunk synthwave background music, heavy bass, futuristic, 120 bpm"},
            timeout=300
        )
        if r_aud.status_code == 200:
            res = r_aud.json()
            path = save_b64(res["audio_base64"], "exodia_audio.wav")
            log(f"  ✅ Sucesso! Áudio salvo em {path} ({round(time.time() - t0, 2)}s)")
        else:
            log(f"  ❌ Erro: {r_aud.text}")
    except Exception as e:
        log(f"  ❌ Erro de conexão: {e}")

    log("\n[EXODIA] TESTE FINALIZADO!")

if __name__ == "__main__":
    testar_tudo()
