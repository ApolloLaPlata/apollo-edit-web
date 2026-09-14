import re

with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add option 'auto' to the select
if 'value="auto_livre"' not in html:
    html = html.replace('<option value="random">Aleatório (Entre Min e Max)</option>', 
                        '<option value="random">Aleatório (Entre Min e Max)</option>\n                      <option value="auto_livre">Livre (Apenas Limite Mínimo)</option>')

# 2. Add the Auto Area div right before musicProgressContainer
auto_area = '''
                  <div id="musicDurationAutoArea" style="display:none; gap:10px; margin-bottom:15px;">
                      <div style="flex:1;">
                          <div class="field-label">Min (s) - A IA calculará o tempo ideal baseado na letra</div>
                          <input type="number" id="musicDurationAutoMin" value="60" min="5" max="300" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                      </div>
                  </div>
'''
if 'id="musicDurationAutoArea"' not in html:
    html = re.sub(r'(\s*<div class="log-box" id="musicMasterStatus")', r'\n' + auto_area + r'\1', html)

# 3. Toggle logic in toggleMusicUI
if "document.getElementById('musicDurationAutoArea').style.display" not in html:
    html = html.replace("document.getElementById('musicDurationRandomArea').style.display = (durationMode === 'random') ? 'flex' : 'none';", 
                        "document.getElementById('musicDurationRandomArea').style.display = (durationMode === 'random') ? 'flex' : 'none';\n            document.getElementById('musicDurationAutoArea').style.display = (durationMode === 'auto_livre') ? 'flex' : 'none';")

# 4. Calculation logic in generateMusicMaster
old_logic_stripped = "else if (durationMode === 'random')"
if old_logic_stripped in html and "durationMode === 'auto_livre'" not in html:
    start_idx = html.find("} else if (durationMode === 'random') {")
    if start_idx != -1:
        end_idx = html.find("}", start_idx + 10) + 1
        new_logic = '''} else if (durationMode === 'random') {
                    const min = parseInt(document.getElementById('musicDurationMin').value) || 45;
                    const max = parseInt(document.getElementById('musicDurationMax').value) || 120;
                    finalDuration = Math.floor(Math.random() * (max - min + 1)) + min;
                } else if (durationMode === 'auto_livre') {
                    const min = parseInt(document.getElementById('musicDurationAutoMin').value) || 60;
                    let computed = min;
                    if (style === 'vocal' && lyrics[i] && lyrics[i].trim().length > 0) {
                        computed = Math.floor(lyrics[i].length / 4);
                        if (computed < min) computed = min;
                        if (computed > 300) computed = 300;
                    } else {
                        computed = min > 120 ? min : 120;
                    }
                    finalDuration = computed;
                }'''
        html = html[:start_idx] + new_logic + html[end_idx:]

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
