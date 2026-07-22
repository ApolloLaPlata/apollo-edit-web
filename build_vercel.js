const fs = require('fs');
const path = require('path');

function copyFolderSync(from, to) {
    if (!fs.existsSync(to)) fs.mkdirSync(to, { recursive: true });
    fs.readdirSync(from).forEach(element => {
        if (element === 'node_modules' || element === '.git') return;
        const fromPath = path.join(from, element);
        const toPath = path.join(to, element);
        if (fs.lstatSync(fromPath).isFile()) {
            fs.copyFileSync(fromPath, toPath);
        } else {
            copyFolderSync(fromPath, toPath);
        }
    });
}

const outDir = 'dist';
if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

if (fs.existsSync('web_ui')) {
    console.log(`Copying web_ui to ${outDir}...`);
    copyFolderSync('web_ui', outDir);
}

if (fs.existsSync(path.join(outDir, 'hub.html'))) {
    console.log('Renaming hub.html to index.html for root access...');
    fs.copyFileSync(path.join(outDir, 'hub.html'), path.join(outDir, 'index.html'));
}

console.log('Vercel Node Build completed successfully.');
