import re
with open('public/pocket_app.js', 'r', encoding='utf-8') as f:
  c = f.read()
c = c.replace("              this.addTranscriptCard(\\'user\\', cmd, false);\n              this.sendToColmeia(JSON.stringify", "              this.addTranscriptCard('user', cmd, false);
              this.sendToColmeia(JSON.stringify")
with open('public/pocket_app.js', 'w', encoding='utf-8') as f:
  f.write(c)
