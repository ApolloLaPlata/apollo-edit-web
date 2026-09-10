import base64
import os
import time
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine

def test_langs():
    with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_tts/rafael_descargas_clean.wav", "rb") as f:
        ref_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    engine = QwenTtsCloneEngine()
    
    langs = ["pt", "pt-BR", "Portuguese", "portuguese"]
    texto = "Este é um teste para descobrir qual parâmetro ativa o português brasileiro."
    
    out_dir = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_tts"
    
    for lang in langs:
        print(f"Testando: {lang}...")
        res = engine.clone.remote(
            text=texto,
            ref_audio_b64=ref_b64,
            ref_text="Fiz o procedimento duas vezes pra ter certeza. Os pinos estão normais.",
            language=lang
        )
        if res["status"] == "success":
            out_path = os.path.join(out_dir, f"rafael_qwen_lang_{lang.replace('-','_')}.wav")
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(res["audio_base64"]))
            print(f"Salvo: {out_path}")
        else:
            print("Erro:", res["message"])

if __name__ == "__main__":
    from backend.cloud_tools.modal_app import app
    with app.run():
        test_langs()
