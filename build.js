const fs = require('fs');
const path = require('path');

function copyFolderSync(from, to) {
    if (!fs.existsSync(to)) fs.mkdirSync(to, { recursive: true });
    fs.readdirSync(from).forEach(element => {
        const fromPath = path.join(from, element);
        const toPath = path.join(to, element);
        if (fs.lstatSync(fromPath).isFile()) {
            fs.copyFileSync(fromPath, toPath);
        } else {
            copyFolderSync(fromPath, toPath);
        }
    });
}

// Vercel output directories (we create all 3 to ensure one of them is picked up depending on Vercel's legacy settings)
const outputDirs = ['dist', 'build', 'public'];

outputDirs.forEach(outDir => {
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }
    
    // Copy frontend to root of output
    if (fs.existsSync('frontend')) {
        console.log(`Copying frontend to ${outDir}`);
        copyFolderSync('frontend', outDir);
    }

    // Also create web_ui inside output to support legacy redirects (www.apolloedit.com.br/web_ui/hub.html)
    const webUiOut = path.join(outDir, 'web_ui');
    if (!fs.existsSync(webUiOut)) fs.mkdirSync(webUiOut, { recursive: true });
    
    // Some old bookmarks might point to web_ui, so let's copy frontend contents there too
    if (fs.existsSync('frontend')) {
        console.log(`Copying frontend to ${webUiOut} for legacy support`);
        copyFolderSync('frontend', webUiOut);
    }
    
    // Also copy the actual web_ui folder if it exists, just in case it has different files
    if (fs.existsSync('web_ui')) {
        console.log(`Copying web_ui to ${webUiOut}`);
        copyFolderSync('web_ui', webUiOut);
    }
});

console.log('Build completed successfully.');
