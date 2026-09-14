import re

with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Insert the Auto Area div right before musicProgressContainer
auto_area = '''
                  <div id="musicDurationAutoArea" style="display:none; gap:10px; margin-bottom:15px;">
                      <div style="flex:1;">
                          <div class="field-label">Min (s) - A IA calculará o tempo ideal baseado na letra</div>
                          <input type="number" id="musicDurationAutoMin" value="60" min="5" max="300" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                      </div>
                  </div>
'''
html = re.sub(r'(\s*<div class="log-box" id="musicMasterStatus")', r'\n' + auto_area + r'\1', html)

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
