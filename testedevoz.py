# testedevoz.py

import requests
import base64

def gerar_tts(
    texto: str,
    voz: str = "Zephyr",
    modelo: str = "gemini-3.1-flash-tts-preview",
    api_key: str = "AIzaSyDrc1Q3-mrVFRFLn2XIDpQh9EcUckqdZXw",
    output: str = "output.wav"
):
    """
    Gera um arquivo WAV a partir de texto usando a API Gemini TTS.
    Parâmetros:
      texto   - string com o texto a ser sintetizado
      voz     - nome da voice prebuilt (ex.: "Zephyr", "Puck", "Charon" etc.)
      modelo  - modelo TTS (pré-lançamento)
      api_key - sua chave de API embutida
      output  - nome do arquivo de saída (.wav)
    """

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{modelo}:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }

    payload = {
        "contents": [
            { "parts": [{ "text": texto }] }
        ],
        "responseModalities": ["AUDIO"],
        "speechConfig": {
            "voiceConfig": {
                "prebuiltVoiceConfig": { "voiceName": voz }
            }
        }
    }

    resp = requests.post(url, headers=headers, json=payload)

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Erro na chamada TTS:", resp.status_code)
        print(resp.text)
        return

    data = resp.json()

    # Navega até o base64 do áudio
    b64_audio = (
        data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("inline_data", {})
            .get("data")
    )

    if not b64_audio:
        print("Resposta sem áudio sintetizado:", data)
        return

    audio_bytes = base64.b64decode(b64_audio)

    # Salva o arquivo WAV
    with open(output, "wb") as f:
        f.write(audio_bytes)

    print(f"Áudio gerado em {output}")


if __name__ == "__main__":
    # Se você quiser passar o texto pela linha de comando:
    import sys
    texto = sys.argv[1] if len(sys.argv) > 1 else "Olá, mundo! Testando Gemini TTS via REST."
    gerar_tts(texto)