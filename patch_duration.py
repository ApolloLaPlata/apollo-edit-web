import re

with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Hide the options auto_livre and auto from the select if they exist (they shouldn't be selectable manually anymore)
html = re.sub(r'<option value="auto_livre">[^<]*</option>', '', html)
html = re.sub(r'<option value="auto">[^<]*</option>', '', html)

# 2. Modify toggleMusicUI to handle the style visibility
toggle_music_ui_old = '''// Duration Areas
            document.getElementById('musicDurationFixedArea').style.display = (durationMode === 'fixed') ? 'block' : 'none';
            document.getElementById('musicDurationRandomArea').style.display = (durationMode === 'random') ? 'flex' : 'none';
              document.getElementById('musicDurationAutoArea').style.display = (durationMode === 'auto') ? 'flex' : 'none';'''
              
# also there might be auto_livre
toggle_music_ui_old_2 = '''// Duration Areas
            document.getElementById('musicDurationFixedArea').style.display = (durationMode === 'fixed') ? 'block' : 'none';
            document.getElementById('musicDurationRandomArea').style.display = (durationMode === 'random') ? 'flex' : 'none';
            document.getElementById('musicDurationAutoArea').style.display = (durationMode === 'auto_livre') ? 'flex' : 'none';'''

toggle_music_ui_new = '''// Duration Areas
            const durationSelect = document.getElementById('musicDurationMode');
            if (style === 'vocal') {
                durationSelect.style.display = 'none';
                document.getElementById('musicDurationFixedArea').style.display = 'none';
                document.getElementById('musicDurationRandomArea').style.display = 'none';
                document.getElementById('musicDurationAutoArea').style.display = 'block';
            } else {
                durationSelect.style.display = 'block';
                document.getElementById('musicDurationAutoArea').style.display = 'none';
                document.getElementById('musicDurationFixedArea').style.display = (durationMode === 'fixed') ? 'block' : 'none';
                document.getElementById('musicDurationRandomArea').style.display = (durationMode === 'random') ? 'flex' : 'none';
            }'''

html = html.replace(toggle_music_ui_old, toggle_music_ui_new)
html = html.replace(toggle_music_ui_old_2, toggle_music_ui_new)

# 3. Replace the AutoArea content to be just a message without inputs (since limits are removed)
auto_area_regex = r'<div id="musicDurationAutoArea" style="display:none; gap:10px; margin-bottom:15px;">.*?</div>\s*</div>'
new_auto_area = '''<div id="musicDurationAutoArea" style="display:none; margin-bottom:15px;">
                      <div style="background: rgba(0, 210, 255, 0.1); border: 1px solid #00d2ff; padding: 10px; border-radius: 8px; font-size: 13px; color: #00d2ff; text-align: center;">
                          ⏳ <b>Duração Automática:</b> Como o modo selecionado é Vocal, o tamanho da música será rigorosamente determinado pelo comprimento exato da sua letra!
                      </div>
                  </div>'''

html = re.sub(auto_area_regex, new_auto_area, html, flags=re.DOTALL)

# 4. In generateMusicMaster, change the duration logic to FORCE lyrics-based duration if vocal
calc_old = '''// Duration Calculation
                let finalDuration = 180; // Suno/Auto Default
                if (durationMode === 'fixed') {
                    finalDuration = parseInt(document.getElementById('musicDurationFixed').value) || 60;
                } else if (durationMode === 'random') {
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
                
calc_new = '''// Duration Calculation
                let finalDuration = 60;
                if (style === 'vocal') {
                    // Force duration based on lyrics length WITHOUT limits!
                    if (lyrics[i] && lyrics[i].trim().length > 0) {
                        finalDuration = Math.floor(lyrics[i].length / 4);
                        // Prevent absolute zero just in case
                        if (finalDuration < 5) finalDuration = 5;
                    } else {
                        finalDuration = 60; // fallback if empty
                    }
                } else {
                    if (durationMode === 'fixed') {
                        finalDuration = parseInt(document.getElementById('musicDurationFixed').value) || 60;
                    } else if (durationMode === 'random') {
                        const min = parseInt(document.getElementById('musicDurationMin').value) || 45;
                        const max = parseInt(document.getElementById('musicDurationMax').value) || 120;
                        finalDuration = Math.floor(Math.random() * (max - min + 1)) + min;
                    }
                }'''

# Replace logic (using regex or simple find/replace)
# Wait, let's use a smart replace
start_idx = html.find('// Duration Calculation')
if start_idx != -1:
    end_idx = html.find('const isMiniMax = engine.includes', start_idx)
    if end_idx == -1:
        end_idx = html.find('const params = {', start_idx)
    
    if end_idx != -1:
        # replace the block
        html = html[:start_idx] + calc_new + '\n                ' + html[end_idx:]

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Patch applied to web_ui/modal_ai_studio.html")
