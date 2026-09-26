import gradio as gr
import requests
import base64
import tempfile
import os
import glob

# Diretórios padrão de vozes
VOICES_DIRS = [
    r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\voices\xtts",
    r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\testes_tts"
]

def load_standard_voices():
    vozes = []
    for d in VOICES_DIRS:
        if os.path.exists(d):
            # Procura wavs
            for f in glob.glob(os.path.join(d, "*.wav")):
                vozes.append(f)
    return vozes

def get_audio_base64(filepath):
    if not filepath: return ""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def call_webhook(model, text, standard_voice, custom_audio_path, temp, speed):
    try:
        endpoints = {
            "Qwen-TTS": "https://apollolaplata--apollo-api-qwen-tts.modal.run",
            "XTTS": "https://apollolaplata--apollo-api-xtts.modal.run",
            "Moss-TTS": "https://apollolaplata--apollo-api-moss-tts.modal.run",
            "F5-TTS": "https://apollolaplata--apollo-api-f5-tts.modal.run",
            "Fish-Speech": "https://apollolaplata--apollo-api-fish-tts.modal.run",
            "Melo-TTS": "https://apollolaplata--apollo-api-melo-tts.modal.run",
            "ChatTTS": "https://apollolaplata--apollo-api-chattts.modal.run",
            "CosyVoice": "https://apollolaplata--apollo-api-cosyvoice.modal.run",
            "OpenVoice": "https://apollolaplata--apollo-api-openvoice.modal.run"
        }
        
        url = endpoints.get(model)
        if not url:
            return None, f"Modelo {model} não configurado."
            
        payload = {
            "text": text,
            "temperature": float(temp),
            "speed": float(speed),
            "language": "pt",
            "return_raw_wav": True
        }
        
        # Decide qual áudio de referência usar (Customizado tem prioridade)
        ref_audio = custom_audio_path if custom_audio_path else standard_voice
        
        if ref_audio and os.path.exists(ref_audio):
            payload["ref_audio_base64"] = get_audio_base64(ref_audio)
            payload["reference_audio_base64"] = payload["ref_audio_base64"]
            
        print(f"[ElevenLab] Chamando {model} em {url}...")
        res = requests.post(url, json=payload, timeout=300) # Timeout longo p/ MOSS-TTS download
        
        if res.status_code != 200:
            return None, f"Erro {res.status_code}: {res.text}"
            
        ext = ".wav"
        if "ogg" in res.headers.get("content-type", ""):
            ext = ".ogg"
            
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        tmp.write(res.content)
        tmp.close()
        
        return tmp.name, "Sucesso!"
    except Exception as e:
        import traceback
        return None, str(e) + "\n" + traceback.format_exc()

def build_ui():
    vozes_padrao = load_standard_voices()
    
    with gr.Blocks(theme=gr.themes.Base()) as demo:
        gr.Markdown("# 🎙️ Apollo Eleven Lab (Local UI -> Modal)")
        gr.Markdown("Selecione um motor, escolha uma voz padrão ou envie uma nova, e teste a geração!")
        
        with gr.Row():
            with gr.Column():
                model_dd = gr.Dropdown(
                    choices=["XTTS", "Moss-TTS", "F5-TTS", "Fish-Speech", "Qwen-TTS", "Melo-TTS", "ChatTTS", "CosyVoice", "OpenVoice"],
                    value="XTTS",
                    label="Motor TTS (Clonador)"
                )
                
                text_input = gr.Textbox(label="Texto para Falar", lines=4, value="Olá, este é o laboratório de testes do Apollo.")
                
                with gr.Accordion("Configurações", open=False):
                    temp_slider = gr.Slider(0.1, 2.0, value=0.7, label="Temperatura")
                    speed_slider = gr.Slider(0.5, 2.0, value=1.0, label="Velocidade")
                    
                gr.Markdown("### Seleção de Voz")
                standard_voice_dd = gr.Dropdown(
                    choices=vozes_padrao,
                    label="Voz Padrão (Arquivos Locais)",
                    value=vozes_padrao[0] if vozes_padrao else None
                )
                
                custom_audio = gr.Audio(label="Ou Faça Upload de uma Voz Nova (Substitui a padrão)", type="filepath")
                
                gen_btn = gr.Button("🎙️ Gerar Voz na Nuvem (Modal Conta 10)", variant="primary")
                
            with gr.Column():
                audio_out = gr.Audio(label="Áudio Gerado", type="filepath")
                status_out = gr.Textbox(label="Status do Servidor", interactive=False, lines=4)
                
        gen_btn.click(
            fn=call_webhook,
            inputs=[model_dd, text_input, standard_voice_dd, custom_audio, temp_slider, speed_slider],
            outputs=[audio_out, status_out]
        )
        
    return demo

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, inbrowser=True)
