const CACHE_NAME = 'auto-blog-v3-cache-v1';
const DYNAMIC_CACHE = 'auto-blog-v3-dynamic-v1';

// Recursos vitais para o site carregar instantaneamente, mesmo sem net.
const PRECACHE_URLS = [
  '/',
  '/manifest.json',
  '/offline',
  '/favicon.ico'
];

self.addEventListener('install', (event) => {
  console.log('[SW] 🚀 Service Worker Instalado (V3 Enterprise)');
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
});

self.addEventListener('activate', (event) => {
  console.log('[SW] ⚡ Service Worker Ativado (Limpando caches antigos...)');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== DYNAMIC_CACHE)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// ESTRATÉGIA DE CACHE: Stale-While-Revalidate (Ultra Rápido)
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Não faz cache de requisições POST (Ex: API de I.A ou Login)
  if (event.request.method !== 'GET') return;

  // Ignorar Analytics ou rotas sensíveis
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/admin')) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // Se está no cache, manda logo pra tela ser instantânea!
      // Em background (Stale-While-Revalidate), busca a versão nova na internet e atualiza o cache.
      const fetchPromise = fetch(event.request).then((networkResponse) => {
        caches.open(DYNAMIC_CACHE).then((cache) => {
          cache.put(event.request, networkResponse.clone());
        });
        return networkResponse;
      }).catch(() => {
         // Se a internet caiu, tenta retornar a página de Offline
         if (event.request.mode === 'navigate') {
            return caches.match('/offline');
         }
      });

      return cachedResponse || fetchPromise;
    })
  );
});
