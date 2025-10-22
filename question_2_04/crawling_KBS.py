# crawling_naver_selenium.py
# Python 3.x / PEP 8 스타일 / 들여쓰기: 공백 2칸
# 필요 패키지: selenium (외부), webdriver는 로컬 설치 필요(예: ChromeDriver)
# 사용자가 직접 캡차/2단계 인증을 통과해야 함.

from time import sleep
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


LOGIN_URL = 'https://nid.naver.com/nidlogin.login?mode=form'
HOME_URL = 'https://www.naver.com/'
MAIL_URL = 'https://mail.naver.com/'


def prompt_credentials() -> tuple[str, str]:
  user_id = input('네이버 아이디 입력: ').strip()
  user_pw = input('네이버 비밀번호 입력: ').strip()
  return user_id, user_pw


def build_driver() -> webdriver.Chrome:
  options = Options()
  # 자동화 티를 줄이는 몇 가지 옵션 (절대적 효과는 아님)
  options.add_argument('--disable-blink-features=AutomationControlled')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')
  driver = webdriver.Chrome(options=options)
  driver.set_window_size(1280, 900)
  return driver


def login_naver(driver: webdriver.Chrome, user_id: str, user_pw: str) -> None:
  driver.get(LOGIN_URL)

  # 로그인 폼 대기 후 ID/PW 입력
  WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, 'id'))
  )
  id_input = driver.find_element(By.ID, 'id')
  pw_input = driver.find_element(By.ID, 'pw')

  id_input.clear()
  id_input.send_keys(user_id)
  pw_input.clear()
  pw_input.send_keys(user_pw)

  # 로그인 버튼 클릭
  login_btn = driver.find_element(By.CSS_SELECTOR, 'button.btn_login')
  login_btn.click()

  # 사용자가 캡차/2단계 인증을 통과하도록 대기
  print('필요 시 캡차/2단계 인증을 완료해 주세요.')
  input('인증이 끝났다면 Enter를 누르세요... ')

  # 홈 진입 확인
  driver.get(HOME_URL)
  WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.TAG_NAME, 'body'))
  )


def collect_login_state_signals(driver: webdriver.Chrome) -> dict:
  """
  로그인 전/후 차이를 신호 기반으로 수집.
  - 비로그인: "로그인" 버튼 존재
  - 로그인: 사용자 프로필/메일/알림 영역 존재 가능
  페이지 구조 변동 가능하므로, 다중 신호를 느슨히 체크.
  """
  html = driver.page_source

  signals = {
    'has_login_button_text': ('로그인' in html),
    'has_mail_word': ('메일' in html),
    'has_my_word': ('MY' in html or 'MY구독' in html),
  }

  # gnb(상단 우측) 사용자 메뉴 근사치 탐색 (구조 변동 가능)
  try:
    gnb_area = driver.find_elements(By.CSS_SELECTOR, '#gnb, #account, .gnb_inner, .header_inner')
    signals['has_gnb_area'] = bool(gnb_area)
  except Exception:
    signals['has_gnb_area'] = False

  return signals


def collect_mail_subjects(driver: webdriver.Chrome, limit: int = 10) -> List[str]:
  """
  네이버 메일 받은편지함에서 상단 일부 제목을 수집.
  - mail.naver.com은 SPA 요소가 많아 로딩 대기가 중요.
  - 셀렉터는 수시로 바뀔 수 있어, 텍스트 기반/유연 탐색을 혼용.
  """
  subjects: List[str] = []

  driver.get(MAIL_URL)
  WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.TAG_NAME, 'body'))
  )
  sleep(2)  # 초기 렌더링 여유

  # 후보 셀렉터 몇 가지 시도 (환경에 맞게 조정 필요)
  candidate_selectors = [
    # 예전/변형 UI에서의 제목 셀렉터 후보
    'div.mailList div.subject strong',
    'div.mailList div.subject',
    'div.subject strong.mail_title',
    'div.mailViewList .mail_title',
    'a.mail_subject',
    'div.MViewList span.title',
  ]

  found = []
  for sel in candidate_selectors:
    try:
      elems = driver.find_elements(By.CSS_SELECTOR, sel)
      if elems and len(found) < limit:
        for el in elems:
          text = el.text.strip()
          if text:
            found.append(text)
          if len(found) >= limit:
            break
      if len(found) >= limit:
        break
    except Exception:
      continue

  subjects = found[:limit]
  return subjects


def main() -> None:
  # 1) 로그인 전 신호 샘플링
  driver = build_driver()
  driver.get(HOME_URL)
  pre_signals = collect_login_state_signals(driver)

  # 2) 로그인
  user_id, user_pw = prompt_credentials()
  login_naver(driver, user_id, user_pw)

  # 3) 로그인 후 신호 샘플링
  post_signals = collect_login_state_signals(driver)

  # 4) 보너스: 메일 제목 수집
  mail_titles = collect_mail_subjects(driver, limit=10)

  driver.quit()

  # 5) 결과 리스트 출력
  # (과제 요구: "가져온 내용들을 리스트 객체에 담아 출력")
  contents: list = []
  contents.append('=== 로그인 전 신호 ===')
  contents.append(str(pre_signals))
  contents.append('=== 로그인 후 신호 ===')
  contents.append(str(post_signals))
  contents.append('=== 메일 제목 상위 10개(있다면) ===')
  contents.extend(mail_titles if mail_titles else ['(수집 실패 또는 메일 없음)'])

  for item in contents:
    print(item)


if __name__ == '__main__':
  main()
