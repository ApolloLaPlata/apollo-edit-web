import sys

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_code = '''                  const response = await fetch(url, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json', 'x-apollo-lock': 'apollo-beta-key-2026' },
                      body: JSON.stringify({ prompt, lyrics, model, duration, reference_audio_base64: refBase64 })
                  });
                  const rawText = await response.text();
                  let data;
                  try {
                      data = JSON.parse(rawText);
                  } catch(e) {
                      throw new Error(rawText.substring(0, 100));
                  }'''

new_code = '''                  const response = await fetch(url, {
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

if old_code in text:
    text = text.replace(old_code, new_code)
    print("Replaced!")
else:
    print("Old code not found! Trying fallback replace...")
    # fallback
    import re
    text = re.sub(
        r'const rawText = await response\.text\(\);\s*let data;\s*try \{\s*data = JSON\.parse\(rawText\);\s*\} catch\(e\) \{\s*throw new Error\(rawText\.substring\(0, 100\)\);\s*\}',
        new_code.split('});\n')[1],
        text
    )

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
