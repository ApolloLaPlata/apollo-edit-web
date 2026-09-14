import re

with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

start_idx = html.find('// Duration Calculation')
end_idx = html.find("logMusicMaster('Preparando fetch...');")

if start_idx != -1 and end_idx != -1:
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
                }
                '''
    html = html[:start_idx] + calc_new + '\n                ' + html[end_idx:]

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
