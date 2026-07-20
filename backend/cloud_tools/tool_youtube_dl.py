import sys
import subprocess

def download_youtube(url, output_path):
    print(f"[ToolYoutubeDL] Baixando video em velocidade Gigabit da nuvem: {url}...")
    
    # We use yt-dlp to download the best single mp4 format, or merge best video/audio
    # The -S ext:mp4:m4a forces mp4 output
    cmd = [
        "yt-dlp",
        "--newline",
        "-S", "ext:mp4:m4a",
        "--output", output_path,
        url
    ]
    
    print(f"[ToolYoutubeDL] Executando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"[ToolYoutubeDL] Concluido: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tool_youtube_dl.py <url> <output_path>")
        sys.exit(1)
        
    download_youtube(sys.argv[1], sys.argv[2])
