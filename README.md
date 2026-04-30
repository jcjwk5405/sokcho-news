# 속초시민뉴스

**자유 · 정의 · 사랑의 시민언론**

속초시민뉴스 인터넷신문 — GitHub Pages + Claude AI 자동 업데이트

---

## 파일 구조

```
sokcho-citizens-news/
├── index.html                    ← 신문 본체 (이 파일이 사이트)
├── update.py                     ← AI 자동 업데이트 스크립트
├── requirements.txt              ← Python 패키지 목록
├── .github/
│   └── workflows/
│       └── update.yml            ← GitHub Actions 자동 실행 설정
└── README.md
```

---

## 섹션 구분

| 섹션 | 마커 | 관리 방식 |
|------|------|---------|
| 편집자 레터 | `MANUAL` | 편집장 직접 수정 |
| 금요 칼럼 | `MANUAL` | 원고 수령 후 직접 수정 |
| 기획연재 | `MANUAL` | 원고 작성 후 직접 수정 |
| 풍향계 | `AUTO` | Claude AI 자동 교체 |
| 주요 뉴스 | `AUTO` | Claude AI 자동 교체 |
| 여론동향 | `AUTO` | Claude AI 자동 교체 |
| 공지사항 | `AUTO` | Claude AI 자동 교체 |
| 속보 티커 | `AUTO` | Claude AI 자동 교체 |

---

## 초기 설정

### 1. GitHub 저장소 생성

```bash
# 저장소 이름을 반드시 아래 형식으로 만들어야 GitHub Pages 작동
# [내 계정명].github.io  또는 일반 저장소명 (Settings에서 Pages 활성화)
```

### 2. 파일 업로드

```bash
git init
git add .
git commit -m "속초시민뉴스 창간"
git remote add origin https://github.com/[계정명]/[저장소명].git
git push -u origin main
```

### 3. GitHub Pages 활성화

1. 저장소 → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** / **/ (root)**
4. Save 클릭
5. 잠시 후 `https://[계정명].github.io/[저장소명]` 에서 확인

### 4. API 키 등록 (자동 업데이트 필수)

1. 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
3. Name: `ANTHROPIC_API_KEY`
4. Secret: Anthropic API 키 입력
5. Add secret

---

## 사용 방법

### 자동 업데이트 (매주 월요일 자동)

GitHub Actions가 매주 월요일 오전 6시(한국시간)에 자동으로:
- 풍향계, 주요뉴스, 여론동향, 공지사항, 속보티커를 Claude AI로 업데이트
- index.html 커밋 후 GitHub Pages에 자동 배포

### 수동 업데이트

**방법 A: GitHub Actions에서 직접 실행**
1. 저장소 → **Actions** 탭
2. "속초시민뉴스 자동 업데이트" 선택
3. **Run workflow** 클릭
4. 특정 섹션만 할 경우 섹션명 입력 (예: `풍향계`)

**방법 B: 로컬에서 실행**

```bash
# 환경 설정 (최초 1회)
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"

# 전체 AUTO 섹션 업데이트
python update.py

# 특정 섹션만 업데이트
python update.py --section 풍향계
python update.py --section 주요뉴스
python update.py --section 여론동향
python update.py --section 공지사항

# 미리보기 (파일 저장 안 함)
python update.py --dry-run

# 업데이트 후 GitHub에 반영
git add index.html
git commit -m "수동 업데이트: $(date +'%Y-%m-%d')"
git push
```

---

## 수동 원고 수정 방법 (MANUAL 섹션)

`index.html`을 직접 열어서 마커 사이의 내용을 수정합니다.

### 편집자 레터 수정

```html
<!-- MANUAL:편집자레터:START -->
  <div class="editor-letter">
    ...여기를 수정...
  </div>
<!-- MANUAL:편집자레터:END -->
```

### 금요 칼럼 교체

```html
<!-- MANUAL:금요칼럼:START -->
  <div class="article">
    <div class="article-cat gold">이번 주 칼럼 | 날짜</div>
    <div class="article-title">칼럼 제목</div>
    <div class="article-body">
      <p>본문...</p>
    </div>
    <div class="article-meta">
      <span>필자 정보</span><span>날짜</span>
    </div>
  </div>
<!-- MANUAL:금요칼럼:END -->
```

수정 후:
```bash
git add index.html
git commit -m "금요칼럼 업데이트: 제목"
git push
```

---

## 게재 원칙

- **월요일**: 풍향계, 주요뉴스, 여론동향, 공지사항 (자동)
- **수요일**: 기획연재 (수동)
- **금요일**: 외부칼럼 (수동)
- **수시**: 편집자 레터 (수동)

---

## 문의

sokchonews@gmail.com | © 2026 속초시민뉴스
