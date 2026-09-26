import os
import sys

try:
    if not os.path.exists('backend'):
        os.symlink('.', 'backend')
except Exception as e:
    print(f'Symlink trick failed: {e}')

import uvicorn
from main import app
import gradio as gr
import spaces
import torch

from gradio.routes import App

original_create_app = App.create_app

def custom_create_app(*args, **kwargs):
    gradio_app = original_create_app(*args, **kwargs)
    
    # Wrap Gradio's lifespan with Apollo's lifespan
    old_lifespan = gradio_app.router.lifespan_context
    import contextlib
    @contextlib.asynccontextmanager
    async def merged_lifespan(app_instance):
        async with app.router.lifespan_context(app):
            async with old_lifespan(app_instance) as state:
                yield state
                
    gradio_app.router.lifespan_context = merged_lifespan
    
    # Merge Apollo routes into Gradio
    for route in app.routes:
        if route not in gradio_app.routes:
            gradio_app.routes.insert(0, route)
            
    # Merge middlewares
    for mw in app.user_middleware:
        gradio_app.add_middleware(mw.cls, **mw.kwargs)
        
    # Merge exception handlers
    for exc_class, exc_handler in app.exception_handlers.items():
        gradio_app.add_exception_handler(exc_class, exc_handler)
        
    return gradio_app

App.create_app = custom_create_app

@spaces.GPU
def dummy_fn():
    # A dummy operation to prove the GPU is available and satisfy the proxy
    zero = torch.Tensor([0]).cuda()
    return f"Apollo Edit Backend is Running! (GPU verified: {zero.device})"

with gr.Blocks() as demo:
    gr.Markdown("# Apollo Edit Web - Cloud Backend")
    gr.Markdown("Esta é uma interface falsa (Trojan Horse) para manter o Hugging Face Space ativo. O verdadeiro backend está rodando no FastAPI oculto.")
    btn = gr.Button("Status")
    out = gr.Textbox()
    btn.click(fn=dummy_fn, inputs=[], outputs=[out])

# The Hugging Face supervisor will find `demo` and patch `demo.launch()`.
# When it runs, it will trigger our monkeypatch and inject the FastAPI routes and lifespan!
if __name__ == "__main__":
    demo.launch()
