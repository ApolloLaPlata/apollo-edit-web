import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. UI: Add the Suno structural buttons above Single Lyrics
suno_toolbar = '''
                        <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                            <div class="field-label">Letra da Música (Opcional)</div>
                            <div style="display:flex; gap:5px; margin-bottom:5px;">
                                <button class="btn btn-ghost btn-sm" style="padding:2px 6px; font-size:0.7rem;" onclick="insertTag('musicSingleLyrics', '[Intro]')">[Intro]</button>
                                <button class="btn btn-ghost btn-sm" style="padding:2px 6px; font-size:0.7rem;" onclick="insertTag('musicSingleLyrics', '[Verse]')">[Verse]</button>
                                <button class="btn btn-ghost btn-sm" style="padding:2px 6px; font-size:0.7rem;" onclick="insertTag('musicSingleLyrics', '[Chorus]')">[Chorus]</button>
                                <button class="btn btn-ghost btn-sm" style="padding:2px 6px; font-size:0.7rem;" onclick="insertTag('musicSingleLyrics', '[Drop]')">[Drop]</button>
                                <button class="btn btn-ghost btn-sm" style="padding:2px 6px; font-size:0.7rem;" onclick="insertTag('musicSingleLyrics', '[Guitar Solo]')">[Solo]</button>
                            </div>
                        </div>
'''
html = html.replace('<div class="field-label">Letra da Música (Opcional)</div>', suno_toolbar)

# 2. UI: Add a "Magic Enhance" button for Styles (Single)
style_toolbar = '''
                    <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                        <div class="field-label">Prompt de Estilo Musical</div>
                        <button class="btn btn-ghost btn-sm" style="padding:2px 6px; font-size:0.7rem; color:var(--cyan);" onclick="magicStyle('musicSinglePrompt')">✨ Melhorar Prompt</button>
                    </div>
'''
html = html.replace('<div class="field-label">Prompt de Estilo Musical</div>', style_toolbar)

# 3. Add the JS functions for these
js_functions = '''
        function insertTag(targetId, tag) {
            const el = document.getElementById(targetId);
            const start = el.selectionStart;
            const end = el.selectionEnd;
            const text = el.value;
            el.value = text.substring(0, start) + tag + "\\n" + text.substring(end);
            el.focus();
            el.selectionEnd = start + tag.length + 1;
        }

        function magicStyle(targetId) {
            const el = document.getElementById(targetId);
            let val = el.value.trim();
            if (!val) val = "Trap";
            
            // Simple rule-based enhancement
            if (!val.toLowerCase().includes("quality")) val += ", masterpiece, ultra high quality, crisp audio";
            if (!val.toLowerCase().includes("bpm") && val.toLowerCase().includes("trap")) val += ", 140 bpm, heavy 808 bass, fast hi-hats";
            if (val.toLowerCase().includes("rock") && !val.toLowerCase().includes("guitar")) val += ", distorted electric guitars, heavy drums, stadium rock";
            if (val.toLowerCase().includes("lo-fi") || val.toLowerCase().includes("lofi")) val += ", vinyl crackle, cozy, relaxing, melodic piano";
            
            el.value = val;
            
            // Visual feedback
            const btn = event.target;
            const old = btn.innerText;
            btn.innerText = "✅ Aplicado!";
            setTimeout(() => { btn.innerText = old; }, 2000);
        }
'''
html = html.replace('// --- MASTER MUSIC GENERATION LOGIC ---', js_functions + '\n        // --- MASTER MUSIC GENERATION LOGIC ---')

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
