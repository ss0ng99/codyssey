#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawling_KBS.py
KBS(news.kbs.co.kr) 주요 헤드라인을 BeautifulSoup으로 수집하여 List에 저장하고 출력.

요구/제약 요약
- Python 3.x
- 외부 패키지: requests(허용), beautifulsoup4(과제 지시에 따라 사용)
- PEP 8, '작은따옴표', = 앞뒤 공백, 들여쓰기는 공백
- 함수명: snake_case, 클래스명: CapWords
"""

from __future__ import annotations

import sys
from typing import List, Set

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = 'https://news.kbs.co.kr/news/pc/main/main.html'
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
    ),
    'Accept-Language': 'ko,en;q=0.8',
}

def fetch_html(url: str) -> str:
    """URL에서 HTML을 가져온다."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        print(f'[오류] 요청 실패: {exc}', file=sys.stderr)
        return ''


def push_unique(titles: List[str], seen: Set[str], text: str) -> None:
    """중복/불필요 텍스트를 제외하고 리스트에 추가."""
    t = (text or '').strip()
    if not t or len(t) < 6:
        return
    if t in {'KBS', '뉴스', '홈', '로그인', '전체보기'}:
        return
    if t in seen:
        return
    seen.add(t)
    titles.append(t)


def extract_headlines(html: str, limit: int = 20) -> List[str]:
    """BeautifulSoup 주요 기능과 CSS 선택자로 헤드라인 텍스트를 수집."""
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')

    # 개발자 도구로 확인한(또는 추론 가능한) 대표 선택자들:
    # - 메인 헤드라인/섹션 타이틀 링크
    # - 기사 카드/리스트의 타이틀 앵커
    # - 기사 상세로 가는 공통 패턴(href에 /news/view.do 포함)
    selectors = [
        '.main-head-line a[href*="/view.do"]',
    ]

    titles: List[str] = []
    seen: Set[str] = set()

    for css in selectors:
        for a in soup.select(css):
            # 링크 텍스트 기반 추출
            text = a.get_text(strip=True)
            push_unique(titles, seen, text)
            if len(titles) >= limit:
                return titles

    # 기사 제목이 이미지에만 있고 텍스트가 빈 경우, title 속성/aria-label 폴백
    if len(titles) < 5:
        for a in soup.select('a[href*="/news/"]'):
            alt = a.get('title') or a.get('aria-label') or ''
            push_unique(titles, seen, alt)
            if len(titles) >= limit:
                break

    return titles[:limit]


def main() -> None:
    html = fetch_html(BASE_URL)
    headlines = extract_headlines(html, limit=20)

    print('KBS 헤드라인 뉴스 (상위 20개 내외)')
    print('-' * 40)
    if not headlines:
        print('수집된 헤드라인이 없습니다. (사이트 구조 변화 또는 접근 제한 가능)')
        return

    # 1) 과제 요구: "List 객체를 화면에 출력"
    print(headlines)

    # 2) 사람이 보기 좋은 포맷도 함께 출력
    print('\n정렬된 목록 출력:')
    for i, title in enumerate(headlines, start=1):
        print(f'{i:2d}. {title}')


if __name__ == '__main__':
    main()
