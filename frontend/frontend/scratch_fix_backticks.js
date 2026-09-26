const fs = require('fs');
const path = require('path');

function walk(dir, done) {
  let results = [];
  fs.readdir(dir, function(err, list) {
    if (err) return done(err);
    let pending = list.length;
    if (!pending) return done(null, results);
    list.forEach(function(file) {
      file = path.resolve(dir, file);
      fs.stat(file, function(err, stat) {
        if (stat && stat.isDirectory()) {
          walk(file, function(err, res) {
            results = results.concat(res);
            if (!--pending) done(null, results);
          });
        } else {
          results.push(file);
          if (!--pending) done(null, results);
        }
      });
    });
  });
}

walk('E:\\MEUS PROGRAMAS\\AUTO_BLOG_CMS\\frontend\\src', function(err, results) {
  if (err) throw err;
  const tsxFiles = results.filter(f => f.endsWith('.tsx') || f.endsWith('.ts'));
  let fixedCount = 0;
  
  tsxFiles.forEach(file => {
    let content = fs.readFileSync(file, 'utf8');
    let original = content;
    
    // Corrige {\` para {`
    content = content.replace(/\{\\`/g, '{`');
    // Corrige \`} para `}
    content = content.replace(/\\`\}/g, '`}');
    // Corrige \${ para ${
    content = content.replace(/\\\$\{/g, '${');
    // Corrige \` no meio de propriedades JSX como href={\`/blog...
    content = content.replace(/=\\{\\`/g, '={`');
    
    // As vezes a crase escaped tá solta tipo \` 
    content = content.replace(/\\`/g, '`');

    if (content !== original) {
      fs.writeFileSync(file, content, 'utf8');
      console.log('Fixed:', file);
      fixedCount++;
    }
  });
  console.log('Total files fixed:', fixedCount);
});
