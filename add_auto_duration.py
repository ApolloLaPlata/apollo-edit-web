import re

with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add option 'auto' to the select
if 'value="auto"' not in html:
    html = html.replace('<option value="random">Aleatório (Entre Min e Max)</option>', 
                        '<option value="random">Aleatório (Entre Min e Max)</option>\n                      <option value="auto">Livre (Apenas Limite Mínimo)</option>')

# 2. Add the Auto Area div
if 'id="musicDurationAutoArea"' not in html:
    auto_area = '''
                  <div id="musicDurationAutoArea" style="display:none; gap:10px; margin-bottom:15px;">
                      <div style="flex:1;">
                          <div class="field-label">Min (s) - A IA decidirá o tempo baseado na letra</div>
                          <input type="number" id="musicDurationAutoMin" value="60" min="5" max="300" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                      </div>
                  </div>
'''
    html = html.replace('</div>\n                  \n                  <div class="progress-wrap"', '</div>\n                  ' + auto_area + '\n                  <div class="progress-wrap"')

# 3. Toggle logic in toggleMusicUI
if "document.getElementById('musicDurationAutoArea').style.display" not in html:
    html = html.replace("document.getElementById('musicDurationRandomArea').style.display = (durationMode === 'random') ? 'flex' : 'none';", 
                        "document.getElementById('musicDurationRandomArea').style.display = (durationMode === 'random') ? 'flex' : 'none';\n              document.getElementById('musicDurationAutoArea').style.display = (durationMode === 'auto') ? 'flex' : 'none';")

# 4. Calculation logic in generateMusicMaster
if "durationMode === 'auto'" not in html:
    random_logic = '''                  } else if (durationMode === 'random') {
                      const min = parseInt(document.getElementById('musicDurationMin').value) || 45;
                      const max = parseInt(document.getElementById('musicDurationMax').value) || 120;
                      finalDuration = Math.floor(Math.random() * (max - min + 1)) + min;
                  }'''
    auto_logic = random_logic + ''' else if (durationMode === 'auto') {
                      const min = parseInt(document.getElementById('musicDurationAutoMin').value) || 60;
                      let computed = min;
                      if (style === 'vocal' && lyrics[i] && lyrics[i].trim().length > 0) {
                          // Calcula aprox 1 segundo pra cada 4 letras/caracteres, ou no mínimo o valor definido.
                          computed = Math.floor(lyrics[i].length / 4);
                          if (computed < min) computed = min;
                          if (computed > 300) computed = 300;
                      } else {
                          // Sem vocais, apenas usa o mínimo (ou poderíamos sortear um maximo, mas vamos apenas deixar um tempo bom)
                          computed = min > 120 ? min : 120; 
                      }
                      finalDuration = computed;
                  }'''
    html = html.replace(random_logic, auto_logic)

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
