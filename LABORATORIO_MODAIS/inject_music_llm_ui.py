import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Auto-Tag button to the single lyrics toolbar
auto_tag_btn = '''<button class="btn btn-ghost btn-sm" style="padding:2px 6px; font-size:0.7rem; color:var(--cyan); margin-left:10px;" onclick="autoTagLyrics()" id="btnAutoTag">🪄 Auto-Tag (IA)</button>'''
if 'autoTagLyrics()' not in html:
    html = html.replace(
        '<button class="btn btn-ghost btn-sm" style="padding:2px 6px; font-size:0.7rem;" onclick="insertTag(\\\'musicSingleLyrics\\\', \\\'[Guitar Solo]\\\')">[Solo]</button>',
        '<button class="btn btn-ghost btn-sm" style="padding:2px 6px; font-size:0.7rem;" onclick="insertTag(\\\'musicSingleLyrics\\\', \\\'[Guitar Solo]\\\')">[Solo]</button>\n                                ' + auto_tag_btn
    )

# 2. Add "Gerador de Lote IA" inside musicBatchArea
ai_batch_ui = '''
                    <div style="background:#1a1a2a; padding:15px; border-radius:8px; border:1px solid var(--border); margin-bottom:15px;">
                        <div class="field-label" style="color:var(--cyan);">🧠 Gerador de Lote (Inteligência Artificial)</div>
                        <div style="font-size:0.8rem; color:var(--text-dim); margin-bottom:10px;">Deixe o LLM criar dezenas de estilos e letras para você.</div>
                        <div style="display:flex; gap:10px;">
                            <input type="text" id="aiBatchTheme" placeholder="Ex: 3 músicas de dark trap sobre hackers..." style="flex:1; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                            <input type="number" id="aiBatchCount" value="3" min="1" max="10" style="width:60px; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;" title="Quantidade">
                            <button class="btn btn-primary" id="btnAIGenerateBatch" onclick="generateBatchIdeas()" style="white-space:nowrap;">✨ Gerar Ideias</button>
                        </div>
                    </div>
'''
if 'aiBatchTheme' not in html:
    html = html.replace(
        '<div id="musicBatchArea" style="display:none;">',
        '<div id="musicBatchArea" style="display:none;">\n' + ai_batch_ui
    )


# 3. Add JS functions
new_js = '''
        async function autoTagLyrics() {
            const btn = document.getElementById('btnAutoTag');
            const el = document.getElementById('musicSingleLyrics');
            const raw = el.value.trim();
            
            if (!raw) return alert("Digite a letra primeiro para a IA estruturar!");
            
            btn.innerText = "⏳ Pensando...";
            btn.disabled = true;
            
            try {
                const response = await fetch("/api/music/auto_tag_lyrics", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ lyrics: raw })
                });
                const result = await response.json();
                
                if (result.success) {
                    el.value = result.structured_lyrics;
                    btn.innerText = "✅ Aplicado!";
                } else {
                    alert("Erro da IA: " + result.error);
                    btn.innerText = "❌ Falha";
                }
            } catch (e) {
                alert("Erro de rede.");
                btn.innerText = "❌ Erro";
            }
            
            setTimeout(() => {
                btn.innerText = "🪄 Auto-Tag (IA)";
                btn.disabled = false;
            }, 3000);
        }

        async function generateBatchIdeas() {
            const btn = document.getElementById('btnAIGenerateBatch');
            const theme = document.getElementById('aiBatchTheme').value.trim();
            const count = parseInt(document.getElementById('aiBatchCount').value) || 3;
            
            if (!theme) return alert("Digite o tema desejado!");
            
            btn.innerText = "⏳ Gerando...";
            btn.disabled = true;
            
            try {
                const response = await fetch("/api/music/generate_batch_ideas", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ theme, count })
                });
                const result = await response.json();
                
                if (result.success && result.tracks.length > 0) {
                    let promptStr = "";
                    let lyricStr = "";
                    
                    result.tracks.forEach((track, i) => {
                        promptStr += track.style + "\\n";
                        lyricStr += track.lyrics + "\\n";
                        if (i < result.tracks.length - 1) lyricStr += "\\n===\\n";
                    });
                    
                    document.getElementById('musicBatchPrompts').value = promptStr.trim();
                    document.getElementById('musicBatchLyrics').value = lyricStr.trim();
                    
                    // Force change to Vocal mode since AI generated lyrics
                    document.getElementById('musicStyle').value = 'vocal';
                    toggleMusicUI();
                    
                    btn.innerText = "✅ Ideias Prontas!";
                } else {
                    alert("Erro da IA: " + (result.error || "Formato inválido retornado."));
                    btn.innerText = "❌ Falha";
                }
            } catch (e) {
                alert("Erro de rede.");
                btn.innerText = "❌ Erro";
            }
            
            setTimeout(() => {
                btn.innerText = "✨ Gerar Ideias";
                btn.disabled = false;
            }, 3000);
        }
'''

if 'async function autoTagLyrics()' not in html:
    html = html.replace('function insertTag(targetId, tag)', new_js + '\n        function insertTag(targetId, tag)')

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Frontend LLM tools injected.")
