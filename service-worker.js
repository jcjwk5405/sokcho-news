/* ═══════════════════════════════════════════════════
   설악시민뉴스 Service Worker v2.0
   - 캐시 완전 초기화 버전
   ═══════════════════════════════════════════════════ */

const CACHE_NAME = 'sokcho-news-v2';

/* ── 설치 즉시 활성화 ── */
self.addEventListener('install', event => {
  self.skipWaiting();
});

/* ── 활성화: 모든 구버전 캐시 삭제 ── */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(name => {
          console.log('[SW] 캐시 삭제:', name);
          return caches.delete(name);
        })
      );
    }).then(() => self.clients.claim())
  );
});

/* ── fetch: 항상 네트워크 우선 ── */
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
