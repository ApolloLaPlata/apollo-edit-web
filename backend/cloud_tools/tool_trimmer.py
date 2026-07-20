import sys
import subprocess

def trim_video(input_path, output_path, start_time, duration):
    # -ss before -i for fast seek
    cmd = [
        "ffmpeg", "-y",
        "-ss", start_time,
        "-i", input_path,
        "-t", duration,
        "-c", "copy",
        output_path
    ]
    print(f"[ToolTrimmer] Executando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"[ToolTrimmer] Concluido: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python tool_trimmer.py <input> <output> <start_time> <duration>")
        sys.exit(1)
    
    trim_video(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
