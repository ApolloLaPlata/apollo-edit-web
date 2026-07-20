import os

filepath = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\transfer_hud.js'
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

# Replace alerts with showToast
content = content.replace("alert('Tocando", "showToast('Tocando")
content = content.replace("alert('Exibindo", "showToast('Exibindo")
content = content.replace("alert(`Item ${itemType} encaixado com sucesso no slot!`);", "showToast(`Item ${itemType} encaixado com sucesso no slot!`, 'success');")
content = content.replace("alert('Consumindo 5 cargas", "showToast('Consumindo 5 cargas")
content = content.replace("alert(`Este slot n", "showToast(`Este slot n")

# We need to be careful with the backticks in the last one, it was alert(`Este slot não aceita o tipo: ${itemType}`);
# Since it's a bit tricky due to encoding of ã (nǜo), let's use regex or a simpler replace.
import re
content = re.sub(r"alert\('Tocando [^']+'\)", "if(typeof showToast==='function'){showToast('Tocando Áudio...');}", content)
content = re.sub(r"alert\('Exibindo Preview\.\.\.'\)", "if(typeof showToast==='function'){showToast('Exibindo Preview...', 'info');}", content)
content = re.sub(r"alert\(`Item \${itemType} encaixado com sucesso no slot!`\)", "if(typeof showToast==='function'){showToast(`Item ${itemType} encaixado!`, 'success');}", content)
content = re.sub(r"alert\('Consumindo 5 cargas[^']+'\)", "if(typeof showToast==='function'){showToast('Consumindo cargas de API...', 'warning');}", content)

# General alert replacement for backticks
content = re.sub(r"alert\(`Este slot n[^\`]+`\)", "if(typeof showToast==='function'){showToast(`Tipo incompatível: ${itemType}`, 'error');}", content)

with open(filepath, 'w', encoding='latin-1') as f:
    f.write(content)
print("transfer_hud.js patched!")
