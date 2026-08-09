import requests
import time
import os
import websocket
import threading

URL_KOKORO = "https://apollolaplata--apollo-api-tts.modal.run/"
URL_STT = "https://apollolaplata--apollo-api-transcribe.modal.run/"
URL_MOSS = "https://apollolaplata--apollo-api-moss-tts.modal.run/"
URL_F5 = "https://apollolaplata--apollo-api-f5-tts.modal.run/"
URL_XTTS = "https://apollolaplata--apollo-api-xtts.modal.run/"
URL_MELO = "https://apollolaplata--apollo-api-melo.modal.run/"
URL_FISH = "https://apollolaplata--apollo-api-fish-tts.modal.run/"
WS_MOSHI = "wss://apollolaplata--apollo-api-moshi.modal.run/ws/live-chat"

def test_tts(url, nome_modelo, output_file, payload=None, texto=""):
    print(f"\nIniciando teste de velocidade e qualidade no {nome_modelo} (Modal Snapshot)...")
    if payload is None:
        payload = {"text": texto}
    else:
        # Pega só os primeiros 50 chars para o log se o texto estiver dentro do payload
        texto = payload.get("text", "")
    
    print(f"Enviando texto: '{texto[:50]}...'")
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=600)
        response.raise_for_status()
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        with open(output_file, "wb") as f:
            f.write(response.content)
            
        print("-" * 50)
        print(f"✅ SUCESSO! Áudio {nome_modelo} gerado em {elapsed:.2f} segundos.")
        print(f"🔊 Arquivo salvo em: {os.path.abspath(output_file)}")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com {nome_modelo}: {e}")
        return False

def run_tests():
    texto_padrao = "Este é um teste de voz em português brasileiro para analisarmos a fluidez, sotaque e velocidade de geração do modelo."
    timestamp = int(time.time())
    
    # Vamos usar o áudio existente do Kokoro como referência
    kokoro_out = "teste_kokoro_1786040948.wav"
    
    # 1. Kokoro TTS (pulado)
    # 2. Whisper Turbo STT (pulado)
    # 3. F5-TTS (pulado)
    payload_clone = {"text": texto_padrao}
    try:
        import base64
        if os.path.exists(kokoro_out):
            with open(kokoro_out, "rb") as f:
                payload_clone["ref_audio_base64"] = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Aviso: Não foi possível carregar áudio de ref para clonagem: {e}")
        
    # test_tts(URL_F5, "F5-TTS", f"teste_f5_{timestamp}.wav", payload=payload_clone)
    
    # 4. XTTSv2 (Zero-Shot Clone) (pulado)
    # test_tts(URL_XTTS, "XTTSv2", f"teste_xtts_{timestamp}.wav", payload=payload_clone)

    # 5. MeloTTS (MyShell) (pulado)
    # test_tts(URL_MELO, "MeloTTS", f"teste_melo_{timestamp}.wav", payload={"text": texto_padrao})

    # 6. Fish-Speech
    test_tts(URL_FISH, "Fish-Speech", f"teste_fish_{timestamp}.wav", payload=payload_clone)



def test_moshi_live():
    print("\nIniciando teste de Conversação ao Vivo Moshi (WebSocket)...")
    
    try:
        import websocket
    except ImportError:
        print("Instalando websocket-client para o teste...")
        os.system("pip install websocket-client")
        import websocket

    def on_message(ws, message):
        print(f"Moshi respondeu com {len(message)} bytes de áudio!")
        ws.close()

    def on_error(ws, error):
        print(f"❌ Erro no WebSocket Moshi: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("Conexão Moshi encerrada.")

    def on_open(ws):
        print("Conectado ao Moshi! Enviando dummy audio...")
        # Envia alguns bytes pra testar
        ws.send(b"\x00" * 1024, opcode=websocket.ABNF.OPCODE_BINARY)

    ws = websocket.WebSocketApp(WS_MOSHI,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
                              
    ws.run_forever()

if __name__ == "__main__":
    run_tests()
