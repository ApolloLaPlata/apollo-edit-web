import re
import json

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\api\routes_studio.py', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = re.compile(
    r'(if req_json\.get\("model"\) == "qwen-image" and images_b64 and len\(images_b64\) >= 1 and not req_json\.get\("dynamic_steps"\):)(.*?)(print\(f"\[PROXY DEBUG\] Erro ao injetar LLM: \{e\}", flush=True\))',
    re.DOTALL
)

new_block = r'''if req_json.get("model") == "qwen-image" and images_b64 and len(images_b64) >= 1 and not req_json.get("dynamic_steps"):
                num_imgs = len(images_b64)
                print(f"[PROXY DEBUG] Detectado Qwen com {num_imgs} imagens. Acionando LLM estrutural...", flush=True)
                
                admin_cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "admin_config.json"))
                lit_key = ""
                if os.path.exists(admin_cfg_path):
                    with open(admin_cfg_path, 'r', encoding='utf-8') as f:
                        c = json.load(f)
                        keys = c.get("api_config", {}).get("lightning_chat", {}).get("api_keys", [])
                        if keys:
                            lit_key = keys[0]
                
                if lit_key:
                    import modal
                    import asyncio
                    import hashlib
                    import json
                    
                    vision_descriptions = []
                    cache_file = os.path.join(os.path.dirname(__file__), "vision_cache.json")
                    
                    try:
                        cache_data = {}
                        if os.path.exists(cache_file):
                            with open(cache_file, "r", encoding="utf-8") as cf:
                                cache_data = json.load(cf)
                                
                        for idx, b64 in enumerate(images_b64):
                            img_hash = hashlib.sha256(b64[:10000].encode('utf-8')).hexdigest()
                            if img_hash in cache_data:
                                vision_descriptions.append(f"Image {idx}: {cache_data[img_hash]}")
                                print(f"[PROXY DEBUG] Imagem {idx} lida do cache.", flush=True)
                            else:
                                def call_vision(img_b64=b64):
                                    engine = modal.Cls.lookup("apollo-vision-engine", "FlorenceVisionEngine")
                                    return engine().analyze_image.remote(img_b64)
                                print(f"[PROXY DEBUG] Chamando Vision Engine para Imagem {idx}...", flush=True)
                                desc = await asyncio.to_thread(call_vision)
                                cache_data[img_hash] = desc
                                vision_descriptions.append(f"Image {idx}: {desc}")
                                
                        with open(cache_file, "w", encoding="utf-8") as cf:
                            json.dump(cache_data, cf)
                            
                    except Exception as ve:
                        print(f"[PROXY DEBUG] Erro Vision Engine: {ve}", flush=True)
                        vision_descriptions.append("Fallback: Error analyzing images.")
                        
                    combined_vision = "\n".join(vision_descriptions)
                    
                    llm_prompt = f"""You are an expert AI prompt engineer for Qwen 2.5 Image Edit.
The user provided {num_imgs} reference images. Raw prompt: "{req_json.get('prompt')}"

Our Vision AI analyzed the images:
{combined_vision}

Task: Rewrite the user's prompt into a highly detailed, descriptive prompt suitable for Qwen.
Rules:
1. Describe the final scene clearly in English. Do NOT copy exact poses if the user requested a NEW scene.
2. If {num_imgs} == 1: Add "SINGLE CHARACTER ONLY, NO CLONES, DO NOT REPEAT".
3. If {num_imgs} > 1: It is a Multi-Pass! Group the images into sequential logical steps (max 2 images per pass).
   - Pass 1 (Base scene): "prompt": "Create a scene... Add the character from Image 0..."
   - Pass 2+ (Editing): "prompt": "EDIT THIS SCENE. Keep existing elements exactly as they are. Add the character from Image 1..."
4. Generate an intelligent "negative_prompt" to exclude things the user DOES NOT want.
5. Output ONLY a valid JSON array of objects. Each object must have: "prompt" (string), "negative_prompt" (string, optional), "image_indices" (array of ints).
Make sure ALL {num_imgs} indices are used. No markdown blocks."""

                    async with httpx.AsyncClient(timeout=45.0) as lc:
                        llm_success = False
                        for k in keys:
                            try:
                                llm_res = await lc.post(
                                    "https://lightning.ai/api/v1/chat/completions",
                                    headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
                                    json={
                                        "model": "nvidia-nemotron-3-ultra-550b-a55b",
                                        "messages": [{"role": "user", "content": llm_prompt}]
                                    }
                                )
                                if llm_res.status_code == 200:
                                    llm_success = True
                                    res_content = llm_res.json()["choices"][0]["message"]["content"]
                                    s_idx = res_content.find('[')
                                    e_idx = res_content.rfind(']')
                                    if s_idx != -1 and e_idx != -1:
                                        dynamic_steps = json.loads(res_content[s_idx:e_idx+1])
                                        req_json["dynamic_steps"] = dynamic_steps
                                        if len(dynamic_steps) > 0 and "negative_prompt" in dynamic_steps[0]:
                                            req_json["negative_prompt"] = dynamic_steps[0]["negative_prompt"]
                                        
                                        body = json.dumps(req_json).encode("utf-8")
                                        print(f"[PROXY DEBUG] LLM Dynamic Steps: {dynamic_steps}", flush=True)
                                    break
                            except Exception as ex:
                                print(f"[PROXY DEBUG] Excecao na chave: {ex}", flush=True)
                        
        except Exception as e:
            print(f"[PROXY DEBUG] Erro ao injetar LLM: {e}", flush=True)'''

new_code = pattern.sub(new_block, code)
with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\api\routes_studio.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Patched successfully!")
