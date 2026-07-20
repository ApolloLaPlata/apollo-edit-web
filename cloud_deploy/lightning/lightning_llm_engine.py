import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from huggingface_hub import hf_hub_download

# =======================================================
# CONFIGURAÇÃO DO MODELO (Modifique aqui se desejar outro)
# =======================================================
REPO_ID = "bartowski/Meta-Llama-3-8B-Instruct-GGUF"
FILENAME = "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
MODEL_PATH = f"./models/{FILENAME}"

app = FastAPI(title="Apollo Lightning LLM Engine")

llm = None

def load_model():
    global llm
    if llm is not None:
        return
        
    print(f"[Apollo LLM] Verificando modelo {FILENAME}...")
    if not os.path.exists(MODEL_PATH):
        print("[Apollo LLM] Modelo não encontrado localmente. Baixando da HuggingFace (pode demorar)...")
        os.makedirs("./models", exist_ok=True)
        # Faz o download direto via HuggingFace
        downloaded_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            local_dir="./models",
            local_dir_use_symlinks=False
        )
        print(f"[Apollo LLM] Download concluído: {downloaded_path}")
        
    print("[Apollo LLM] Carregando modelo GGUF na VRAM (GPU)...")
    try:
        from llama_cpp import Llama
        # Configurações otimizadas para T4 (16GB VRAM) ou CPU se não houver placa
        llm = Llama(
            model_path=MODEL_PATH,
            n_gpu_layers=-1, # -1 = Todas as camadas na GPU
            n_ctx=8192,      # Janela de contexto
            verbose=False
        )
        print("[Apollo LLM] Modelo carregado com sucesso na GPU!")
    except Exception as e:
        print(f"[Apollo LLM] ERRO ao carregar o modelo: {e}")

@app.on_event("startup")
async def startup_event():
    # Tenta importar llama_cpp para validar a instalação
    try:
        import llama_cpp
    except ImportError:
        print("❌ ERRO CRÍTICO: llama-cpp-python não está instalado. Execute o comando de instalação do README.")
        return
        
    load_model()

@app.post("/api/v1/chat/completions")
async def chat_completions(req: Request):
    """
    Endpoint padrão compatível com a API da OpenAI.
    Isso permite que o Apollo Web se comunique com este servidor como se fosse a OpenAI ou OpenRouter.
    """
    if llm is None:
         return JSONResponse({"error": "Modelo offline ou carregando."}, status_code=503)
         
    try:
        body = await req.json()
        messages = body.get("messages", [])
        
        # Formata usando o chat format nativo do Llama-cpp (que suporta Llama-3, ChatML, etc.)
        response = llm.create_chat_completion(
            messages=messages,
            max_tokens=body.get("max_tokens", 2048),
            temperature=body.get("temperature", 0.7),
            stream=False
        )
        
        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    print("==================================================")
    print("🚀 APOLLO LIGHTNING LLM ENGINE (OpenAI Compatible)")
    print("==================================================")
    print("Iniciando servidor web na porta 8000...")
    uvicorn.run("lightning_llm_engine:app", host="0.0.0.0", port=8000, reload=False)
