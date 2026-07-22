const fs = require('fs');
const path = require('path');

function copyFolderSync(from, to) {
    if (!fs.existsSync(to)) fs.mkdirSync(to, { recursive: true });
    fs.readdirSync(from).forEach(element => {
        // Skip node_modules and .git
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

// 1. Only target "dist" (which is what Vercel Vite preset expects)
const outDir = 'dist';
if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

// 2. Copy the actual interface (web_ui) to the root of dist
if (fs.existsSync('web_ui')) {
    console.log(`Copying web_ui to ${outDir}...`);
    copyFolderSync('web_ui', outDir);
}

// 3. Rename hub.html to index.html so it loads when visiting the root domain (/)
if (fs.existsSync(path.join(outDir, 'hub.html'))) {
    console.log('Renaming hub.html to index.html for root access...');
    fs.copyFileSync(path.join(outDir, 'hub.html'), path.join(outDir, 'index.html'));
}

// 4. Create web_ui inside dist so old cached URLs like /web_ui/hub.html still work perfectly
const webUiOut = path.join(outDir, 'web_ui');
if (!fs.existsSync(webUiOut)) {
    fs.mkdirSync(webUiOut, { recursive: true });
}
if (fs.existsSync('web_ui')) {
    console.log(`Copying web_ui to ${webUiOut} for legacy support...`);
    copyFolderSync('web_ui', webUiOut);
}

console.log('Vercel Dist Build completed successfully. Total size should be ~500MB, well under Vercel limits.');
