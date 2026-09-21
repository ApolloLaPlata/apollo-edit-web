import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const config = {
  matcher: [
    /*
     * Intercepta todas as requisições, exceto:
     * - api (rotas de API)
     * - _next/static (arquivos estáticos)
     * - _next/image (arquivos de otimização de imagem)
     * - favicon.ico, sitemap.xml, robots.txt (arquivos genéricos)
     * - /uploads (pasta que os bots salvam as imagens locais)
     * - /admin (painel de controle global)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|uploads|admin).*)',
  ],
};

// Dicionário na memória para Rate Limiting (Funciona bem em instâncias Node.js/VPS)
const rateLimitMap = new Map<string, { count: number; lastReset: number }>();
const RATE_LIMIT_WINDOW_MS = 60000; // 1 minuto
const RATE_LIMIT_MAX_REQUESTS = 120; // 120 requisições por minuto

export default function middleware(req: NextRequest) {
  const url = req.nextUrl;
  
  // ==========================================
  // FASE 84: ESCUDO ANTI-BOT (Scraping & Spam)
  // ==========================================
  const userAgent = req.headers.get('user-agent')?.toLowerCase() || '';
  const badBots = ['python-requests', 'scrapy', 'curl', 'wget', 'postman', 'insomnia', 'urllib', 'java', 'httpclient', 'nikto', 'nmap', 'sqlmap'];
  
  // Lista de bots benignos que DEVEMOS permitir para SEO
  const allowedBots = ['googlebot', 'bingbot', 'yandex', 'slurp', 'duckduckbot', 'baiduspider', 'twitterbot', 'facebookexternalhit'];
  
  // Se o User Agent contiver a palavra 'bot', verificamos se é um dos permitidos
  const containsBotString = userAgent.includes('bot') || userAgent.includes('spider') || userAgent.includes('crawl');
  
  const isBadBot = badBots.some(bot => userAgent.includes(bot));
  const isAllowedBot = allowedBots.some(bot => userAgent.includes(bot));

  if ((isBadBot || containsBotString) && !isAllowedBot) {
    console.log(`[ESCUDO] 🛡️ Ataque bloqueado! User-Agent banido: ${userAgent}`);
    return new NextResponse('Forbidden: Automations and Scraping are blocked by AntiGravity Shield.', { status: 403 });
  }

  // ==========================================
  // FASE V3: RATE-LIMIT EDGE (Anti-DDoS Básico) (PASSO 62)
  // ==========================================
  const clientIp = req.headers.get('x-forwarded-for') || (req as any).ip || '127.0.0.1';
  const isLocal = clientIp.startsWith('10.') || clientIp.startsWith('172.16.') || clientIp.startsWith('192.168.') || clientIp === '127.0.0.1' || clientIp === '::1';
  
  if (!isLocal && !isAllowedBot) {
     const now = Date.now();
     const clientData = rateLimitMap.get(clientIp);

     if (!clientData) {
       rateLimitMap.set(clientIp, { count: 1, lastReset: now });
     } else {
       if (now - clientData.lastReset > RATE_LIMIT_WINDOW_MS) {
         // Reset after window passes
         clientData.count = 1;
         clientData.lastReset = now;
       } else {
         clientData.count++;
         if (clientData.count > RATE_LIMIT_MAX_REQUESTS) {
           console.log(`[DDoS SHIELD] 💥 Rajada Bloqueada! IP: ${clientIp} (Count: ${clientData.count})`);
           // Ban temporário (retorna 429 Too Many Requests)
           return new NextResponse('Too Many Requests. Rate limit exceeded. IP temporarily blocked.', { 
             status: 429,
             headers: { 'Retry-After': '60' }
           });
         }
       }
     }
  }

  // Limpeza de memória do Map a cada 1000 IPs registrados (Prevenção de vazamento de memória)
  if (rateLimitMap.size > 5000) {
     rateLimitMap.clear();
  }

  // Pega o hostname da requisição (ex: observadoreconomico.com, localhost:3000)
  const hostname = req.headers.get('host') || 'localhost:3000';
  
  // Caminho original acessado (ex: /, /blog/artigo-1)
  const path = url.pathname;
  
  // ==========================================
  // FASE V3: CÉREBRO DE TRADUÇÃO I18N
  // ==========================================
  // Ler o idioma do navegador do visitante
  let locale = 'pt'; // Default fallback
  const acceptLanguage = req.headers.get('accept-language');
  
  if (acceptLanguage) {
    if (acceptLanguage.includes('en')) locale = 'en';
    else if (acceptLanguage.includes('es')) locale = 'es';
  }

  // ==========================================
  // FASE V4 (OMNIVERSE): ROTEAMENTO SAAS MULTI-TENANT
  // ==========================================
  // Se o cliente acessar joao.autoblog.com, o sistema deve entender que é o Tenant "joao"
  // e carregar apenas as notícias que a IA dele gerou, com as cores dele!
  
  // Exemplo: host = "joao.autoblog.com" ou "autoblog.com"
  const isCustomDomain = hostname.includes('.') && !hostname.includes('localhost') && !hostname.includes('vercel.app');
  let currentTenant = 'master'; // Você, o dono do software.

  if (isCustomDomain) {
    const parts = hostname.split('.');
    if (parts.length > 2 && parts[0] !== 'www') {
      currentTenant = parts[0]; // Puxa "joao" de "joao.autoblog.com"
    }
  }

  // Se a requisição for para rotas internas (Painel Admin, API, Imagens, Uploads)
  // Nós NÃO fazemos rewrite do domínio, apenas repassamos.
  if (path.startsWith('/api') || path.startsWith('/_next') || path.startsWith('/admin') || path.startsWith('/uploads') || path === '/favicon.ico') {
    const response = NextResponse.next();
    
    // ==========================================
    // FASE 58: CORS RÍGIDO PARA ROTAS DA API
    // ==========================================
    if (path.startsWith('/api')) {
      const origin = req.headers.get('origin');
      if (origin && !isLocal) {
        const allowedOriginPattern = /.*\.?(autoblog\.com|localhost|seu-dominio-principal\.com)$/;
        if (!allowedOriginPattern.test(origin)) {
           console.log(`[CORS SHIELD] 🚫 API Access Denied for Origin: ${origin}`);
           return new NextResponse('CORS Policy: Access Denied. Origin not allowed.', { status: 403 });
        }
        response.headers.set('Access-Control-Allow-Origin', origin);
        response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
      }
    }

    // ==========================================
    // FASE 112: SINGLE SIGN-ON (SSO) FOUNDATION
    // ==========================================
    if (path.startsWith('/admin') && path !== '/admin/login') {
      const token = req.cookies.get('apollo_sso_token')?.value;
      
      // Simulação rápida de JWT Verification. O Apollo dita quem pode acessar.
      // Sem token = redireciona para login (que vai atuar de bridge pro Apollo)
      if (!token) {
         return NextResponse.redirect(new URL('/admin/login', req.url));
      }
    }

    // ==========================================
    // FASE 84: HEADERS DE SEGURANÇA MILITAR
    // ==========================================
    response.headers.set('X-DNS-Prefetch-Control', 'on');
    response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
    response.headers.set('X-XSS-Protection', '1; mode=block');
    response.headers.set('X-Frame-Options', 'SAMEORIGIN'); // Impede Clickjacking
    response.headers.set('X-Content-Type-Options', 'nosniff'); // Impede MIME-Sniffing
    response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    
    return response;
  }

  // ==========================================
  // ROTEAMENTO SAAS MULTI-TENANT (O Pulo do Gato)
  // ==========================================
  // Qualquer outra requisição (Home, Artigos, Categorias) será reescrita 
  // para dentro da pasta `src/app/[domain]/...`
  // Ex: joao.com/blog/artigo -> /joao.com/blog/artigo
  const response = NextResponse.rewrite(
    new URL(`/${hostname}${path}`, req.url)
  );

  // Headers de segurança também na rota pública
  response.headers.set('X-DNS-Prefetch-Control', 'on');
  response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('X-Frame-Options', 'SAMEORIGIN'); 
  response.headers.set('X-Content-Type-Options', 'nosniff'); 
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  return response;
}
