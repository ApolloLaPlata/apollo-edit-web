import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update the image model dropdown
old_img_model = '''<select id="imgModel" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;" onchange="document.getElementById('imgBadgeModel').textContent = this.options[this.selectedIndex].text; updateGenButtonState();">
                    <option value="qwen-image">Qwen 2.5 Image Edit (T2I / I2I / Multi-Characters)</option>
                </select>'''
new_img_model = '''<select id="imgModel" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;" onchange="document.getElementById('imgBadgeModel').textContent = this.options[this.selectedIndex].text; updateGenButtonState(); document.getElementById('loraContainer').style.display = (this.value === 'flux2-universal') ? 'block' : 'none';">
                    <option value="qwen-image">Qwen 2.5 Image Edit (T2I / I2I / Multi-Characters)</option>
                    <option value="flux2-universal">FLUX.1-dev Universal (Img2Img / LoRA Civitai)</option>
                    <option value="flux-schnell">FLUX.1-schnell (Rápido T2I)</option>
                </select>'''
code = code.replace(old_img_model, new_img_model)

# 2. Add the LoRA fields after the Image Reference field
lora_ui = '''                <div id="loraContainer" style="display:none; margin-top:15px; border:1px dashed var(--border); padding:10px; border-radius:8px; background:rgba(255,100,255,0.05);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <h4 style="margin:0; color:#ff66ff;">🎭 Injeção de LoRA (Civitai)</h4>
                    </div>
                    <div class="field-label">URL Direta do Safetensors (Civitai)</div>
                    <input type="text" id="imgLoraUrl" placeholder="https://civitai.com/api/download/models/XXXX" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom:10px;">
                    <div class="field-label">Força do LoRA: <span id="imgLoraStrengthVal">1.0</span></div>
                    <input type="range" id="imgLoraStrength" min="0.1" max="2.0" step="0.1" value="1.0" style="width:100%;" oninput="document.getElementById('imgLoraStrengthVal').innerText = this.value">
                </div>
'''
if 'id="loraContainer"' not in code:
    # Find the end of the file-input-wrap div
    file_wrap_end = code.find('</div>', code.find('class="file-input-wrap"')) + 6
    code = code[:file_wrap_end] + '\n' + lora_ui + code[file_wrap_end:]

# 3. Update generateImage function to send lora_url and lora_strength
generate_img_js_old = '''const model = document.getElementById('imgModel') ? document.getElementById('imgModel').value : 'flux-schnell';
    const use_upscale = document.getElementById('toggleUpscale') ? document.getElementById('toggleUpscale').checked : true;
    const url    = "/api/studio/modal/generate_image";'''

generate_img_js_new = '''const model = document.getElementById('imgModel') ? document.getElementById('imgModel').value : 'flux-schnell';
    const use_upscale = document.getElementById('toggleUpscale') ? document.getElementById('toggleUpscale').checked : true;
    const lora_url = document.getElementById('imgLoraUrl') ? document.getElementById('imgLoraUrl').value.trim() : null;
    const lora_strength = document.getElementById('imgLoraStrength') ? parseFloat(document.getElementById('imgLoraStrength').value) : 1.0;
    const url    = "/api/studio/modal/generate_image";'''

if 'const lora_url =' not in code:
    code = code.replace(generate_img_js_old, generate_img_js_new)

body_js_old = '''const body = {
        prompt,
        model,
        aspect_ratio,
        use_upscale,
        reference_images_base64: imgReferences
    };'''

body_js_new = '''const body = {
        prompt,
        model,
        aspect_ratio,
        use_upscale,
        reference_images_base64: imgReferences,
        lora_url: lora_url,
        lora_strength: lora_strength
    };'''

if 'lora_url: lora_url' not in code:
    code = code.replace(body_js_old, body_js_new)

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(code)
print("LoRA UI injetada com sucesso!")
