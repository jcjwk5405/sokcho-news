/* ═══════════════════════════════════════════════════════════════
   설악시민뉴스 — 투표 시스템 vote.js
   버전: v1.0 | 2026.06.29
   역할: Firebase 초기화 + castVote + renderVote + initVotes
   로드 위치: index.html </body> 바로 위
            (firebase-app-compat.js, firebase-database-compat.js 다음)
   매호 수정: VOTE_APIKEY 한 곳만 (apiKey 변경 시)
              initVotes() 안의 ids 배열에 이번 호 id 추가
   ═══════════════════════════════════════════════════════════════ */

/* ── ★ 매호 수정 불필요 — Firebase 고정 설정 ── */
(function () {
  var VOTE_CONFIG = {
    apiKey:            'AIzaSyCHY5-_H22YgTGAbbp_NMcPE4QjwwwtfwE',
    databaseURL:       'https://eorak-citizen-news-default-rtdb.asia-southeast1.firebasedatabase.app',
    projectId:         'eorak-citizen-news',
    appId:             '1:367212604918:web:740d0156bc6043649a2bd7',
    messagingSenderId: '367212604918'
  };
  /* ★ databaseURL은 Firebase 콘솔 → Realtime Database → 데이터 탭에서 확인 필요
     현재 추정값: eorak-citizen-news-default-rtdb.asia-southeast1.firebasedatabase.app
     실제 URL이 다를 경우 위 databaseURL 수정 후 재업로드 */

  if (typeof firebase === 'undefined') {
    console.error('[vote.js] Firebase SDK 미로드 — firebase-app-compat.js, firebase-database-compat.js 먼저 로드하세요.');
    return;
  }

  if (!firebase.apps.length) {
    firebase.initializeApp(VOTE_CONFIG);
  }
  window._fbDb = firebase.database();
  console.log('[vote.js] Firebase 초기화 완료');
})();


/* ── 투표 실행 (전역 — HTML onclick에서 호출) ── */
function castVote(issueId, side) {
  var storageKey = 'vote_' + issueId;

  /* 중복 투표 방지 */
  var already;
  try { already = localStorage.getItem(storageKey); } catch (e) { /* noop */ }
  if (!already) { already = (window._localVotes || {})[issueId]; }
  if (already) { alert('이미 투표하셨습니다.'); return; }

  if (window._fbDb) {
    /* Firebase transaction — 서버 누적 */
    window._fbDb.ref('votes/' + issueId + '/' + side)
      .transaction(
        function (cur) { return (cur || 0) + 1; },
        function (err, committed) {
          if (err || !committed) {
            console.warn('[vote.js] Firebase 오류, localStorage 폴백:', err);
            _localVoteFallback(issueId, side);
          }
        }
      );
  } else {
    _localVoteFallback(issueId, side);
  }

  /* 중복 방지 마킹 — Firebase 성공 여부와 무관하게 기록 */
  try {
    localStorage.setItem(storageKey, side);
  } catch (e) {
    if (!window._localVotes) window._localVotes = {};
    window._localVotes[issueId] = side;
  }
}


/* ── localStorage 폴백 (Firebase 불가 환경) ── */
function _localVoteFallback(issueId, side) {
  var countKey = 'vcount_' + issueId;
  try {
    var stored = localStorage.getItem(countKey);
    var counts = stored ? JSON.parse(stored) : { pro: 0, con: 0 };
    counts[side] = (counts[side] || 0) + 1;
    localStorage.setItem(countKey, JSON.stringify(counts));
    renderVote(issueId, counts, side);
  } catch (e) {
    console.error('[vote.js] localStorage 폴백 실패:', e);
  }
}


/* ── 투표 결과 UI 렌더링 ── */
function renderVote(issueId, counts, voted) {
  var pro   = (counts.pro | 0);
  var con   = (counts.con | 0);
  var total = pro + con;
  var proPct = total ? Math.round(pro / total * 100) : 50;
  var conPct = total ? (100 - proPct) : 50;

  /* 숫자 뱃지 */
  var elPro = document.getElementById('vcnt-' + issueId + '-pro');
  var elCon = document.getElementById('vcnt-' + issueId + '-con');
  if (elPro) elPro.textContent = pro;
  if (elCon) elCon.textContent = con;

  /* 버튼 상태 — 섹션 + 모달 두 쌍 모두 처리 */
  ['', '-modal'].forEach(function (suffix) {
    var btnPro = document.getElementById('vbtn-' + issueId + '-pro' + suffix);
    var btnCon = document.getElementById('vbtn-' + issueId + '-con' + suffix);
    if (btnPro) {
      btnPro.classList.add('voted');
      if (voted === 'pro') btnPro.classList.add('selected');
    }
    if (btnCon) {
      btnCon.classList.add('voted');
      if (voted === 'con') btnCon.classList.add('selected');
    }
  });

  /* 결과 바 — 섹션 + 모달 두 곳 모두 */
  ['vresult-' + issueId, 'vresult-' + issueId + '-modal'].forEach(function (elId) {
    var el = document.getElementById(elId);
    if (!el) return;
    el.innerHTML =
      '<div class="vote-bar-wrap">' +
        '<div style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;margin-bottom:4px;">' +
          '<span style="color:#1F7A4D;">👍 찬성 ' + proPct + '% <small>(' + pro + '명)</small></span>' +
          '<span style="color:#B03030;">👎 반대 ' + conPct + '% <small>(' + con + '명)</small></span>' +
        '</div>' +
        '<div class="vote-bar-track">' +
          '<div class="vote-bar-fill-pro" style="width:' + proPct + '%;transition:width 0.5s;"></div>' +
        '</div>' +
        '<div style="color:#94a3b8;font-size:11px;text-align:center;margin-top:4px;">총 ' + total + '명 참여</div>' +
      '</div>';
  });
}


/* ── 페이지 로드 시 Firebase 실시간 리스너 등록 ──
   ★ 매호 수정: ids 배열에 이번 호 issueId가 포함되어 있는지만 확인
   (issue1~issue50 전체 미리 넣어도 무방 — DB에 없으면 counts=0 처리) ── */
function initVotes() {
  var ids = [
    'issue1','issue2','issue3','issue4','issue5',
    'issue6','issue7','issue8','issue9','issue10'
    /* 필요 시 issue11 이후 추가 */
  ];

  ids.forEach(function (id) {
    var voted;
    try { voted = localStorage.getItem('vote_' + id); } catch (e) {
      voted = (window._localVotes || {})[id];
    }

    if (window._fbDb) {
      /* Firebase 실시간 리스너 — 다른 기기 투표도 실시간 반영 */
      window._fbDb.ref('votes/' + id).on('value', function (snap) {
        var data   = snap.val() || {};
        var counts = { pro: data.pro || 0, con: data.con || 0 };
        if (voted || counts.pro > 0 || counts.con > 0) {
          renderVote(id, counts, voted);
        }
      });
    } else {
      /* 폴백: localStorage */
      var counts;
      try { counts = JSON.parse(localStorage.getItem('vcount_' + id) || '{"pro":0,"con":0}'); }
      catch (e) { counts = { pro: 0, con: 0 }; }
      if (voted || counts.pro > 0 || counts.con > 0) {
        renderVote(id, counts, voted);
      }
    }
  });
}
