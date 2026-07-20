import os
import json
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # Permite requisições do Apollo Web UI

# ---------------------------------------------------------
# LIGHTNING SERVER - MOTOR DE INFERÊNCIA DO MASCOTE
# ---------------------------------------------------------
# Este micro-serviço roda no Servidor Lightning (Latência Baixa).
# Responsabilidades: Whisper (STT) -> LLM (Raciocínio) -> TTS (Fala)

# Mocks para IAs enquanto os modelos pesados não estão na memória
def mock_whisper_stt(audio_base64):
    """Simula a conversão de Áudio para Texto (Speech-to-Text)."""
    # Na implementação real, chamar openai.Audio.transcribe ou Whisper local
    time.sleep(0.5)
    return "Ei, me mostre os meus copilotos."

def mock_llm_reasoning(user_text, character_prompt):
    """Simula o LLM (Gemini/GPT-4) recebendo o texto e decidindo a ação."""
    time.sleep(1.0)
    
    # Prompt System real instruirá o LLM a sempre retornar JSON
    # Exemplo de payload esperado:
    response_json = {
        "text": "Com certeza, chefe! Abrindo o Mascot Forge para você dar uma olhada na frota.",
        "emotion": "happy",
        "action": {
            "type": "navigate",
            "payload": {
                "file": "forge", 
                "title": "Mascot Forge"
            }
        }
    }
    
    if "copiloto" not in user_text.lower():
        response_json = {
            "text": "Ainda estou aprendendo as cordas, chefe. Quer que eu faça outra coisa?",
            "emotion": "thinking",
            "action": None
        }

    return response_json

def mock_voice_cloning_tts(text, voice_id="default"):
    """Simula a geração de TTS (ElevenLabs/Kokoro)."""
    # Na implementação real, retorna a URL ou o Base64 do .wav gerado
    time.sleep(0.5)
    return "audio_base64_simulado_aqui"

@app.route('/api/mascot/interact', methods=['POST'])
def mascot_interact():
    try:
        data = request.json
        
        # 1. Receber Input (Áudio ou Texto)
        audio_data = data.get('audio_base64', None)
        text_input = data.get('text', None)
        character_prompt = data.get('system_prompt', 'Você é o assistente padrão.')
        nitro_level = data.get('nitro_level', 'free') # 'free', 'nitro', 'nitro_master'
        
        # 2. STT (se for áudio)
        # O Whisper rodará no Lightning. A velocidade depende do Nitro Level.
        if audio_data:
            # Simulação de tempo de STT baseado no Nitro
            stt_delay = 2.0 if nitro_level == 'free' else 0.5
            time.sleep(stt_delay)
            text_input = mock_whisper_stt(audio_data)
        
        if not text_input:
            return jsonify({"error": "Nenhum áudio ou texto fornecido"}), 400

        # 3. Raciocínio LLM
        # O LLM é instantâneo e barato, independente do nível de Nitro
        llm_response = mock_llm_reasoning(text_input, character_prompt)
        
        # 4. Geração de Áudio (TTS / Voice Cloning)
        # O TTS (Ex: Piper ou RVC) também escala com a máquina.
        tts_delay = 3.0 if nitro_level == 'free' else (1.0 if nitro_level == 'nitro' else 0.2)
        time.sleep(tts_delay)
        
        tts_audio = mock_voice_cloning_tts(llm_response['text'], voice_id="custom_character")
        
        # 5. Montar pacote de resposta para a UI
        payload = {
            "status": "success",
            "transcription": text_input, # O que o usuário falou
            "response": llm_response,    # text, emotion, action
            "audio_response": tts_audio  # Base64 do áudio gerado
        }
        
        return jsonify(payload)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/mascot/forge', methods=['POST'])
def mascot_forge():
    """Endpoint para treinar uma nova voz e gerar sprites a partir da imagem base."""
    # Aqui o servidor Lightning repassaria a geração de Imagem para o Modal (Servidor Pesado)
    # E rodaria o fine-tuning do TTS localmente.
    return jsonify({
        "status": "success", 
        "message": "Entidade forjada com sucesso. Treinamento TTS concluído."
    })

if __name__ == '__main__':
    print("⚡ Lightning Server (Mascot Engine) rodando na porta 5005...")
    app.run(host='0.0.0.0', port=5005, debug=True)
