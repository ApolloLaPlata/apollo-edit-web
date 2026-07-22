const fs = require('fs');

console.log("Renaming web_ui to dist...");
fs.renameSync('web_ui', 'dist');

console.log("Creating index.html...");
if (fs.existsSync('dist/hub.html')) {
    fs.copyFileSync('dist/hub.html', 'dist/index.html');
}

console.log("Copying dist to public and build to satisfy any Vercel preset...");
fs.cpSync('dist', 'public', { recursive: true });
fs.cpSync('dist', 'build', { recursive: true });

console.log("Vercel Node Build completed successfully.");
