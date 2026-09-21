const fs = require('fs');
const path = require('path');

function replaceInDir(dir, search, replace) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      replaceInDir(fullPath, search, replace);
    } else if (fullPath.endsWith('.ts') || fullPath.endsWith('.tsx') || fullPath.endsWith('.js')) {
      let content = fs.readFileSync(fullPath, 'utf8');
      if (content.includes(search)) {
        content = content.split(search).join(replace);
        fs.writeFileSync(fullPath, content, 'utf8');
        console.log(`Updated: ${fullPath}`);
      }
    }
  }
}

const srcDir = path.resolve(__dirname, 'src');
replaceInDir(srcDir, 'meta-llama/Llama-3.1-8B-Instruct', 'llama-3.3-70b-versatile');

console.log('Model replacement complete to llama-3.3-70b-versatile.');
