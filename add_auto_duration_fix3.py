import re

with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace duration mode logic
old_logic = '''                } else if (durationMode === 'random') {
                    const min = parseInt(document.getElementById('musicDurationMin').value) || 45;
                    const max = parseInt(document.getElementById('musicDurationMax').value) || 120;
                    finalDuration = Math.floor(Math.random() * (max - min + 1)) + min;
                }'''
old_logic_stripped = "else if (durationMode === 'random')"

if old_logic_stripped in html:
    # We find the start and end of this block manually
    start_idx = html.find("} else if (durationMode === 'random') {")
    end_idx = html.find("}", start_idx + 10) + 1
    
    new_logic = '''} else if (durationMode === 'random') {
                    const min = parseInt(document.getElementById('musicDurationMin').value) || 45;
                    const max = parseInt(document.getElementById('musicDurationMax').value) || 120;
                    finalDuration = Math.floor(Math.random() * (max - min + 1)) + min;
                } else if (durationMode === 'auto') {
                    const min = parseInt(document.getElementById('musicDurationAutoMin').value) || 60;
                    let computed = min;
                    if (style === 'vocal' && lyrics[i] && lyrics[i].trim().length > 0) {
                        // Calcula aprox 1 segundo pra cada 4 letras, no mínimo o valor de min
                        computed = Math.floor(lyrics[i].length / 4);
                        if (computed < min) computed = min;
                        if (computed > 300) computed = 300;
                    } else {
                        computed = min > 120 ? min : 120;
                    }
                    finalDuration = computed;
                }'''
    html = html[:start_idx] + new_logic + html[end_idx:]

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
