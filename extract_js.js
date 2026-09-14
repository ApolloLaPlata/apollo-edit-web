const fs = require('fs');
const html = fs.readFileSync('frontend/modal_ai_studio.html', 'utf-8');
const scriptRegex = /<script\b[^>]*>([\s\S]*?)<\/script>/gm;
let match;
let i = 0;
while ((match = scriptRegex.exec(html)) !== null) {
    const code = match[1];
    fs.writeFileSync('temp_script_' + i + '.js', code);
    console.log('Extracted script ' + i);
    i++;
}
