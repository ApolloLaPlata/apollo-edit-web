import modal
import os
import io
import wave
import struct
import base64

print("Gerando áudio falso...")
dummy_wav_path = "dummy_ref_opus.wav"
with wave.open(dummy_wav_path, "w") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(24000)
    for i in range(24000):
        w.writeframes(struct.pack('h', 0))

with open(dummy_wav_path, "rb") as f:
    ref_bytes = f.read()

print("Buscando F5TTSEngine na nuvem Modal...")
try:
    cls = modal.Cls.from_name("apollo-render-router", "F5TTSEngine")
    f5 = cls()
    
    print("Invocando geração de voz...")
    texto_teste = "Olá! Este é o teste definitivo do motor de voz otimizado. Eu fui gerada nativamente em formato Opus de trinta e dois kilobits por segundo direto na placa de vídeo, sem usar arquivos locais. A infraestrutura de voz está completa."
    opus_bytes = f5.generate_voice.remote(texto_teste, ref_bytes)
    
    print(f"Gerado {len(opus_bytes)} bytes de áudio.")
    
    # Salva na pasta do Apollo Edit para ele testar no navegador ou cria o HTML local
    b64_audio = base64.b64encode(opus_bytes).decode('utf-8')
    
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Teste de Voz OPUS (Nuvem)</title>
        <style>
            body {{ background: #121212; color: #fff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .card {{ background: #1e1e1e; padding: 2rem; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; }}
            h2 {{ margin-top: 0; color: #00ffcc; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Teste do Motor F5-TTS (OPUS Nativo)</h2>
            <p><strong>Texto gerado:</strong><br/>"{texto_teste}"</p>
            <br/>
            <audio controls autoplay>
                <source src="data:audio/ogg;base64,{b64_audio}" type="audio/ogg">
                Seu navegador não suporta o formato de áudio.
            </audio>
            <p style="font-size: 12px; color: #888; margin-top: 20px;">Tamanho do arquivo: {len(opus_bytes)} bytes</p>
        </div>
    </body>
    </html>
    '''
    
    with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/teste_audio.html', 'w', encoding='utf-8') as f_html:
        f_html.write(html_content)
        
    print("Salvo em E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/teste_audio.html")

except Exception as e:
    print(f"Erro no teste: {e}")
finally:
    if os.path.exists(dummy_wav_path):
        os.remove(dummy_wav_path)

print("Finalizado.")
