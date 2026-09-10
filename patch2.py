import re

with open('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\public\\pocket_director.html', 'r', encoding='utf-8') as f:
    html = f.read()

# I want to inject the setInterval into the script block
old_script = '''    window.addEngineLog = function(message, type="info") {
      const box = document.getElementById('leftLogsBox');
      if(!box) return;
      const time = new Date().toLocaleTimeString();
      let color = "#a7f3d0";
      if (type === "warn") color = "#fcd34d";
      if (type === "error") color = "#fca5a5";
      box.innerHTML += <div style="color: ; margin-bottom: 4px; padding-bottom: 2px; border-bottom: 1px solid rgba(255,255,255,0.05);">[] </div>;
      box.scrollTop = box.scrollHeight;
    };'''

new_script = old_script + '''

    // Sincronizar logs do backend na mesma tela
    setInterval(async () => {
      try {
        const res = await fetch('/api/colmeia/logs', { timeout: 2000 });
        if(res.ok) {
          const logs = await res.text();
          if (logs && logs.trim() !== '') {
            const box = document.getElementById('leftLogsBox');
            if (box && box.innerText.indexOf(logs) === -1) {
              // Limpa se estiver muito grande
              if (box.innerHTML.length > 50000) box.innerHTML = '';
              const time = new Date().toLocaleTimeString();
              box.innerHTML += <div style="color: #a7f3d0; margin-bottom: 4px; padding-bottom: 2px; border-bottom: 1px solid rgba(255,255,255,0.05);">[] [BACKEND] </div>;
              box.scrollTop = box.scrollHeight;
            }
          }
        }
      } catch(e) {
        // Ignora erros silenciosamente para não floodar
      }
    }, 2000);
'''

new_html = html.replace(old_script, new_script)

with open('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\public\\pocket_director.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
print("Patcher executado")
