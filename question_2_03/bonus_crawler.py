#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://weworkremotely.com"
URL = f"{BASE}/categories/remote-full-stack-programming-jobs"

HEADERS = {
  "User-Agent": (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
  )
}

def safe_text(node):
  return node.get_text(strip=True) if node else ""

def extract_jobs(limit=10):
  res = requests.get(URL, headers=HEADERS, timeout=10)
  res.raise_for_status()
  soup = BeautifulSoup(res.content, "html.parser")

  # 목록 li들을 넉넉히 집계 (광고/구분선 제외)
  items = soup.select("section.jobs li:not(.view-all)")[:limit]

  jobs = []
  for li in items:
    # 가장 확실한 a 태그 하나를 잡는다(로고 a 말고 본문 링크 a)
    a = li.select_one("a[href].preventLink, a[href].job-listing, a[href]")  # 폴백 순서
    href = urljoin(BASE, a["href"]) if a and a.has_attr("href") else ""

    # 타이틀 / 회사명 (여러 구조를 폴백으로 커버)
    title = (
      safe_text(li.select_one("h4.new-listing__header__title")) or
      safe_text(li.select_one("span.title")) or
      safe_text(li.select_one("h2, h3, h4"))
    )
    company = (
      safe_text(li.select_one("p.new-listing__company-name")) or
      safe_text(li.select_one("span.company")) or
      safe_text(li.select_one(".company, .company-name"))
    )

    # 링크가 로그인 필요 등으로 막히면 문구 처리
    if not href:
      href = "You need log-in"

    # 최소 정보가 있을 때만 append
    if title or company or href:
      jobs.append({
        "title": title,
        "company": company,
        "url": href
      })

  return jobs

def main():
  jobs = extract_jobs(limit=5)

  # 1) 리스트(dict) 그대로 출력
  print(jobs)

  # 2) 사람이 보기 좋게도 출력
  print("\nTop Jobs")
  print("-" * 60)
  for i, j in enumerate(jobs, 1):
    print(f"{i}. {j['title']}  |  {j['company']}")
    print(f"   {j['url']}")

if __name__ == "__main__":
  main()
