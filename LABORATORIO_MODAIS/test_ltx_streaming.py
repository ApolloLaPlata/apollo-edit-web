import urllib.request
import json
import base64
import os
import time

url = "https://roxingo--apollo-render-router-api-generate-video.modal.run"
payload = {
    "prompt": "Cinematic drone shot over a highly detailed cyberpunk city, neon lights reflecting on wet streets, flying cars passing by, 8k resolution, photorealistic",
    "model": "ltx",
    "duration": 5,
    "quality": "hd",
    "aspect_ratio": "horizontal"
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

print("🎬 Iniciando geração de vídeo na Modal...")
print(f"Modelo: LTX 2.3 | Resolução: HD | Duração: 5s")
print("Enviando requisição...")

try:
    start_time = time.time()
    with urllib.request.urlopen(req) as response:
        print("✅ Conectado! Aguardando renderização (O keep-alive evitará o timeout)...")
        for line in response:
            line_str = line.decode('utf-8').strip()
            if not line_str:
                print(f"📡 [Ping] Mantendo conexão viva... (Tempo decorrido: {int(time.time() - start_time)}s)")
                continue
            
            print("🚀 Resposta final recebida!")
            result = json.loads(line_str)
            
            if "error" in result:
                print("❌ ERRO NA NUVEM:", result["error"])
                if "traceback" in result:
                    print(result["traceback"])
            else:
                video_b64 = result.get("video_base64")
                if video_b64:
                    video_data = base64.b64decode(video_b64)
                    out_path = os.path.join(os.path.dirname(__file__), "teste_ltx_streaming_hd.mp4")
                    with open(out_path, "wb") as f:
                        f.write(video_data)
                    print(f"🎉 SUCESSO! Vídeo de {len(video_data)/1024/1024:.2f} MB salvo em: {out_path}")
                else:
                    print("❌ Falha: video_base64 não encontrado na resposta.")
            break
except Exception as e:
    print("❌ Erro na requisição HTTP:", e)
