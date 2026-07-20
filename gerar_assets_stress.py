import os
import subprocess
from pathlib import Path
import random

BASE_DIR = Path(__file__).parent.absolute()
STRESS_DIR = BASE_DIR / "Teste_Stress_30Min"

def gerar_assets():
    STRESS_DIR.mkdir(exist_ok=True)
    
    print("[1/3] Gerando áudio de 30 minutos (ruído branco suave + beeps)...")
    audio_path = STRESS_DIR / "audio_30min.wav"
    if not audio_path.exists():
        # Gera 30 min de aevalsrc para não ser 100% silêncio
        cmd_audio = [
            "ffmpeg", "-y", "-f", "lavfi", 
            "-i", "anoisesrc=c=pink:r=44100:a=0.1",
            "-t", "1800", "-c:a", "pcm_s16le", str(audio_path)
        ]
        subprocess.run(cmd_audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("OK: Audio gerado:", audio_path)
    else:
        print("OK: Audio ja existe.")

    print("[2/3] Gerando 50 imagens de B-Roll...")
    broll_dir = STRESS_DIR / "B_Rolls_Nature"
    broll_dir.mkdir(exist_ok=True)
    cores = ["red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta"]
    
    for i in range(1, 51):
        img_path = broll_dir / f"img_{i:02d}.jpg"
        if not img_path.exists():
            cor = random.choice(cores)
            cmd_img = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"color=c={cor}:s=1080x1920",
                "-frames:v", "1", str(img_path)
            ]
            subprocess.run(cmd_img, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"OK: 50 imagens geradas em: {broll_dir}")

    print("[3/3] Criando roteiro de teste...")
    roteiro_path = STRESS_DIR / "roteiro.txt"
    with open(roteiro_path, "w", encoding="utf-8") as f:
        f.write("Este é um teste de stress extremo.\n")
        f.write("O sistema deve aguentar 30 minutos de renderização sem crashar.\n")
        for i in range(1, 50):
            f.write(f"Incrível! Vamos testar B-Roll nature e ver como o sistema se comporta no minuto {i}.\n")
            f.write("Censura: droga! Isso e importante.\n")
    print("OK: Roteiro gerado.")

    print("\nPRONTO PARA O TESTE DE STRESS!")
    print("Para testar no DarkFacil:")
    print("1. Abra a aba 'Mapeamento'")
    print(f"2. Carregue o áudio: {audio_path}")
    print(f"3. Na aba 'Diretor IA', marque 'B-Roll Contextual' e aponte para: {broll_dir}")
    print("4. Cole o texto do roteiro gerado")
    print("5. Clique em Gerar Vídeo e observe o consumo de RAM/Disco e estabilidade!")

if __name__ == "__main__":
    gerar_assets()
