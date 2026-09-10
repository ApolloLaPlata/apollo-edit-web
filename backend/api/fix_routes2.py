import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/api/routes_studio.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''                    async with httpx.AsyncClient(timeout=10.0) as lc:
                        llm_res = await lc.post(
                            "https://lightning.ai/api/v1/chat/completions",
                            headers={"Authorization": f"Bearer {lit_key}", "Content-Type": "application/json"},
                            json={
                                "model": "nvidia-nemotron-3-ultra-550b-a55b",
                                "messages": [{"role": "user", "content": llm_prompt}]
                            }
                        )
                        if llm_res.status_code == 200:
                            content = llm_res.json()["choices"][0]["message"]["content"]
                            s_idx = content.find('[')
                            e_idx = content.rfind(']')
                            if s_idx != -1 and e_idx != -1:dynamic_steps = json.loads(content[s_idx:e_idx+1])
                                req_json["dynamic_steps"] = dynamic_steps
                                if len(dynamic_steps) > 0 and "negative_prompt" in dynamic_steps[0]:
                                    req_json["negative_prompt"] = dynamic_steps[0]["negative_prompt"]
                                    print(f"[PROXY DEBUG] [NEGATIVE PROMPT] Gerado: {dynamic_steps[0]['negative_prompt']}", flush=True)
                                
                                body = json.dumps(req_json).encode("utf-8")
                                print(f"[PROXY DEBUG] LLM Dynamic Steps Injetados com sucesso: {dynamic_steps}", flush=True)
                        else:
                            print(f"[PROXY DEBUG] Erro no LLM: {llm_res.text}", flush=True)'''

replacement = '''                    async with httpx.AsyncClient(timeout=15.0) as lc:
                        llm_success = False
                        for k in keys:
                            try:
                                print(f"[PROXY DEBUG] Testando chave LLM: {k[:10]}...", flush=True)
                                llm_res = await lc.post(
                                    "https://lightning.ai/api/v1/chat/completions",
                                    headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
                                    json={
                                        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
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
                                            print(f"[PROXY DEBUG] [NEGATIVE PROMPT] Gerado: {dynamic_steps[0]['negative_prompt']}", flush=True)
                                        
                                        body = json.dumps(req_json).encode("utf-8")
                                        print(f"[PROXY DEBUG] LLM Dynamic Steps Injetados com sucesso: {dynamic_steps}", flush=True)
                                    break
                                else:
                                    print(f"[PROXY DEBUG] Falha na chave {k[:10]}... Code: {llm_res.status_code}", flush=True)
                            except Exception as ex:
                                print(f"[PROXY DEBUG] Excecao na chave {k[:10]}... Erro: {ex}", flush=True)
                        if not llm_success:
                            print(f"[PROXY DEBUG] Erro critico: Todas as chaves LLM falharam.", flush=True)'''

content = content.replace(target, replacement)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("routes_studio.py LLM routing corrigido.")
