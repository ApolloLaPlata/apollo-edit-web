"""
Apollo Modal - Teste Local de Geracao de Midia
Chama as APIs da Modal e salva os resultados localmente.
"""
import requests
import base64
import os
import sys
import json
import time

BASE_URL = "https://roxingo--apollo-render-router"
OUTPUT_DIR = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_modal_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def log(msg):
    print(msg.encode('ascii', 'replace').decode('ascii'), flush=True)

def ping():
    url = BASE_URL + "-api-ping.modal.run"
    log(f"\n[PING] Testando conexão com a Modal...")
    log(f"[PING] -> {url}")
    try:
        t0 = time.time()
        r = requests.get(url, timeout=30)
        elapsed = round(time.time() - t0, 2)
        log(f"[PING] HTTP Status: {r.status_code} | Latência: {elapsed}s")
        data = r.json()
        log(f"[PING] Resultado: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        log(f"[PING] ERRO: {e}")
        return None

def gerar_imagem():
    url = BASE_URL + "-api-generate-image.modal.run"
    prompt = "A hyper-realistic cinematic portrait of a cyberpunk hacker woman in a neon-lit city at night, 8K, dramatic lighting, photorealistic, ultra detailed"
    steps = 25

    log(f"[FLUX] ============================================")
    log(f"[FLUX] Gerando imagem com FLUX.1-dev na A10G...")
    log(f"[FLUX] URL: {url}")
    log(f"[FLUX] Prompt: {prompt}")
    log(f"[FLUX] Steps: {steps}")
    log(f"[FLUX] Aguardando (pode levar 30-120s na primeira chamada)...")

    try:
        t0 = time.time()
        r = requests.post(
            url,
            json={"prompt": prompt, "steps": steps},
            timeout=600
        )
        elapsed = round(time.time() - t0, 2)
        log(f"[FLUX] HTTP Status: {r.status_code} | Tempo: {elapsed}s")

        if r.status_code != 200:
            log(f"[FLUX] ERRO HTTP: {r.text[:1000]}")
            return False

        data = r.json()

        if data.get("status") == "success" and data.get("image_base64"):
            # Salvar imagem com nome unico
            timestamp = int(time.time())
            filename = f"flux_gerado_{timestamp}.png"
            out_path = os.path.join(OUTPUT_DIR, filename)
            img_bytes = base64.b64decode(data["image_base64"])
            with open(out_path, "wb") as f:
                f.write(img_bytes)
            log(f"[FLUX] [OK] SUCESSO! Imagem salva em: {out_path}")
            log(f"[FLUX] Tamanho: {len(img_bytes)/1024:.1f} KB")
            log(f"[FLUX] Salvo no Volume Modal: {data.get('file_saved', 'N/A')}")
            return True
        else:
            log(f"[FLUX] [ERRO] na geracao: {json.dumps(data, indent=2)[:2000]}")
            return False

    except Exception as e:
        elapsed = round(time.time() - t0, 2) if 't0' in locals() else '?'
        log(f"[FLUX] [EXCECAO] apos {elapsed}s: {type(e).__name__}: {e}")
        return False

def gerar_video():
    url = BASE_URL + "-api-generate-video.modal.run"
    prompt = "A wide cinematic shot of a group of street dancers performing an energetic hip-hop choreography in the middle of a futuristic neon-lit city square at night, glowing wet pavement, smooth steadycam motion, photorealistic, 4k"

    log(f"[LTX]  ============================================")
    log(f"[LTX]  Gerando vídeo com LTX-Video na A10G...")
    log(f"[LTX]  URL: {url}")
    log(f"[LTX]  Prompt: {prompt}")
    log(f"[LTX]  Aguardando (pode levar 2-5 minutos)...")

    try:
        t0 = time.time()
        r = requests.post(
            url,
            json={
                "prompt": prompt,
                "negative_prompt": "worst quality, inconsistent, blurry, deformed, lowres",
                "num_frames": 121
            },
            timeout=900
        )
        elapsed = round(time.time() - t0, 2)
        log(f"[LTX]  HTTP Status: {r.status_code} | Tempo: {elapsed}s")

        if r.status_code != 200:
            log(f"[LTX]  ERRO HTTP: {r.text[:1000]}")
            return False

        data = r.json()

        if data.get("status") == "success" and data.get("video_base64"):
            timestamp = int(time.time())
            filename = f"ltx_gerado_{timestamp}.mp4"
            out_path = os.path.join(OUTPUT_DIR, filename)
            vid_bytes = base64.b64decode(data["video_base64"])
            with open(out_path, "wb") as f:
                f.write(vid_bytes)
            log(f"[LTX]  [OK] SUCESSO! Video salvo em: {out_path}")
            log(f"[LTX]  Tamanho: {len(vid_bytes)/1024/1024:.2f} MB")
            return True
        else:
            log(f"[LTX]  [ERRO]: {json.dumps(data, indent=2)[:2000]}")
            return False

    except Exception as e:
        elapsed = round(time.time() - t0, 2) if 't0' in locals() else '?'
        log(f"[LTX]  [EXCECAO] apos {elapsed}s: {type(e).__name__}: {e}")
        return False

def main():
    log("=" * 55)
    log(f"  APOLLO MODAL - TESTE DE GERACAO LOCAL")
    log("=" * 55)
    log(f"  Output: {OUTPUT_DIR}")

    # 1. Ping
    ping_data = ping()

    if ping_data is None:
        log(f"[FATAL] Nao foi possivel conectar na Modal. Abortando.")
        sys.exit(1)

    models = ping_data.get("models", {})
    flux_ok = models.get("flux_dev", False)
    ltx_ok  = models.get("ltx_video", False)

    log(f"\n[STATUS] Modelos no Volume:")
    log(f"  FLUX.1-dev : {'[OK]' if flux_ok else '[AUSENTE - precisa rodar download]'}")
    log(f"  LTX-Video  : {'[OK]' if ltx_ok else '[AUSENTE]'}")

    resultados = {}

    # 2. Gerar imagem
    if flux_ok:
        resultados["imagem"] = gerar_imagem()
    else:
        log(f"\n[FLUX] [AVISO] Modelo nao encontrado no Volume. Tentando mesmo assim...")
        resultados["imagem"] = gerar_imagem()

    # 3. Gerar vídeo
    if ltx_ok:
        resultados["video"] = gerar_video()
    else:
        log(f"\n[LTX]  [AVISO] Modelo nao encontrado no Volume. Tentando mesmo assim...")
        resultados["video"] = gerar_video()

    # Resumo final
    log(f"\n{'=' * 55}")
    log(f"  RESUMO FINAL")
    log(f"{'=' * 55}")
    log(f"  Imagem FLUX : {'[OK] Gerada!' if resultados.get('imagem') else '[FALHOU]'}")
    log(f"  Video LTX   : {'[OK] Gerado!' if resultados.get('video') else '[FALHOU]'}")
    log(f"  Diretorio   : {OUTPUT_DIR}")
    log(f"{'=' * 55}")

    if resultados.get("imagem"):
        log(f"\n  Arquivo salvo na pasta: {OUTPUT_DIR}")
    if resultados.get("video"):
        log(f"  Arquivo salvo na pasta: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
