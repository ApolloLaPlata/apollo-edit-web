import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\pocket_app.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

search1 = '    await this.checkEnvironmentIntegrity();'
replace1 = '    await this.checkEnvironmentIntegrity();\n    await this.loadVoiceCatalog();'

search2 = '  async testDirectorTTS() {'
replace2 = '''  async loadVoiceCatalog() {
    try {
      const res = await fetch("/api/voice/catalog");
      const data = await res.json();
      if(data.success && this.voiceSelect) {
        this.voiceSelect.innerHTML = "";
        let currentGroup = "";
        let optgroup = null;
        data.catalog.forEach(v => {
          if(v.type !== currentGroup) {
            currentGroup = v.type;
            optgroup = document.createElement("optgroup");
            optgroup.label = v.type === "standard" ? "⚡ Vozes Nativas (Kokoro)" : "🧬 Clones de Voz (XTTSv2)";
            this.voiceSelect.appendChild(optgroup);
          }
          const opt = document.createElement("option");
          opt.value = v.id;
          opt.textContent = v.name;
          if(optgroup) optgroup.appendChild(opt);
          else this.voiceSelect.appendChild(opt);
        });
      }
    } catch(e) { console.error("Erro carregando vozes:", e); }
  }

  async testDirectorTTS() {'''

if search1 in content and search2 in content:
    content = content.replace(search1, replace1).replace(search2, replace2)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Sucesso!")
else:
    print("Falhou em achar o alvo")
