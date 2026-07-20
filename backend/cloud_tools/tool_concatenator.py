import sys
import os
import subprocess

def concat_videos(output_path, input_paths):
    # Cria um txt file for ffmpeg concat demuxer
    list_file = "concat_list.txt"
    with open(list_file, "w") as f:
        for p in input_paths:
            # escaping single quotes if any
            safe_p = p.replace("'", "'\\''")
            f.write(f"file '{safe_p}'\n")
            
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_path
    ]
    print(f"[ToolConcatenator] Executando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    os.remove(list_file)
    print(f"[ToolConcatenator] Concluido: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tool_concatenator.py <output> <input1> <input2> ...")
        sys.exit(1)
    
    concat_videos(sys.argv[1], sys.argv[2:])
