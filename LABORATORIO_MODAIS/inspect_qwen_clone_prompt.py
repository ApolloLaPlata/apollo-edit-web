from backend.cloud_tools.modal_app import app
import modal

qwen_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch==2.4.0", "qwen-tts", "transformers")
)

@app.local_entrypoint()
def run():
    print("Enviando script para a nuvem...")
    res = inspect_clone_prompt.remote()
    print("====== RESULTADO ======")
    print(res)

@app.function(image=qwen_image)
def inspect_clone_prompt():
    import inspect
    from qwen_tts import Qwen3TTSModel
    res = ""
    try:
        res += "create_voice_clone_prompt:\n"
        res += str(inspect.signature(Qwen3TTSModel.create_voice_clone_prompt))
        if Qwen3TTSModel.create_voice_clone_prompt.__doc__:
            res += "\n" + Qwen3TTSModel.create_voice_clone_prompt.__doc__
    except Exception as e:
        res += str(e)
    return res
