import sys

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_code = '''                  const rawText = await response.text();
                  let data;
                  try {
                      data = JSON.parse(rawText);
                  } catch(e) {
                      throw new Error(rawText.substring(0, 100));
                  }'''

new_code = '''                  const rawText = await response.text();
                  let data;
                  try {
                      const lines = rawText.split('\\n').map(l => l.trim()).filter(l => l.length > 0 && l.startsWith('{'));
                      if (lines.length > 0) {
                          data = JSON.parse(lines[lines.length - 1]);
                      } else {
                          throw new Error("Nenhum JSON encontrado");
                      }
                  } catch(e) {
                      throw new Error(rawText.substring(0, 100));
                  }'''

text = text.replace(old_code, new_code)

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
