import json

with open('servidor_web.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We know generate_broll starts around line 779 and ends at 'return\n            \n        # Serve static files from web_ui\n'
# Let's find the exact string

start_marker = "elif parsed_path.path == '/api/generate_broll':"
end_marker = "# Serve static files from web_ui"

idx_start = content.find(start_marker)
idx_end = content.find(end_marker, idx_start)

if idx_start != -1 and idx_end != -1:
    broll_block = content[idx_start:idx_end]
    content = content[:idx_start] + content[idx_end:]

    # Now let's inject a new generate_broll into do_POST
    post_end_marker = "self.send_response(404)\n            self.end_headers()\n\n    def do_GET(self):"
    
    new_broll = '''elif parsed_path.path == '/api/generate_broll':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                prompt = data.get('prompt', '')
                
                if not prompt:
                    raise ValueError("Prompt não fornecido para gerar imagem.")
                    
                print(f"🎨 Gerando imagem B-Roll para: '{prompt}'...")
                
                import time
                import requests
                import base64
                from config_manager import ConfigManager
                
                cfg = ConfigManager()
                
                midias_dir = os.path.join(BASE_DIR, "Midias", "Geradas_IA")
                os.makedirs(midias_dir, exist_ok=True)
                
                filename = f"broll_ai_{int(time.time())}.jpg"
                filepath = os.path.join(midias_dir, filename)
                
                def get_all_keys(provider):
                    keys_raw = cfg.get_api_config(provider, "api_keys")
                    parsed = []
                    if isinstance(keys_raw, list):
                        for k in keys_raw:
                            if isinstance(k, dict) and k.get('key'):
                                parsed.append(k['key'])
                            elif isinstance(k, str):
                                parsed.append(k)
                    if not parsed:
                        legacy = cfg.get_api_config(provider, "api_key")
                        if legacy:
                            parsed.append(legacy)
                    return [k for k in parsed if k and str(k).strip() and str(k).strip() != "YOUR_API_KEY"]

                gemini_keys = get_all_keys("gemini")
                
                safe_prompt = f"cinematic b-roll footage of {prompt}, masterpiece, 8k, highly detailed"
                success = False
                source_used = ""
                
                # PLANO A: GEMINI (Imagen 3)
                print(f"🔄 Tentando gerar com {len(gemini_keys)} chaves Gemini...")
                for idx, key in enumerate(gemini_keys):
                    try:
                        url = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict"
                        headers = {"Content-Type": "application/json", "X-goog-api-key": key}
                        payload = {
                            "instances": [{"prompt": safe_prompt}],
                            "parameters": {"sampleCount": 1, "aspectRatio": "16:9"}
                        }
                        resp = requests.post(url, headers=headers, json=payload, timeout=60)
                        if resp.status_code == 200:
                            result = resp.json()
                            if 'predictions' in result and len(result['predictions']) > 0:
                                img_bytes = base64.b64decode(result['predictions'][0]['bytesBase64Encoded'])
                                with open(filepath, 'wb') as f:
                                    f.write(img_bytes)
                                print(f"✅ B-Roll gerado via Gemini (Chave {idx+1}) e salvo em: {filepath}")
                                success = True
                                source_used = f"Gemini (Chave {idx+1})"
                                break
                        else:
                            print(f"⚠️  Falha no Gemini (Chave {idx+1}): {resp.status_code}")
                    except Exception as e:
                        print(f"⚠️  Erro na chamada Gemini (Chave {idx+1}): {e}")
                
                if success:
                    web_path = filepath.replace('\\\\', '/')
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "success",
                        "path": web_path,
                        "message": f"Imagem gerada com sucesso via {source_used}!"
                    }).encode('utf-8'))
                else:
                    raise ValueError(f"Falha na geração via Gemini. (Verificou se há chaves configuradas?)")
                    
            except Exception as e:
                import traceback
                print(f"🎨 ERRO na geração de imagem: {traceback.format_exc()}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

    def do_GET(self):'''
    
    content = content.replace(post_end_marker, new_broll)

    with open('servidor_web.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Sucesso!")
else:
    print("Nao encontrou")
