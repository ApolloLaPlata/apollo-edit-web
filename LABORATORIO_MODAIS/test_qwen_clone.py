import base64
import time
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine

def test_clone():
    print("Enviando áudio de referência do Rafael para a Nuvem...")
    with open("E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_descargas_clean.wav", "rb") as f:
        ref_bytes = f.read()
    
    b64_ref = base64.b64encode(ref_bytes).decode('utf-8')
    
    engine = QwenTtsCloneEngine()
    
    # Texto a sintetizar
    texto = "Isso é um teste de clonagem zero-shot da minha voz usando o modelo Base do Qwen. Ele captura o meu timbre diretamente do áudio."
    
    res = engine.clone.remote(
        text=texto,
        ref_audio_b64=b64_ref,
        ref_text="Fiz o procedimento duas vezes pra ter certeza. Os pinos estão normais.",
        language="Portuguese"
    )
    
    if res["status"] == "success":
        out_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_qwen_clone.wav"
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(res["audio_base64"]))
        print(f"Sucesso! Salvo em {out_path} (Tempo na nuvem: {res.get('render_time_seconds')}s)")
    else:
        print("Erro:")
        print(res["message"])
        print(res.get("traceback", ""))

if __name__ == "__main__":
    from backend.cloud_tools.modal_app import app
    with app.run():
        test_clone()
