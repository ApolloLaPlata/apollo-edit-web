import re

with open('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\public\\pocket_director.html', 'r', encoding='utf-8') as f:
    html = f.read()

replacement = '''    <div class="sidebar-footer">
      <div style="font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; color: #fff; text-transform: uppercase; letter-spacing: 1px; display: flex; justify-content: space-between; align-items: center;">
        <span>?? ENGINE LOGS</span>
        <button id="btnCopyLogs" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; cursor: pointer; transition: 0.2s;">Copiar</button>
      </div>
      <div id="leftLogsBox" style="height: 120px; background: #000; border-radius: 4px; border: 1px solid #333; padding: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #a7f3d0; overflow-y: auto; word-break: break-all; margin-bottom: 10px;">
        > Monitoramento de Processamento Ativo...
      </div>
      <script>
        document.getElementById('btnCopyLogs').addEventListener('click', function() {
          const logs = document.getElementById('leftLogsBox').innerText;
          navigator.clipboard.writeText(logs).then(() => {
            this.innerText = 'Copiado!';
            setTimeout(() => { this.innerText = 'Copiar'; }, 2000);
          }).catch(err => {
            console.error('Falha ao copiar', err);
          });
        });
      </script>
      <button class="deck-btn primary" id="btnNewChat" style="width: 100%; font-size: 0.9rem;">? Novo Chat</button>
    </div>
  </aside>'''

# Regex to match the sidebar-footer and the hiveLogsSidebar
pattern = re.compile(r'    <div class="sidebar-footer">.*?</aside>\s*<!-- ETAPA 194: Sidebar Logs da Colmeia -->\s*<aside class="chat-sidebar" id="hiveLogsSidebar">.*?</aside>', re.DOTALL)

new_html = pattern.sub(replacement, html)

# Inject the global JS function
js_func = '''
  <!-- Engine Logs globais -->
  <script>
    window.addEngineLog = function(message, type="info") {
      const box = document.getElementById('leftLogsBox');
      if(!box) return;
      const time = new Date().toLocaleTimeString();
      let color = "#a7f3d0";
      if (type === "warn") color = "#fcd34d";
      if (type === "error") color = "#fca5a5";
      box.innerHTML += <div style="color: ; margin-bottom: 4px; padding-bottom: 2px; border-bottom: 1px solid rgba(255,255,255,0.05);">[] </div>;
      box.scrollTop = box.scrollHeight;
    };
  </script>
</body>'''

new_html = new_html.replace('</body>', js_func)

with open('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\public\\pocket_director.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
print("PATCH APLICADO COM SUCESSO!")
