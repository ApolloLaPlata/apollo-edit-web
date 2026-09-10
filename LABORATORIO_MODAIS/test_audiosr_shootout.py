import os
import sys
import modal

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")

try:
    app = modal.App.lookup("apollo-laplata", create_if_missing=False)
except modal.exception.NotFoundError:
    pass

from backend.cloud_tools.engines.xtts_engine import XttsEngine, app

@app.local_entrypoint()
def main():
    print("=== TESTE RAFAEL DESCARGAS: AUDIO SR 48kHz ===")
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_audiosr"
    os.makedirs(save_dir, exist_ok=True)
    
    # Referência Limpa (Fala 3 Normalizada)
    ref_neutra_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\fala_3_rafael_clean.wav"
    with open(ref_neutra_path, "rb") as f:
        ref_rafael_bytes = f.read()

    texto = "Eu já falei mil vezes que o prazo era ontem! Como vocês têm a audácia de me entregar isso agora?!"
    
    engine = XttsEngine()
    
    print(" -> Gerando versão 24kHz (Original do XTTS)...")
    xtts_24k_bytes = engine.generate_voice.remote(
        text=texto,
        reference_audio_bytes=ref_rafael_bytes,
        language="pt",
        temperature=0.65,
        speed=1.0,
        upsample_audiosr=False
    )
    with open(os.path.join(save_dir, "rafael_24kHz_muffled.wav"), "wb") as f:
        f.write(xtts_24k_bytes)
        
    print(" -> Gerando OPÇÃO A: AudioSR Neural (Suave - GS 2.5)...")
    xtts_48k_gs25_bytes = engine.generate_voice.remote(
        text=texto,
        reference_audio_bytes=ref_rafael_bytes,
        language="pt",
        temperature=0.65,
        speed=1.0,
        upsample_audiosr=True,
        audiosr_gs=2.5
    )
    path_48k_suave = os.path.join(save_dir, "rafael_opcaoA_48kHz_suave.wav")
    with open(path_48k_suave, "wb") as f:
        f.write(xtts_48k_gs25_bytes)

    print(" -> Gerando OPÇÃO B: Híbrido Crossover (Grave 24k + Agudo 48k)...")
    import subprocess
    path_24k_puro = os.path.join(save_dir, "rafael_24kHz_muffled.wav")
    path_hibrido = os.path.join(save_dir, "rafael_opcaoB_hibrido.wav")
    
    # Crossover de 6000Hz (6kHz) usando FFmpeg localmente
    # Pega o corpo do original (lowpass) e o ar do neural (highpass) e soma (amix)
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", path_24k_puro,
        "-i", path_48k_suave,
        "-filter_complex",
        "[0:a]lowpass=f=6000[low]; [1:a]highpass=f=6000[high]; [low][high]amix=inputs=2:duration=longest,volume=2[out]",
        "-map", "[out]",
        path_hibrido
    ]
    subprocess.run(cmd, check=True)

    print("=== TESTE CONCLUÍDO ===")
    print(f"Arquivos salvos em: {save_dir}")
