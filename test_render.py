import os
import sys
import json
import subprocess
import time

BASE_DIR = r"E:\MEUS PROGRAMAS\APOLLO_STUDIO"
os.chdir(BASE_DIR)

print("[1] Gerando Mídias de Teste...")
# Vídeo 1 (3s)
subprocess.run("ffmpeg -y -f lavfi -i testsrc=duration=3:size=1920x1080:rate=30 -c:v libx264 -preset ultrafast dummy_v1.mp4", shell=True)
# Vídeo 2 (3s)
subprocess.run("ffmpeg -y -f lavfi -i color=c=red:duration=3:s=1920x1080:r=30 -c:v libx264 -preset ultrafast dummy_v2.mp4", shell=True)

# Voz (Narração) - 2s de beep a 440Hz
subprocess.run("ffmpeg -y -f lavfi -i sine=frequency=440:duration=2 -c:a aac dummy_voice.m4a", shell=True)
# Música (BGM) - 5s de beep a 1000Hz (mais contínuo)
subprocess.run("ffmpeg -y -f lavfi -i sine=frequency=1000:duration=5 -c:a aac dummy_music.m4a", shell=True)

print("[2] Criando JSON de Exportação...")
timeline_data = {
    "project_name": "teste_e2e",
    "export_quality": "fast",
    "project_settings": {
        "global_filter": "high_contrast"
    },
    "clips": [
        # Vídeos (Com transição entre eles)
        {
            "id": 1, "name": "dummy_v1.mp4", "type": "video", "track": "v1",
            "start_time": 0.0, "duration": 3.0, "trim_in": 0.0,
            "volume": 100, "opacity": 100, "scale": 100, "pos_x": 0, "pos_y": 0
        },
        {
            "id": 2, "name": "dummy_v2.mp4", "type": "video", "track": "v1",
            "start_time": 3.0, "duration": 3.0, "trim_in": 0.0,
            "volume": 100, "opacity": 100, "scale": 100, "pos_x": 0, "pos_y": 0
        },
        # Voz na trilha A1 (Onde entra o Auto-Ducking)
        {
            "id": 3, "name": "dummy_voice.m4a", "type": "audio", "track": "a1",
            "start_time": 1.5, "duration": 2.0, "trim_in": 0.0, "volume": 100
        },
        # Música de Fundo na trilha A2
        {
            "id": 4, "name": "dummy_music.m4a", "type": "audio", "track": "audio-music",
            "start_time": 0.0, "duration": 5.0, "trim_in": 0.0, "volume": 100
        },
        # Texto gerado pela IA
        {
            "id": 5, "name": "Texto de Teste", "type": "text", "track": "t1",
            "start_time": 0.5, "duration": 2.0, "trim_in": 0.0,
            "text_content": "IA NO CONTROLE!", "font_size": 120, "font_color": "#ff00ff", "pos_x": 500, "pos_y": 500
        }
    ],
    "transitions": [
        {
            "id": 101, "type": "fadeblack", "duration": 1.0,
            "left_clip_id": 1, "right_clip_id": 2
        }
    ]
}

export_json_path = os.path.join(BASE_DIR, "timeline_export_test.json")
with open(export_json_path, "w", encoding="utf-8") as f:
    json.dump(timeline_data, f, indent=4)

print("[3] Chamando Renderizador...")
# Executa render_timeline.py
cmd = f"python render_timeline.py \"{export_json_path}\""
result = subprocess.run(cmd, shell=True, capture_output=True, encoding="utf-8", errors="replace")

with open(os.path.join(BASE_DIR, "render_test_log.txt"), "w", encoding="utf-8") as f:
    f.write("--- STDOUT ---\n")
    f.write(result.stdout)
    f.write("\n--- STDERR ---\n")
    f.write(result.stderr)

output_file = os.path.join(BASE_DIR, "timeline_final_render.mp4")
if os.path.exists(output_file):
    size = os.path.getsize(output_file)
    print(f"\n[SUCESSO] Render gerado com sucesso! Tamanho: {size / 1024 / 1024:.2f} MB")
else:
    print("\n[FALHA] Render não foi gerado.")
