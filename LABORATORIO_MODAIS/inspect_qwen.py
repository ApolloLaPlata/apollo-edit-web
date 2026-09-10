import modal

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch==2.4.0", "qwen-tts", "transformers", "accelerate")
)

app = modal.App("inspect-qwen-tts")

@app.function(image=image, gpu="A10G")
def inspect():
    import inspect as py_inspect
    try:
        from qwen_tts import Qwen3TTSModel
        print("MÉTODOS Qwen3TTSModel:")
        print(dir(Qwen3TTSModel))
        
        print("\n\nINSPECIONAR generate:")
        if hasattr(Qwen3TTSModel, "generate"):
            print(py_inspect.signature(Qwen3TTSModel.generate))
            
        print("\n\nINSPECIONAR generate_custom_voice:")
        if hasattr(Qwen3TTSModel, "generate_custom_voice"):
            print(py_inspect.signature(Qwen3TTSModel.generate_custom_voice))
            
    except Exception as e:
        print(f"Erro: {e}")

@app.local_entrypoint()
def run():
    inspect.remote()
