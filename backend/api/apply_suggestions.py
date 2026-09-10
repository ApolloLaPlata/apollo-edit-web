# coding: utf-8
import os
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/api/routes_studio.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Semaphore at global level
if 'global_modal_semaphore' not in content:
    content = content.replace('from fastapi.responses import StreamingResponse\n', 'from fastapi.responses import StreamingResponse\nimport asyncio\nimport hashlib\nimport os\nimport json\n\nglobal_modal_semaphore = asyncio.Semaphore(2) # Limit to 2 concurrent Modal requests\n')

# 2. Add Vision Cache and Smart Cropping
stitch_block = '''
                if num_imgs > 1:
                    print(f"[PROXY DEBUG] [SMART CROP] Juntando {num_imgs} imagens em um unico grid com Smart Cropping (centering)...", flush=True)
                    try:
                        from PIL import Image, ImageOps
                        import io
                        import math
                        import base64
                        
                        pil_imgs = []
                        for b64 in images_b64:
                            b = b64.split(",")[1] if "," in b64 else b64
                            pil_imgs.append(Image.open(io.BytesIO(base64.b64decode(b))).convert("RGB"))
                        
                        cols = math.ceil(math.sqrt(num_imgs))
                        rows = math.ceil(num_imgs / cols)
                        
                        w, h = 512, 512
                        grid = Image.new("RGB", size=(cols * w, rows * h), color=(255, 255, 255))
                        for i, img in enumerate(pil_imgs):
                            img_smart = ImageOps.fit(img, (w, h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.2))
                            grid.paste(img_smart, box=(i % cols * w, i // cols * h))
                            
                        buf = io.BytesIO()
                        grid.save(buf, format="JPEG", quality=85)
                        stitched_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                        
                        images_b64 = [stitched_b64]
                        req_json["reference_images_base64"] = images_b64
                        num_imgs = 1
                        print("[PROXY DEBUG] [SMART CROP] Imagens coladas e otimizadas com sucesso.", flush=True)
                    except Exception as e:
                        print(f"[PROXY DEBUG] [SMART CROP] Erro: {e}", flush=True)
'''
content = re.sub(r'if num_imgs > 1:.*?except Exception as e:\s*print\(f"\[PROXY DEBUG\] Erro ao juntar imagens: \{e\}", flush=True\)', stitch_block.strip(), content, flags=re.DOTALL)

# 3. Add Vision Cache logic around Florence-2
vision_block = '''
                      vision_desc = ""
                      try:
                          import modal
                          import asyncio
                          import hashlib
                          import json
                          
                          cache_file = os.path.join(os.path.dirname(__file__), "vision_cache.json")
                          img_hash = hashlib.sha256(images_b64[0][:10000].encode('utf-8')).hexdigest()
                          
                          cache_data = {}
                          if os.path.exists(cache_file):
                              with open(cache_file, "r", encoding="utf-8") as cf:
                                  cache_data = json.load(cf)
                                  
                          if img_hash in cache_data:
                              vision_desc = cache_data[img_hash]
                              print(f"[PROXY DEBUG] [VISION CACHE] Memoria fotografica ativada! Imagem ja analisada antes. Pulando Florence-2.", flush=True)
                          else:
                              def call_vision():
                                  engine = modal.Cls.lookup("apollo-vision-engine", "FlorenceVisionEngine")
                                  return engine().analyze_image.remote(images_b64[0])
                              
                              print("[PROXY DEBUG] [VISION CACHE] Imagem nova detectada. Chamando Vision Engine (Florence-2)...", flush=True)
                              vision_desc = await asyncio.to_thread(call_vision)
                              print(f"[PROXY DEBUG] [VISION CACHE] Analise concluida e salva no cache local.", flush=True)
                              
                              cache_data[img_hash] = vision_desc
                              with open(cache_file, "w", encoding="utf-8") as cf:
                                  json.dump(cache_data, cf)
                                  
                      except Exception as ve:
                          print(f"[PROXY DEBUG] [VISION CACHE] Erro na Vision Engine: {ve}", flush=True)
'''
content = re.sub(r'vision_desc = ""\s*try:\s*import modal.*?print\(f"\[PROXY DEBUG\] Erro na Vision Engine: \{ve\}", flush=True\)', vision_block.strip(), content, flags=re.DOTALL)

# 4. Modify LLM Prompt for Negative Prompt
llm_prompt_block = '''
                      llm_prompt = f"""You are an expert AI prompt engineer for Qwen 2.5 Image Edit.
  The user provided 1 reference image of a character/subject and a raw prompt: \\"{req_json.get('prompt')}\\"
  
  Our Vision AI analyzed the reference image and described it as:
  "{vision_desc}"
  
  Your task is to rewrite the user's prompt into a highly detailed, descriptive prompt suitable for Qwen.
Rules for Qwen:
1. Describe the final scene clearly and comprehensively in English.
2. Incorporate the character/subject naturally into the environment described by the user.
3. CRITICAL: apply "Semantic Shielding" to force the AI to draw the character ONLY ONCE. Always include terms like "SINGLE CHARACTER ONLY, NO CLONES".
4. NEW RULE: Generate an intelligent "negative_prompt" to exclude things the user DOES NOT want, based on the requested style (e.g. if photorealistic, exclude 'anime, drawing').
5. Output ONLY a valid JSON array with exactly ONE object.
Format:
[
  {{
    "prompt": "The highly detailed rewritten prompt here...",
    "negative_prompt": "The negative prompt here...",
    "image_indices": [0]
  }}
]
Do not include markdown blocks."""
'''
content = re.sub(r'llm_prompt = f\"\"\"You are an expert AI prompt engineer for Qwen 2.5 Image Edit\..*?Do not include markdown blocks or any other text\.\"\"\"', llm_prompt_block.strip(), content, flags=re.DOTALL)

# Modify LLM JSON parsing to extract negative prompt
llm_parse_block = '''
                                dynamic_steps = json.loads(content[s_idx:e_idx+1])
                                req_json["dynamic_steps"] = dynamic_steps
                                if len(dynamic_steps) > 0 and "negative_prompt" in dynamic_steps[0]:
                                    req_json["negative_prompt"] = dynamic_steps[0]["negative_prompt"]
                                    print(f"[PROXY DEBUG] [NEGATIVE PROMPT] Gerado: {dynamic_steps[0]['negative_prompt']}", flush=True)
                                
                                body = json.dumps(req_json).encode("utf-8")
'''
content = content.replace('''
                                dynamic_steps = json.loads(content[s_idx:e_idx+1])
                                req_json["dynamic_steps"] = dynamic_steps
                                body = json.dumps(req_json).encode("utf-8")''', llm_parse_block.strip())

# 5. Wrap Modal request with Semaphore
sem_block = '''
    print(f"[PROXY DEBUG] [RATE LIMIT] Aguardando liberacao na fila da Modal (Max 2 simultaneos)...", flush=True)
    async with global_modal_semaphore:
        print(f"[PROXY DEBUG] [RATE LIMIT] Fila liberada! Enviando requisicao para a Modal.", flush=True)
        client = httpx.AsyncClient(timeout=300.0)
        try:
            req = client.build_request(
                method=request.method,
                url=modal_url,
                headers=headers,
                content=body
            )
            response = await client.send(req, stream=True)
            
            async def stream_gen():
                try:
                    async for chunk in response.aiter_raw():
                        yield chunk
                finally:
                    await response.aclose()
                    await client.aclose()
                    
            return StreamingResponse(
                stream_gen(),
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json")
            )
        except Exception as e:
            await client.aclose()
            raise HTTPException(status_code=500, detail=str(e))
'''
content = re.sub(r'client = httpx\.AsyncClient\(timeout=300\.0\).*?raise HTTPException\(status_code=500, detail=str\(e\)\)', sem_block.strip(), content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Sugestoes aplicadas!")
