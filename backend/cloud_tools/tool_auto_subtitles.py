import sys
import whisper

def generate_subtitles(input_path, output_srt_path, model_size="tiny"):
    print(f"[ToolSubtitles] Carregando modelo Whisper ({model_size})...")
    model = whisper.load_model(model_size)
    print(f"[ToolSubtitles] Transcrevendo {input_path}...")
    result = model.transcribe(input_path)
    
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(result["segments"], start=1):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()
            
            # Format to SRT timestamp 00:00:00,000
            def format_time(seconds):
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                s = int(seconds % 60)
                ms = int((seconds - int(seconds)) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
                
            srt_file.write(f"{i}\n")
            srt_file.write(f"{format_time(start)} --> {format_time(end)}\n")
            srt_file.write(f"{text}\n\n")
            
    print(f"[ToolSubtitles] Concluido: {output_srt_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tool_auto_subtitles.py <input_video_or_audio> <output_srt>")
        sys.exit(1)
        
    generate_subtitles(sys.argv[1], sys.argv[2])
