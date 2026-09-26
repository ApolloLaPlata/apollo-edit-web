const fs = require('fs');
const path = require('path');

console.log("Creating dist directory...");
fs.mkdirSync('dist', { recursive: true });

console.log("Moving frontend files into dist to satisfy Vercel Vite preset limits...");
const files = fs.readdirSync('.');
files.forEach(file => {
    if (['dist', 'node_modules', '.git', 'build.js', 'package.json', 'vercel.json'].includes(file)) return;
    try {
        fs.renameSync(file, path.join('dist', file));
    } catch (e) {
        console.error("Failed to move " + file, e);
    }
});

console.log("Ensuring index.html exists in dist...");
if (fs.existsSync('dist/hub.html')) {
    fs.copyFileSync('dist/hub.html', 'dist/index.html');
}

console.log("Vercel Lightweight Node Build completed.");
