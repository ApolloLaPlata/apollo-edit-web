const fs = require('fs');
const file = 'services/geminiService.ts';
let code = fs.readFileSync(file, 'utf8');
code = code.replace(/contents: \{ parts \}/g, 'contents: [{ role: "user", parts }]');
fs.writeFileSync(file, code);
console.log("Replaced all instances");
