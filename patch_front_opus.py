# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/pocket_app.js'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = r'''      this.ws.onmessage = \(event\) => \{
        if \(typeof event.data === 'string'\) \{
          const data = JSON.parse\(event.data\);
          this.handleServerEvent\(data\);
        \}
      \};'''

new_block = r'''      this.ws.onmessage = (event) => {
        if (typeof event.data === 'string') {
          const data = JSON.parse(event.data);
          this.handleServerEvent(data);
        } else if (event.data instanceof Blob || event.data instanceof ArrayBuffer) {
          // Áudio Opus recebido da nuvem via WebSocket
          console.log("ðŸŽ§ Áudio Opus recebido! Tocando...");
          const blob = event.data instanceof Blob ? event.data : new Blob([event.data], {type: 'audio/ogg; codecs=opus'});
          const audioUrl = URL.createObjectURL(blob);
          const audio = new Audio(audioUrl);
          audio.volume = this.ttsVolume || 1.0;
          audio.play().catch(e => console.error("Erro ao tocar Opus:", e));
          
          // Cleanup
          audio.onended = () => URL.revokeObjectURL(audioUrl);
        }
      };'''

text = re.sub(old_block, new_block, text)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch Opus player em pocket_app.js aplicado!")
