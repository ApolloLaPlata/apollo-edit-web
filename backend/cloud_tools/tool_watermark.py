import sys
import subprocess

def watermark_video(input_path, watermark_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-i", watermark_path,
        "-filter_complex", "overlay=W-w-10:H-h-10", # Bottom right by default
        "-codec:a", "copy",
        output_path
    ]
    print(f"[ToolWatermark] Executando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"[ToolWatermark] Concluido: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tool_watermark.py <input_video> <input_image> <output>")
        sys.exit(1)
    
    watermark_video(sys.argv[1], sys.argv[2], sys.argv[3])
