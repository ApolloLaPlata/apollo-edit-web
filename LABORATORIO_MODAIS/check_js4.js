const fs = require('fs');
const html = fs.readFileSync('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'utf8');
const match = html.match(/<script>([\s\S]*?)<\/script>/i);
fs.writeFileSync('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/script_test4.js', match[1]);
