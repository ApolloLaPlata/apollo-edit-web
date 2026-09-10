const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'utf8');
const scriptRegex = /<script\b[^>]*>([\s\S]*?)<\/script>/gi;
let match;
let hasError = false;

while ((match = scriptRegex.exec(html)) !== null) {
    const code = match[1];
    if (code.trim() === '') continue;
    
    try {
        new vm.Script(code);
    } catch (e) {
        console.error('Syntax Error found in <script> tag:');
        console.error(e.message);
        hasError = true;
    }
}

if (!hasError) {
    console.log('All inline JavaScript is syntax-error free!');
}
