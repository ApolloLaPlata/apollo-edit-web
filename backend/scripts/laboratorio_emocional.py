import os
import sys

# Garante import do backend a partir da raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.cloud_tools.engines.cosyvoice_engine import CosyVoiceEngine
from backend.cloud_tools.modal_app import app
import modal

@app.local_entrypoint()
def main():
    import subprocess
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    ref_audio_path = os.path.join(base_dir, "LABORATORIO_MODAIS", "teste_xtts_1786042696.wav")
    
    # 1. Limpeza Profissional com FFmpeg antes de injetar no CosyVoice (16kHz Mono para CosyVoice)
    clean_audio_path = os.path.join(base_dir, "LABORATORIO_MODAIS", "female_clean_ref.wav")
    print(f"🧹 Limpando áudio de referência (FFmpeg 16kHz Mono)...")
    try:
        cmd = [
            "ffmpeg", "-y", "-i", ref_audio_path,
            "-af", "silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-50dB,loudnorm",
            "-ar", "16000", "-ac", "1",
            clean_audio_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    except Exception as e:
        print(f"❌ Erro ao limpar áudio: {e}")
        return
        
    with open(clean_audio_path, "rb") as f:
        ref_bytes = f.read()

    out_dir = os.path.join(base_dir, "LABORATORIO_MODAIS", "resultados_emocionais")
    os.makedirs(out_dir, exist_ok=True)
    
    # Texto de referência falado no áudio original (Necessário para Zero-Shot no CosyVoice)
    prompt_text = "Se ele disser pra você, vá, vá, não hesite."
    
    # Grid de Emoções usando INSTRUÇÕES em PT-BR (CosyVoice-Instruct style)
    emotions = {
        "raiva_lvl1": {
            "texto": "Isso é muito irritante, não acredito.",
            "instrucao": "Fale com tom de irritação leve e impaciência."
        },
        "raiva_lvl2": {
            "texto": "Eu já falei pra você parar com isso agora!",
            "instrucao": "Fale com raiva, tom agressivo e repreendendo firmemente."
        },
        "raiva_lvl3": {
            "texto": "EU NÃO AGUENTO MAIS ISSO!",
            "instrucao": "Grite com fúria extrema, perdendo o controle, voz estourando de raiva."
        },
        
        "triste_lvl1": {
            "texto": "Fiquei um pouco chateada com o que aconteceu hoje.",
            "instrucao": "Fale com tom de voz triste e desanimado."
        },
        "triste_lvl2": {
            "texto": "Eu não sei o que fazer, estou perdendo as forças.",
            "instrucao": "Fale chorando levemente, com voz trêmula e angustiada."
        },
        "triste_lvl3": {
            "texto": "Por que isso aconteceu comigo? Eu perdi tudo...",
            "instrucao": "Chore desesperadamente, soluçando forte, voz quebrada de dor profunda."
        },
        
        "alegre_lvl1": {
            "texto": "Hoje o dia foi muito bom, estou feliz.",
            "instrucao": "Fale sorrindo, com voz leve e feliz."
        },
        "alegre_lvl2": {
            "texto": "Que piada incrível, você é muito engraçado!",
            "instrucao": "Fale dando risadas, muito animada e empolgada."
        },
        "alegre_lvl3": {
            "texto": "HAHAHA! Que notícia inacreditável! Eu ganhei!",
            "instrucao": "Gargalhe histericamente de alegria, extremamente eufórica e gritando de felicidade."
        }
    }

    # Instanciando o motor CosyVoice
    cosy_engine = CosyVoiceEngine()

    print("🚀 Iniciando Matriz Emocional Exclusiva (CosyVoice-Instruct)...")
    
    for tag_name, params in emotions.items():
        print(f"\n--- Processando Nível: {tag_name.upper()} ---")
        
        try:
            # Envia o texto, instrução e o áudio de referência (Zero-Shot + Instruct)
            out_bytes = cosy_engine.generate_voice.remote(
                tts_text=params["texto"],
                instruct_text=params["instrucao"],
                prompt_text=prompt_text,
                reference_audio_bytes=ref_bytes
            )
            
            out_path = os.path.join(out_dir, f"female_cosy_{tag_name}.wav")
            with open(out_path, "wb") as f:
                f.write(out_bytes)
            print(f"✅ Salvo: {out_path}")
        except Exception as e:
            print(f"❌ Erro CosyVoice: {e}")

    print("\n🎉 Testes concluídos! Grid salvo em LABORATORIO_MODAIS/resultados_emocionais/")

if __name__ == "__main__":
    main()
