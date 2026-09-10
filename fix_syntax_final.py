import sys

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Match the entire try block inside generateMusicTest
pattern = re.compile(r'const url = \'/api/studio/modal/generate/audio_lab\';\s+const response = await fetch\(url, \{.*?\n\s+if \(!response\.ok\).*?if \(!data\) \{\s*throw new Error\(Nenhum dado valido retornado: \$\{rawText\.substring\(0,100\)\}\);\s*\}', re.DOTALL)

new_block = '''const url = '/api/studio/modal/generate/audio_lab';
                  const response = await fetch(url, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json', 'x-apollo-lock': 'apollo-beta-key-2026' },
                      body: JSON.stringify({ prompt, lyrics, model, duration, reference_audio_base64: refBase64 })
                  });
                                    
                    if (!response.ok) {
                        const errText = await response.text();
                        throw new Error(HTTP : );
                    }
                    
                    const rawText = await response.text();
                    let data = null;
                    
                    // Tratamento robusto para lidar com streaming NDJSON que pode vir do Oracle
                    const lines = rawText.trim().split('\\n');
                    for (let i = lines.length - 1; i >= 0; i--) {
                        if (lines[i].trim() === "") continue;
                        try {
                            const parsed = JSON.parse(lines[i]);
                            if (parsed.status === 'success' || parsed.status === 'error') {
                                data = parsed;
                                break;
                            }
                        } catch(e) {}
                    }
                    
                    if (!data) {
                        throw new Error(Nenhum dado valido retornado: );
                    }'''

# Replace the broken syntax block
if pattern.search(text):
    text = pattern.sub(new_block, text)
else:
    print("Pattern not found! Trying fallback")
    # Fallback: Just replace the exact string that is broken
    text = text.replace("const lines = rawText.trim().split('\n  ');", "const lines = rawText.trim().split('\\n');")
    text = text.replace("const lines = rawText.trim().split('\r\n  ');", "const lines = rawText.trim().split('\\n');")

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
