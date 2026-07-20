import sys
import asyncio
import edge_tts

async def generate_tts(text, output_path, voice="pt-BR-AntonioNeural"):
    print(f"[ToolEdgeTTS] Gerando locucao com voz {voice}...")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    print(f"[ToolEdgeTTS] Concluido: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tool_edge_tts.py <\"Texto para falar\"> <output_audio>")
        sys.exit(1)
    
    text = sys.argv[1]
    out_path = sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) > 3 else "pt-BR-AntonioNeural"
    
    asyncio.run(generate_tts(text, out_path, voice))
