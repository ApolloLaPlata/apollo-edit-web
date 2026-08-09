"""
Motor LLM via vLLM na Modal Cloud
==================================
Pipeline 'Cérebro' 100% Self-Hosted.
Gera texto em streaming (Server-Sent Events) para alimentar o TTS.
"""

import modal
from backend.cloud_tools.modal_app import app
from fastapi import Request
from fastapi.responses import StreamingResponse
import json

# Imagem com vLLM instalado
vllm_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "vllm==0.5.4", # Versão estável
        "fastapi[standard]"
    )
)

MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct" # Usando Qwen 2.5 7B por ser Open-Weights (Sem necessidade de Token da Meta) e extremamente rápido.

@app.cls(
    image=vllm_image, 
    gpu="L4", 
    timeout=600,
    scaledown_window=120, # O timeout de ociosidade (Hot-GPU) de 2 minutos
    min_containers=0
)
class VLLMEngine:
    @modal.enter()
    def load_model(self):
        print(f"[INIT] Inicializando vLLM com o modelo {MODEL_NAME} na VRAM...")
        from vllm import LLM
        # Usar enforce_eager=True pode reduzir consumo de VRAM e acelerar startup na L4
        self.llm = LLM(model=MODEL_NAME, tensor_parallel_size=1, max_model_len=4096, enforce_eager=True)
        print("[INIT] Modelo vLLM carregado na VRAM (Hot-GPU Ready)!")

    @modal.method(is_generator=True)
    def generate_stream_generator(self, prompt: str, system_prompt: str = ""):
        """
        Emite tokens um a um.
        """
        from vllm import SamplingParams
        
        sampling_params = SamplingParams(
            temperature=0.7, 
            top_p=0.9, 
            max_tokens=200,
        )
        
        # Formatador manual para evitar dores de cabeça de template
        prompt_formatted = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        print(f"[LLM] Recebeu Prompt. Gerando stream para: {prompt[:50]}...")
        
        # vLLM LLM.generate não é nativamente um gerador assíncrono fácil no Python loop se não usar AsyncLLMEngine.
        # Mas para o Modal VLLM, podemos iterar na saída se usarmos `use_tqdm=False`.
        # Como o F5-TTS exige chunks inteiros (frases), podemos gerar a frase inteira de uma vez, 
        # ou particionar a frase e enviar.
        
        # Simulando Streaming por Sentenças (Chunking lógico) para facilitar o TTS downstream.
        outputs = self.llm.generate([prompt_formatted], sampling_params, use_tqdm=False)
        full_text = outputs[0].outputs[0].text
        
        # Simulamos o envio por chunk (Na produção real usa-se AsyncLLMEngine)
        import re
        chunks = re.split(r'(?<=[.!?]) +', full_text)
        
        for chunk in chunks:
            if chunk.strip():
                yield chunk.strip()


@app.function(image=vllm_image)
@modal.fastapi_endpoint(method="POST", label="apollo-api-llm-stream")
async def api_llm_stream(request: Request):
    """
    Endpoint FastAPI que retorna Server-Sent Events (SSE).
    """
    data = await request.json()
    prompt = data.get("prompt", "")
    system_prompt = data.get("system_prompt", "Você é um assistente de IA conversando por voz. Responda de forma extremamente curta e concisa, como uma pessoa real conversando.")
    
    engine = VLLMEngine()
    
    async def event_generator():
        for chunk in engine.generate_stream_generator.remote_gen(prompt, system_prompt):
            # Formato SSE
            yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield "data: [DONE]\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")
