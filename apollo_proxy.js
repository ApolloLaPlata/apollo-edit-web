const http = require('http');
const https = require('https');

const server = http.createServer((req, res) => {
    // Liberar CORS total para o navegador
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'OPTIONS, POST');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    if (req.url === '/api/chat' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            const options = {
                hostname: 'lightning.ai',
                path: '/api/v1/chat/completions',
                method: 'POST',
                headers: {
                    'Authorization': req.headers.authorization,
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(body)
                }
            };

            const proxyReq = https.request(options, proxyRes => {
                // Remove headers que podem dar conflito
                delete proxyRes.headers['access-control-allow-origin'];
                res.writeHead(proxyRes.statusCode, proxyRes.headers);
                proxyRes.pipe(res);
            });

            proxyReq.on('error', e => {
                res.writeHead(500, {'Content-Type': 'application/json'});
                res.end(JSON.stringify({error: e.message}));
            });

            proxyReq.write(body);
            proxyReq.end();
        });
    } else {
        res.writeHead(404);
        res.end('Not Found');
    }
});

server.listen(4000, () => {
    console.log('🤖 APOLLO CORS PROXY INICIADO!');
    console.log('O túnel para a Lightning AI está aberto na porta 4000.');
    console.log('Pode usar o chat no navegador agora!');
});
