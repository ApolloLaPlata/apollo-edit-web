import sys

filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\frontend\la_plata.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# REPLACE IMAGE GENERATION FETCH
target_img = '''    const response = await fetch(https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            contents: [{
                parts: [
                    {
                        text: "Analise esta imagem e crie uma descrição detalhada e profissional que possa ser usada para recriar a imagem com IA. Inclua detalhes sobre: composição, cores, iluminação, estilo, elementos visuais, texturas, atmosfera e qualquer outro aspecto importante. A descrição deve ser precisa e técnica, adequada para geração de imagens com IA."
                    },
                    {
                        inline_data: {
                            mime_type: file.type,
                            data: base64.split(',')[1]
                        }
                    }
                ]
            }]
        })
    });'''

replacement_img = '''    const response = await fetch('/api/lightning_proxy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            model: 'gpt-4o', // Lightning AI roteia vision para GPT-4o ou LLava
            messages: [{
                role: 'user',
                content: [
                    { type: 'text', text: "Analise esta imagem e crie uma descrição detalhada e profissional que possa ser usada para recriar a imagem com IA. Inclua detalhes sobre: composição, cores, iluminação, estilo, elementos visuais, texturas, atmosfera e qualquer outro aspecto importante. A descrição deve ser precisa e técnica, adequada para geração de imagens com IA." },
                    { type: 'image_url', image_url: { url: data:;base64, } }
                ]
            }]
        })
    });'''

if target_img in content:
    content = content.replace(target_img, replacement_img)
else:
    print('ALVO IMG NAO ENCONTRADO')


# REPLACE TEXT FETCH
target_txt = '''    const response = await fetch(https://generativelanguage.googleapis.com/v1beta/models/:generateContent?key=, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            contents: [{
                parts: [{
                    text: fullPrompt
                }]
            }],
            generationConfig: {
                temperature: temperature,
                maxOutputTokens: maxTokens
            }
        })
    });'''

replacement_txt = '''    const response = await fetch('/api/lightning_proxy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            model: 'nvidia-nemotron-3-ultra-550b-a55b',
            messages: [{ role: 'user', content: fullPrompt }],
            temperature: temperature,
            max_tokens: maxTokens
        })
    });'''

if target_txt in content:
    content = content.replace(target_txt, replacement_txt)
else:
    print('ALVO TXT NAO ENCONTRADO')

# ALSO REPLACE RESPONSE PARSING
target_parse_img = '''    const data = await response.json();
    return data.candidates[0].content.parts[0].text;'''
    
replacement_parse = '''    const data = await response.json();
    return data.choices[0].message.content;'''

if target_parse_img in content:
    content = content.replace(target_parse_img, replacement_parse)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('LA PLATA SUBSTITUIDO COM SUCESSO')
