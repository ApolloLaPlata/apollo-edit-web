import sys
import subprocess
import re

def remove_silence(input_path, output_path, silence_thresh="-30dB", silence_duration="0.5"):
    """
    Remove silence using ffmpeg silencedetect and then cutting/concatenating.
    This is a simplified approach using silencedetect to get timestamps.
    For a fully robust solution without re-encoding it requires splitting and merging.
    Here we use a single complex filter to drop audio/video silence (re-encoding needed).
    """
    print(f"[ToolSilenceRemover] Analisando silencios em {input_path}...")
    
    # We will use the silencedemove audio filter, and we need to drop corresponding video frames.
    # The most robust pure-ffmpeg way to do A/V silence removal without complex Python parsing is a bit tricky.
    # We will use Python parsing of silencedetect to build a select/aselect filter.
    
    cmd_detect = [
        "ffmpeg", "-i", input_path,
        "-af", f"silencedetect=noise={silence_thresh}:d={silence_duration}",
        "-f", "null", "-"
    ]
    
    res = subprocess.run(cmd_detect, capture_output=True, text=True)
    out = res.stderr
    
    # Parse silences
    silences = []
    for line in out.splitlines():
        if "silencedetect" in line and "silence_start" in line:
            match = re.search(r"silence_start: ([\d\.]+)", line)
            if match:
                silences.append({"start": float(match.group(1))})
        if "silencedetect" in line and "silence_end" in line:
            match = re.search(r"silence_end: ([\d\.]+)", line)
            if match and silences and "end" not in silences[-1]:
                silences[-1]["end"] = float(match.group(1))
    
    if not silences or "end" not in silences[-1]:
        print("[ToolSilenceRemover] Nenhum silencio encontrado, copiando o arquivo.")
        subprocess.run(["ffmpeg", "-y", "-i", input_path, "-c", "copy", output_path], check=True)
        return

    # Build complex filter
    # This requires re-encoding.
    filter_complex = []
    # If there's no silence, we keep everything. If there's silence, we keep the INVERTED parts.
    keep_segments = []
    last_end = 0.0
    for s in silences:
        if s["start"] > last_end:
            keep_segments.append((last_end, s["start"]))
        if "end" in s:
            last_end = s["end"]
            
    # Assuming the video goes to some large duration, we add the last segment
    # Get total duration
    cmd_dur = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path]
    dur_res = subprocess.run(cmd_dur, capture_output=True, text=True)
    try:
        total_dur = float(dur_res.stdout.strip())
        if last_end < total_dur:
            keep_segments.append((last_end, total_dur))
    except:
        keep_segments.append((last_end, 999999.0)) # Fallback
        
    select_filters = []
    aselect_filters = []
    for start, end in keep_segments:
        select_filters.append(f"between(t,{start},{end})")
    
    select_expr = "+".join(select_filters)
    if not select_expr:
        select_expr = "0"
        
    filter_complex_str = f"[0:v]select='{select_expr}',setpts=N/FRAME_RATE/TB[v];[0:a]aselect='{select_expr}',asetpts=N/SR/TB[a]"
    
    cmd_encode = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-filter_complex", filter_complex_str,
        "-map", "[v]", "-map", "[a]",
        output_path
    ]
    print(f"[ToolSilenceRemover] Executando: {' '.join(cmd_encode)}")
    subprocess.run(cmd_encode, check=True)
    print(f"[ToolSilenceRemover] Concluido: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tool_silence_remover.py <input> <output>")
        sys.exit(1)
    
    remove_silence(sys.argv[1], sys.argv[2])
