import time
import os
import asyncio
from typing import Dict, List, Optional, Callable
import sys
import base64

# Forçar log streaming
sys.stdout.reconfigure(line_buffering=True)

class DummyServer:
    """
    Overrides the ComfyUI server to be able to run in the main thread.
    """
    def __new__(cls):
        import server
        import execution

        try:
            event_loop = asyncio.get_event_loop()
        except RuntimeError:
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)

        class Server(server.PromptServer):
            def __init__(self, loop, on_send_sync=None):
                super().__init__(loop)
                server.PromptServer.instance = self
                q = execution.PromptQueue(server.PromptServer.instance)
                self.client_id = "dummy"
                self.prompt_queue = q
                self.on_send_sync = on_send_sync

            def send_sync(self, event, data, sid=None):
                if self.on_send_sync:
                    self.on_send_sync(event, data, sid)

        return Server(event_loop, on_send_sync=None)


class CustomPromptExecutor:
    """Defer imports until ComfyUI is on system path"""
    def __new__(cls, lru_size=None):
        import execution

        class Executor(execution.PromptExecutor):
            def __init__(self, lru_size=None):
                server = DummyServer()
                super().__init__(server, lru_size)
                self.on_start: Optional[Callable[[dict], None]] = None
                self.on_error: Optional[Callable[[dict], None]] = None
                self.on_progress: Optional[Callable[[dict], None]] = None
                self.on_cached_nodes: Optional[Callable[[dict], None]] = None
                self.on_interrupt: Optional[Callable[[dict], None]] = None
                self.on_done: Optional[Callable[[dict], None]] = None
                self.server = server

            def add_message(self, event: str, data: dict, broadcast: bool):
                super().add_message(event, data, broadcast)
                try:
                    if event == "execution_start" and self.on_start:
                        self.on_start(data)
                    elif event == "execution_cached" and self.on_cached_nodes:
                        self.on_cached_nodes(data)
                    elif event == "execution_error" and self.on_error:
                        self.on_error(data)
                    elif event == "execution_interrupted" and self.on_interrupt:
                        self.on_interrupt(data)
                    elif event == "execution_success" and self.on_done:
                        self.on_done(data)
                except Exception as e:
                    print(f"Error in callback: {str(e)}")

        return Executor(lru_size)

class ExperimentalComfyServer:
    """Experimental ComfyUI server that runs workflows in the main thread."""
    MSG_TYPES_TO_PROCESS = [
        "executing",
        "execution_cached",
        "execution_complete",
        "execution_start",
        "progress",
        "status",
        "completed",
    ]

    from contextlib import contextmanager

    @contextmanager
    def force_cpu_during_snapshot(self):
        import torch
        """Monkeypatch Torch CUDA checks during model loading/snapshotting"""
        original_is_available = torch.cuda.is_available
        original_current_device = torch.cuda.current_device

        torch.cuda.is_available = lambda: False
        torch.cuda.current_device = lambda: torch.device("cpu")
        try:
            yield
        finally:
            torch.cuda.is_available = original_is_available
            torch.cuda.current_device = original_current_device

    def __init__(self, preload_models: List[str] = None):
        if preload_models is None:
            preload_models = []
        with self.force_cpu_during_snapshot():
            print("[ExperimentalComfyServer] Initializing experimental server")
            self.initialized = False
            self.model_cache = {}
            self.executor = None
            self._override_comfy(preload_models)

            # Registrar os paths no ComfyUI NATIVAMENTE
            import folder_paths
            folder_paths.add_model_folder_path("checkpoints", "/comfyui_models/checkpoints")
            folder_paths.add_model_folder_path("loras", "/comfyui_models/loras")
            folder_paths.add_model_folder_path("vae", "/comfyui_models/vae")
            folder_paths.add_model_folder_path("clip", "/comfyui_models/clip")
            folder_paths.add_model_folder_path("unet", "/comfyui_models/unet")
            folder_paths.add_model_folder_path("controlnet", "/comfyui_models/controlnet")

    def _preload_models_to_cpu(self, model_paths: List[str] = []):
        import safetensors.torch
        print("[ExperimentalComfyServer] Preloading models to CPU memory...")
        for model_path in model_paths:
            full_path = os.path.join("/comfyui_models", model_path)
            print(f"[ExperimentalComfyServer] Loading {model_path} into CPU memory...")
            start_time = time.time()
            try:
                if full_path.endswith(".safetensors"):
                    state_dict = safetensors.torch.load_file(full_path, device="cpu")
                    load_time = time.time() - start_time
                    file_size = os.path.getsize(full_path) / (1024 * 1024 * 1024)
                    speed = file_size / load_time if load_time > 0 else 0
                    print(f"[ExperimentalComfyServer] Model loaded in {load_time:.2f}s ({speed:.2f} GB/s)")
                    
                    filename = model_path.split("/")[-1]
                    self.model_cache[filename] = state_dict
            except Exception as e:
                print(f"[ExperimentalComfyServer] Failed to load {model_path}: {e}")

    def model_load_override_with_gpu(self):
        if not self.initialized:
            import comfy.utils
            self._patch_model_loading(comfy.utils)
            self.initialized = True

    def _patch_model_loading(self, comfy_utils):
        original_load = comfy_utils.load_torch_file

        def cached_load(path, *args, **kwargs):
            filename = os.path.basename(path)
            for model_key, state_dict in self.model_cache.items():
                if filename in str(model_key):
                    print(f"[ExperimentalComfyServer] Using cached model {model_key}. Args: {args}, Kwargs: {kwargs}")
                    
                    # Se return_metadata=True estiver em kwargs, ou se houver um argumento no qual deduzimos que seja o return_metadata
                    if kwargs.get("return_metadata", False) or (len(args) >= 3 and args[2] == True):
                        return (state_dict, {"safetensors": True})
                    
                    # Vamos forcar retornar tuple se der erro de unpack (hackish mas funciona)
                    # Mas para ser seguro, se 'metadata' for esperado, retornamos tuple
                    if "return_metadata" in kwargs and kwargs["return_metadata"]:
                        return (state_dict, {"safetensors": True})
                        
                    # Se não temos como saber, e nodes.py exige, talvez possamos apenas retornar a tupla SEMPRE se o caller pedir? 
                    # Na dúvida, checamos o call stack para ver se ele espera uma tupla (apenas como ultima alternativa)
                    
                    return state_dict
            return original_load(path, *args, **kwargs)

        comfy_utils.load_torch_file = cached_load

    async def execute(self, prompt: dict, process_id: str, callbacks=None):
        import execution
        import torch

        self.model_load_override_with_gpu()

        result_future = asyncio.Future()
        result_data = {"process_id": process_id, "images_base64": []}

        try:
            def on_error(error_data: Dict):
                print(f"[ExperimentalComfyServer] Error: {error_data}")
                result_future.set_exception(Exception(str(error_data)))

            def on_done(msg: Dict):
                print(f"[ExperimentalComfyServer] Done: {msg}")
                result_data["outputs"] = msg
                result_future.set_result(result_data)

            self.job_outputs = {}

            def on_ws_message(event_type: str, msg: dict, sid=None):
                if event_type == "executed":
                    node_id = msg.get("node")
                    if node_id:
                        self.job_outputs[node_id] = msg.get("output", {})
                
                if event_type in self.MSG_TYPES_TO_PROCESS:
                    if callbacks and hasattr(callbacks, "on_ws_message"):
                        callbacks.on_ws_message(event_type, msg)

            self.executor.on_error = on_error
            self.executor.on_done = on_done
            self.executor.server.on_send_sync = on_ws_message

            start_time = time.time()
            import nodes
            outputs_to_execute = []
            for k, v in prompt.items():
                class_def = nodes.NODE_CLASS_MAPPINGS.get(v.get('class_type'))
                if class_def and getattr(class_def, 'OUTPUT_NODE', False):
                    outputs_to_execute.append(k)
            if not outputs_to_execute:
                outputs_to_execute = list(prompt.keys())
            
            print(f"[ExperimentalComfyServer] Bypass Validation. Found {len(outputs_to_execute)} output nodes.")

            self.executor.cache_args = {"ram": 1000, "vram": 1000, "ram_inactive": 1000, "vram_inactive": 1000} # Dummy
            # DUMMY COMMENT TO FORCE UPLOAD

            with torch.inference_mode(), torch.autocast(device_type="cuda", enabled=False):
                await self.executor.execute_async(
                    prompt,
                    process_id,
                    {"client_id": process_id},
                    outputs_to_execute,
                )

            if getattr(self.executor, "success", True):
                for output_id, output_data in self.job_outputs.items():
                    if "images" in output_data:
                        # Parse output
                        import folder_paths
                        output_dir = folder_paths.get_output_directory()
                        for img_info in output_data["images"]:
                            filename = img_info["filename"]
                            subfolder = img_info.get("subfolder", "")
                            img_path = os.path.join(output_dir, subfolder, filename)
                            if os.path.exists(img_path):
                                with open(img_path, "rb") as f:
                                    img_b64 = base64.b64encode(f.read()).decode('utf-8')
                                    result_data["images_base64"].append(img_b64)
                                    print(f"[ExperimentalComfyServer] Imagem carregada do FS local: {img_path}")
                                    
                result_data["outputs"] = self.job_outputs
                if not result_future.done():
                    result_future.set_result(result_data)
            else:
                if not result_future.done():
                    error_msg = getattr(self.executor, "error", "Unknown execution error")
                    result_future.set_exception(Exception(str(error_msg)))

            return await result_future

        except Exception as e:
            if not result_future.done():
                result_future.set_exception(e)
            raise

    def _override_comfy(self, preload_models: List[str] = []):
        if "/comfyui" not in sys.path:
            sys.path.append("/comfyui")
        
        # O ComfyUI precisa que o CWD seja a raiz dele para achar os custom_nodes corretamente em algumas situações
        import os
        original_cwd = os.getcwd()
        os.chdir("/comfyui")
        
        import comfy.cli_args as cli_args
        if not hasattr(cli_args, "args") or cli_args.args is None:
            cli_args.args = cli_args.parser.parse_args([])

        import folder_paths
        original_get_filename_list = folder_paths.get_filename_list
        def patched_get_filename_list(folder_name):
            results = original_get_filename_list(folder_name)
            if results is None:
                results = []
            else:
                results = list(results)
            for k in preload_models:
                parts = k.split("/")
                if len(parts) >= 2:
                    cached_folder = parts[0]
                    cached_filename = parts[-1]
                    if cached_folder == folder_name and cached_filename not in results:
                        results.append(cached_filename)
            return results
        folder_paths.get_filename_list = patched_get_filename_list

        import execution
        def patched_validate_prompt(prompt):
            import nodes
            good_outputs = []
            for k, v in prompt.items():
                class_def = nodes.NODE_CLASS_MAPPINGS.get(v.get('class_type'))
                if class_def and getattr(class_def, 'OUTPUT_NODE', False):
                    good_outputs.append(k)
            if not good_outputs:
                good_outputs = list(prompt.keys())
            return (True, None, good_outputs, {})
        execution.validate_prompt = patched_validate_prompt

        import nodes
        import asyncio
        self.executor = CustomPromptExecutor()
        start_time = time.time() * 1000
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(nodes.init_extra_nodes())
        init_time = time.time() * 1000 - start_time
        print(f"[ExperimentalComfyServer] Node initialization took {init_time:.2f} ms")
        self._preload_models_to_cpu(preload_models)
