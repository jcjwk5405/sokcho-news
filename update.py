#!/usr/bin/env python3
"""
속초시민뉴스 자동 업데이트 스크립트
- AUTO 마커 구간만 Claude API로 교체
- MANUAL 마커 구간은 절대 건드리지 않음

사용법:
  python update.py                  # 전체 AUTO 섹션 업데이트
  python update.py --section 풍향계  # 특정 섹션만 업데이트
  python update.py --dry-run        # 실제 파일 저장 없이 미리보기
"""

import os
import re
import sys
import json
import argparse
from datetime import datetime, timedelta
import anthropic

# ── 설정 ────────────────────────────────────────────────
HTML_FILE = "index.html"
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096

# 현재 날짜
today = datetime.now()
week_start = (today - timedelta(days=today.weekday())).strftime("%Y.%m.%d")
week_end = (today - timedelta(days=today.weekday()) + timedelta(days=4)).strftime("%Y.%m.%d")
today_str = today.strftime("%Y.%m.%d")

# ── Claude 클라이언트 ────────────────────────────────────
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def get_html_content():
    """index.html 읽기"""
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        return f.read()


def save_html_content(content):
    """index.html 저장"""
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ {HTML_FILE} 저장 완료")


def replace_section(html: str, section_name: str, new_content: str) -> str:
    """AUTO 마커 사이의 내용을 교체"""
    start_marker = f"<!-- AUTO:{section_name}:START -->"
    end_marker = f"<!-- AUTO:{section_name}:END -->"

    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL
    )

    if not pattern.search(html):
        print(f"⚠️  '{section_name}' 마커를 찾을 수 없습니다.")
        return html

    replacement = f"{start_marker}\n{new_content}\n    {end_marker}"
    new_html = pattern.sub(replacement, html)
    print(f"✅ '{section_name}' 섹션 교체 완료")
    return new_html


def call_claude(system_prompt: str, user_prompt: str) -> str:
    """Claude API 호출 - 웹 검색 포함"""
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        # 텍스트 블록만 추출
        result = ""
        for block in response.content:
            if block.type == "text":
                result += block.text
        return result.strip()
    except Exception as e:
        print(f"❌ Claude API 오류: {e}")
        return ""


# ── 시스템 프롬프트 (공통) ─────────────────────────────────
BASE_SYSTEM = """
당신은 속초시민뉴스의 AI 편집 보조입니다.
편집 원칙: 자유 민주주의 · 시장 자본주의 · 정의와 사랑
기사 원칙:
- 최대 1,000자를 넘지 않는다
- 사실에 근거하며, 다원적 관점을 존중한다
- 전문성과 노블레스 오블리주의 가치를 신뢰한다
- 개인의 자율의지와 선택의 자유를 최우선 존중한다

출력 규칙:
- 순수 HTML 코드만 출력한다 (```html 마크다운 없이)
- CSS 클래스는 반드시 기존 스타일시트의 것만 사용한다
- 아래 클래스들을 활용한다:
  article, article-cat, article-title, article-body, article-meta
  chart-wrap, chart-title, chart-source, week-info
  bar-item, bar-label-row, bar-pct, bar-track, bar-fill (navy/gold/red/green/blue/gray)
  donut-row, donut-item, donut-val (navy/red/gold/green/gray), donut-label
  paper-row, paper-name, paper-summary, paper-tag (con/pro/neutral)
  notice-item, n-title, n-meta, notice-badge (new 포함)
  data-table, highlight, positive
  opinion-block, opinion-attribution
"""


# ── 섹션별 생성 함수 ──────────────────────────────────────

def generate_ticker():
    """속보 티커 생성"""
    system = BASE_SYSTEM
    user = f"""
현재 날짜: {today_str}

웹 검색으로 이번 주 속초시 및 강원도 관련 뉴스를 찾아서
속보 티커용 <span> 태그 항목 10개를 만들어주세요.
(같은 내용을 2번 반복해서 총 10개 = 무한 스크롤 효과)

출력 형식 예시:
<span>속초시의회 예산심의 착수… 주요 안건 5건 상정</span>
<span>청초호 주변 공청회 5월 15일 예정</span>
...

조건:
- 각 항목은 30자 이내
- 실제 뉴스 기반으로 작성
- 속초 관련 뉴스 우선
"""
    return call_claude(system, user)


def generate_punghyang():
    """풍향계 - 5대 신문 사설 분석"""
    system = BASE_SYSTEM
    user = f"""
현재 날짜: {today_str}
분석 기간: {week_start} ~ {week_end}

웹 검색으로 이번 주 조선일보, 중앙일보, 동아일보, 한겨레, 경향신문의
주요 사설을 찾아 분석해주세요.

출력할 HTML 구조:
1. week-info 블록 (분석 기간, 분석 대상 편수)
2. article 블록 (주간 사설 분석 요약 - 핵심 의제 3가지)
3. chart-wrap - 신문별 주요 사설 논조 (paper-row 5개)
   - 각 신문의 보수/중도/진보 태그 포함
4. chart-wrap - 주간 핵심 의제 관심도 (bar-item 4~5개, 백분율)
5. article-meta (AI 자동 분석 | {today_str})
6. copy-btn 버튼과 숨겨진 복사 텍스트 div

모든 내용은 실제 검색 결과를 기반으로 작성하세요.
600자 이내를 지향합니다.
"""
    return call_claude(system, user)


def generate_news():
    """주요 뉴스 - 전국 및 속초"""
    system = BASE_SYSTEM
    user = f"""
현재 날짜: {today_str}

웹 검색으로 다음을 찾아주세요:
1. 이번 주 전국 주요 뉴스 3가지 (정치, 경제, 사회 각 1개)
2. 이번 주 속초시 주요 뉴스 3가지

출력할 HTML 구조:
1. article 블록 - 전국 주요 뉴스
   - article-cat: "전국 주요 뉴스"
   - article-title: "이번 주 전국: [핵심 키워드 3개]"
   - article-body: ①②③ 형식으로 각 뉴스 (총 600자 이내)
   - article-meta: "연합뉴스 수집 후 AI 편집 | {today_str}"

2. article 블록 - 속초 주요 뉴스  
   - article-cat red: "속초 주요 뉴스"
   - article-title: "이번 주 속초: [핵심 키워드 3개]"
   - article-body: ①②③ 형식 (600자 이내)
   - article-meta: "강원일보·강원도민일보 수집 후 AI 편집 | {today_str}"

3. chart-wrap - 속초 이슈 중요도 (bar-item 3~4개, ★ 별점)

실제 검색 결과 기반으로 작성하세요.
"""
    return call_claude(system, user)


def generate_opinion():
    """여론동향 - 갤럽, NBS 데이터"""
    system = BASE_SYSTEM
    user = f"""
현재 날짜: {today_str}

웹 검색으로 최신 한국갤럽 주간 정례조사(대통령 직무평가)와
NBS 여론조사 결과를 찾아주세요.

출력할 HTML 구조:
1. chart-wrap - 한국갤럽 대통령 직무수행 평가
   - donut-row: 긍정/부정/모름 3개 donut-item
   - 추이 설명 (텍스트)
   - chart-source (조사 방법, 날짜, 표본오차)

2. chart-wrap - NBS 또는 기타 최신 여론조사 결과
   (있으면 포함, 없으면 생략)

3. chart-wrap - 속초시장 후보 지지도
   (이레리서치 데이터 - 최신 데이터 없으면 기존 수치 유지)
   - bar-item 4개 (후보별)
   - chart-source

4. article-meta: "매주 월요일 업데이트 | 갤럽·NBS | {today_str}"

실제 검색된 수치를 사용하세요. 없으면 "현재 집계 중"으로 표시.
"""
    return call_claude(system, user)


def generate_notice():
    """공지사항 - 속초시청 공고"""
    system = BASE_SYSTEM
    user = f"""
현재 날짜: {today_str}
수집 기간: {week_start} ~ {week_end}

웹 검색으로 속초시청 홈페이지(sokcho.go.kr)의 최신 공고·공지사항을 찾아주세요.

출력할 HTML 구조:
1. week-info 블록 (수집 기간, 출처: 속초시청 홈페이지)

2. notice-item 4~6개
   - notice-badge: 신규/공고/입찰/모집/행사 중 적절한 것
   - n-title: 공지 제목
   - n-meta: 날짜, 장소, 담당부서

3. chart-wrap - 이번 주 발주 계약 현황 (data-table)
   - 사업명, 계약방식(수의계약은 highlight 클래스), 금액
   - chart-source에 수의계약 비율 표시

4. article-meta: "속초시청 홈페이지 수집 후 AI 편집 | {today_str}"

실제 검색 결과 기반으로 작성. 없으면 "이번 주 신규 공고 없음"으로 표시.
"""
    return call_claude(system, user)


# ── 섹션 매핑 ──────────────────────────────────────────
SECTIONS = {
    "TICKER": generate_ticker,
    "풍향계": generate_punghyang,
    "주요뉴스": generate_news,
    "여론동향": generate_opinion,
    "공지사항": generate_notice,
}


# ── 메인 ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="속초시민뉴스 자동 업데이트")
    parser.add_argument("--section", type=str, help="특정 섹션만 업데이트 (예: 풍향계)")
    parser.add_argument("--dry-run", action="store_true", help="파일 저장 없이 미리보기")
    args = parser.parse_args()

    # API 키 확인
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    print(f"\n🗞  속초시민뉴스 업데이트 시작 — {today_str}")
    print("=" * 50)

    html = get_html_content()

    # 업데이트할 섹션 결정
    sections_to_update = {}
    if args.section:
        if args.section in SECTIONS:
            sections_to_update[args.section] = SECTIONS[args.section]
        else:
            print(f"❌ 알 수 없는 섹션: {args.section}")
            print(f"   가능한 섹션: {', '.join(SECTIONS.keys())}")
            sys.exit(1)
    else:
        sections_to_update = SECTIONS

    # 섹션별 생성 및 교체
    for section_name, generator_fn in sections_to_update.items():
        print(f"\n📝 [{section_name}] 생성 중...")
        content = generator_fn()

        if content:
            if args.dry_run:
                print(f"--- {section_name} 미리보기 (첫 200자) ---")
                print(content[:200] + "...")
            else:
                html = replace_section(html, section_name, content)
        else:
            print(f"⚠️  [{section_name}] 내용 생성 실패, 기존 내용 유지")

    # 저장
    if not args.dry_run:
        save_html_content(html)
        print(f"\n🎉 업데이트 완료! — {today_str}")
    else:
        print("\n[dry-run] 파일을 저장하지 않았습니다.")


if __name__ == "__main__":
    main()
