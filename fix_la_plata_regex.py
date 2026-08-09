import sys
import re

filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\frontend\la_plata.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# REPLACE IMAGE GENERATION FETCH
# We use regex to match from "const response = await fetch(https://generativelanguage.googleapis.com" to "});"
img_pattern = re.compile(r'const response = await fetch\(https://generativelanguage\.googleapis\.com/v1beta/models/gemini-1\.5-flash:generateContent\?key=\$\{geminiApiKey\},\s*\{.*?\n\s*\}\);', re.DOTALL)
replacement_img = '''const response = await fetch('/api/lightning_proxy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            model: 'gpt-4o',
            messages: [{
                role: 'user',
                content: [
                    { type: 'text', text: "Analise esta imagem." },
                    { type: 'image_url', image_url: { url: data:;base64, } }
                ]
            }]
        })
    });'''

content = img_pattern.sub(replacement_img, content, count=1)

txt_pattern = re.compile(r'const response = await fetch\(https://generativelanguage\.googleapis\.com/v1beta/models/\$\{model\}:generateContent\?key=\$\{geminiApiKey\},\s*\{.*?\n\s*\}\);', re.DOTALL)
replacement_txt = '''const response = await fetch('/api/lightning_proxy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            model: 'nvidia-nemotron-3-ultra-550b-a55b',
            messages: [{ role: 'user', content: fullPrompt }],
            temperature: temperature,
            max_tokens: maxTokens
        })
    });'''

content = txt_pattern.sub(replacement_txt, content, count=1)

content = content.replace('data.candidates[0].content.parts[0].text', 'data.choices[0].message.content')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('LA PLATA REGEX CONCLUIDO')
