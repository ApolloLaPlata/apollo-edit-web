const fs = require('fs');
const html = fs.readFileSync('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'utf8');
const match = html.match(/<script>([\s\S]*?)<\/script>/i);
if (match) {
    fs.writeFileSync('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/script_test.js', match[1]);
    console.log("Extracted JS to script_test.js");
}
