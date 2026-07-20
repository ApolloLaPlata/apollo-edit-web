import sys
import subprocess

def extract_audio(input_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-q:a", "0",
        "-map", "a",
        output_path
    ]
    print(f"[ToolAudioExtractor] Executando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"[ToolAudioExtractor] Concluido: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tool_audio_extractor.py <input> <output>")
        sys.exit(1)
    
    extract_audio(sys.argv[1], sys.argv[2])
