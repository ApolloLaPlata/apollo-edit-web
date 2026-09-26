const fs = require('fs');
const path = require('path');

const templatesDir = path.join(__dirname, 'src/components/blog/templates');
const files = fs.readdirSync(templatesDir).filter(f => f.endsWith('.tsx'));

const replacements = [
  { 
    pattern: /post\.blog_name/g, 
    replace: "(post as any).blog_name" 
  }
];

let changedFiles = 0;

for (const file of files) {
  const filePath = path.join(templatesDir, file);
  let content = fs.readFileSync(filePath, 'utf8');
  let originalContent = content;

  for (const { pattern, replace } of replacements) {
    content = content.replace(pattern, replace);
  }

  if (content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Fix aplicado: ${file}`);
    changedFiles++;
  }
}

console.log(`\nTS Fix Concluído.`);
