const fs = require('fs');
const path = require('path');

function copyFolderSync(from, to) {
    if (!fs.existsSync(to)) fs.mkdirSync(to, { recursive: true });
    fs.readdirSync(from).forEach(element => {
        if (element === 'node_modules' || element === '.git' || element === 'dist' || element === 'public' || element === 'backend' || element === '.agents') return;
        const stat = fs.lstatSync(path.join(from, element));
        if (stat.isFile()) {
            if (element.endsWith('.html') || element.endsWith('.js') || element.endsWith('.css') || element.endsWith('.json') || element.endsWith('.png') || element.endsWith('.jpg') || element.endsWith('.svg') || element.endsWith('.ico')) {
                fs.copyFileSync(path.join(from, element), path.join(to, element));
            }
        } else if (stat.isDirectory()) {
            copyFolderSync(path.join(from, element), path.join(to, element));
        }
    });
}

console.log("Copying files to public...");
copyFolderSync('.', 'public');

console.log("Writing dummy index.html at root of public...");
fs.writeFileSync('public/index.html', '<!DOCTYPE html><html><head><script>window.location.href="/hub.html";</script></head><body></body></html>');

const vercelJson = {
  "framework": null,
  "buildCommand": null,
  "outputDirectory": "public",
  "redirects": [
    {
      "source": "/web_ui/(.*)",
      "destination": "/$1",
      "permanent": false
    }
  ]
};
fs.writeFileSync('vercel.json', JSON.stringify(vercelJson, null, 2));

console.log("Done!");
