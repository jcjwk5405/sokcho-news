# index.html 패치 가이드 — 호외 발간 대응 (2026.09.28)
### 개정: 2026.09.26 — 9/26 시점 라이브 index.html 실제 문구에 맞춰 패치②의 BEFORE/AFTER 갱신

이 문서는 **완전한 index.html 대체본이 아닙니다.** 현재 라이브 index.html(제15호)은
계속 그대로 "현재호"로 유지되어야 하므로(제16호는 10/5 발행), 전체 파일을
새로 만들어 덮어쓰는 대신 **정확히 아래 두 군데만 찾아서 바꾸는 방식**을
권장합니다. (문서 작성일 기준 최신 적용 — 이 가이드가 기존 STEP F 체크리스트
4종과 충돌하지 않고, 호외라는 새로운 케이스에 대한 추가 규칙 역할을 합니다.)

⚠️ 9월 26일 기준으로 라이브 index.html의 속초 뉴스·편집자 레터 등 다른 부분이
일부 갱신되어 있었습니다(호외와 무관한 정기 업데이트). 아래 패치 ①·②는 그
9월 26일자 라이브 본문을 기준으로 다시 확인한 최신 버전입니다 — 이 버전의
BEFORE 텍스트로 다시 찾아서 적용하십시오.

---

## 패치 ① — 아카이브 목록에서 "호외"가 "제호외호"로 깨지지 않게

**파일:** `index.html`
**위치:** `<script>` 안 `loadArchive()` 함수, 아카이브 항목 렌더링 템플릿

### 찾기 (BEFORE)
```js
      return `
        <a class="archive-item${isCurrent ? ' current' : ''}"
           href="${isCurrent ? './' : 'archives/' + issue.filename}">
          <div class="archive-num">
            ${isCurrent ? '현재호' : '제' + issue.no + '호'}
            ${isCurrent ? '<span class="archive-badge">최신</span>' : ''}
          </div>
          <div class="archive-headline">${issue.headline}</div>
          <div class="archive-date">${issue.date}</div>
        </a>
        ${enHref ? `<a class="archive-en-link" href="${enHref}">🌐 English</a>` : ''}`;
```

### 바꾸기 (AFTER)
```js
      return `
        <a class="archive-item${isCurrent ? ' current' : ''}"
           href="${isCurrent ? './' : 'archives/' + issue.filename}">
          <div class="archive-num">
            ${isCurrent ? '현재호' : (typeof issue.no === 'string' ? issue.no : '제' + issue.no + '호')}
            ${isCurrent ? '<span class="archive-badge">최신</span>' : ''}
          </div>
          <div class="archive-headline">${issue.headline}</div>
          <div class="archive-date">${issue.date}</div>
        </a>
        ${enHref ? `<a class="archive-en-link" href="${enHref}">🌐 English</a>` : ''}`;
```

**바뀌는 부분은 단 한 줄**입니다:
```
- ${isCurrent ? '현재호' : '제' + issue.no + '호'}
+ ${isCurrent ? '현재호' : (typeof issue.no === 'string' ? issue.no : '제' + issue.no + '호')}
```
숫자 `no`(1, 2, 3 … 15)는 지금처럼 "제15호"로 그대로 표시되고, 문자열
`no: "호외"`만 "호외"로 그대로 표시됩니다. 기존 정기호 동작에는 전혀 영향이
없습니다.

---

## 패치 ② — 신문사공지 박스: "호외 발간 예정" → "호외 발간" (링크 추가)

**파일:** `index.html`
**위치:** `#s-announce` 섹션(신문사공지) 안, 추석 연휴 휴간 안내 박스

### 찾기 (BEFORE) — 2026.09.26 라이브 기준
```html
    <div style="background:#fff7ed;border:1px solid #fdba74;border-radius:8px;padding:14px 16px;margin-bottom:12px;">
      <div style="font-size:12px;font-weight:700;color:#9a3412;margin-bottom:8px;">📢 추석 연휴 휴간 안내</div>
      <div style="font-size:12px;line-height:1.7;color:#475569;">추석 연휴를 맞아 <strong>9월 28일(월)자 신문은 휴간</strong>합니다. 독자 여러분, 풍성하고 편안한 한가위 보내십시오.</div>
      <div style="margin-top:10px;padding-top:10px;border-top:1px dashed #fdba74;font-size:12px;line-height:1.7;color:#475569;">📰 <strong>호외 발간 예정</strong> — 휴간 기간에는 준비해 온 <strong style="color:#9a3412;">'설악권 6·3 선거결과 분석 완결판'</strong>을 호외로 발간할 예정입니다.<br><strong>[설악시민뉴스 6.3 선거특집 완결판] 정당이 아니라 사람이었다 — 2026 설악권 선거, 네 가지 진단</strong></div>
    </div>
```

### 바꾸기 (AFTER)
```html
    <div style="background:#fff7ed;border:1px solid #fdba74;border-radius:8px;padding:14px 16px;margin-bottom:12px;">
      <div style="font-size:12px;font-weight:700;color:#9a3412;margin-bottom:8px;">📢 추석 연휴 휴간 안내</div>
      <div style="font-size:12px;line-height:1.7;color:#475569;">추석 연휴를 맞아 <strong>9월 28일(월)자 신문은 휴간</strong>합니다. 독자 여러분, 풍성하고 편안한 한가위 보내십시오.</div>
      <div style="margin-top:10px;padding-top:10px;border-top:1px dashed #fdba74;font-size:12px;line-height:1.7;color:#475569;">
        📰 <strong>호외 발간</strong> — 휴간 기간 동안 준비해 온 <strong style="color:#9a3412;">'설악권 6·3 선거결과 분석 완결판'</strong>을 호외로 발간했습니다.<br>
        <strong>[설악시민뉴스 6.3 선거특집 완결판] 정당이 아니라 사람이었다 — 2026 설악권 선거, 네 가지 진단</strong>
        <div style="margin-top:8px;">
          <a href="archives/20260928.html" style="display:inline-block;background:#9a3412;color:#fff;font-size:12px;font-weight:700;padding:6px 14px;border-radius:6px;text-decoration:none;">📖 호외 전문 읽기 →</a>
        </div>
      </div>
    </div>
```

⚠️ 이전(9/19) 버전 가이드의 BEFORE 텍스트에는 `<strong style="color:#9a3412;">`
강조가 없었지만, 실제 라이브 페이지에는 이미 그 강조가 들어가 있습니다(그 사이
다른 갱신 때 함께 반영된 것으로 보입니다). 이 문서의 위 BEFORE 텍스트가 정확한
최신 버전이니 이 버전 기준으로 찾아 바꾸십시오.

바뀐 점: "발간 예정" → "발간"(완료형)으로 문구를 바꾸고, 호외 본문
(`archives/20260928.html`)으로 바로 가는 버튼을 추가했습니다.

---

## 패치가 끝나면

1. 위 두 군데만 바뀐 `index.html`을 저장소에 커밋·푸시합니다.
2. `archives/20260928.html`에 이번에 전달한 호외 페이지 파일을 그대로 업로드합니다.
3. `archives/manifest.json`의 `issues` 배열 맨 끝에 `manifest_호외_추가_스니펫.json`의
   항목을 추가합니다(제15호 항목은 그대로 둡니다 — 아직 index.html이 현재호이므로).
4. 브라우저에서 "📂 이전 신문" 패널을 열어 "호외"가 최상단에, 제대로 "호외"라고
   표시되는지, 클릭 시 `archives/20260928.html`로 이동하는지 확인합니다.
5. 신문사공지 섹션의 버튼을 눌러 호외 본문이 정상적으로 열리는지 확인합니다.

---

## 다음 정기발행(제16호, 2026.10.05)과의 관계

제16호를 새 index.html로 올릴 때는 기존 STEP F 체크리스트(① manifest
현재호등록 v1)를 그대로 따르면 됩니다 — 그때 제15호 항목의 `filename`을
`"index.html"`에서 `"20260921.html"`로 바꾸고, 제15호 페이지 사본을
`archives/20260921.html`로 저장소에 추가하면 됩니다. 이번 호외 항목(`no:
"호외"`)은 그 사이에도 그대로 배열에 남아 있으면 됩니다 — 위치만 제15호
항목보다 뒤(=더 최신)이면 순서가 올바르게 유지됩니다.
