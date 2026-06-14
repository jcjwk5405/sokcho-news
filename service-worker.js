/* ═══════════════════════════════════════════════════
   설악시민뉴스 Service Worker v1.0
   - 오프라인에서도 마지막 호 열람 가능
   - 빠른 로딩 (캐시 우선)
   ═══════════════════════════════════════════════════ */

const CACHE_NAME = 'sokcho-news-v2';

/* 앱 설치 시 미리 캐시할 파일 목록 */
const PRE_CACHE = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png'
];

/* ── 설치 이벤트: 핵심 파일 사전 캐시 ── */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] 사전 캐시 설치 중...');
        return cache.addAll(PRE_CACHE);
      })
      .then(() => self.skipWaiting())
  );
});

/* ── 활성화 이벤트: 오래된 캐시 삭제 ── */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME)
          .map(name => {
            console.log('[SW] 구버전 캐시 삭제:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

/* ── fetch 이벤트: 네트워크 우선, 실패 시 캐시 사용 ── */
self.addEventListener('fetch', event => {
  /* POST 요청은 캐시 안 함 */
  if (event.request.method !== 'GET') return;

  /* 외부 API (GoatCounter 등)는 캐시 안 함 */
  const url = new URL(event.request.url);
  if (!url.origin.includes(self.location.hostname) &&
      !url.hostname.includes('fonts.googleapis.com') &&
      !url.hostname.includes('fonts.gstatic.com')) {
    return;
  }

  event.respondWith(
    /* 전략: 네트워크 우선 (최신 신문 항상 표시) */
    fetch(event.request)
      .then(response => {
        /* 성공하면 캐시에도 저장 */
        if (response && response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        /* 네트워크 실패 시 캐시에서 제공 (오프라인 모드) */
        return caches.match(event.request)
          .then(cached => {
            if (cached) {
              console.log('[SW] 오프라인 캐시 제공:', event.request.url);
              return cached;
            }
            /* 캐시도 없으면 index.html 반환 (SPA 폴백) */
            return caches.match('./index.html');
          });
      })
  );
});

/* ── 백그라운드 동기화: 새 호 발행 알림 (선택적) ── */
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
