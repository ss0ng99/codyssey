from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import getpass

NAVER_HOME = 'https://www.naver.com'
NAVER_LOGIN = 'https://nid.naver.com/nidlogin.login'

def get_user_info() -> tuple[str, str]:
  user_id = input('ID 입력: ').strip()
  user_pw = getpass.getpass('PASSWORD 입력: ')
  return user_id, user_pw

def open_driver() -> webdriver.Chrome:
  options = webdriver.ChromeOptions()
  options.add_argument('--lang=ko-KR')
  # 필요 시 디버깅 유지: options.add_experimental_option('detach', True)
  return webdriver.Chrome(options=options)

def go_login_page(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
  driver.get(NAVER_HOME)
  try:
    # 메인 우상단 "로그인" 버튼 대기 후 클릭
    login_btn = wait.until(
      EC.element_to_be_clickable((By.XPATH, '//*[@id="account"]//a'))
    )
    login_btn.click()
  except TimeoutException:
    # 메인에서 버튼을 못 찾거나 클릭 실패 시 로그인 페이지로 바로 이동
    driver.get(NAVER_LOGIN)

def do_login(driver: webdriver.Chrome, wait: WebDriverWait, user_id: str, user_pw: str) -> None:
  try:
    id_input = wait.until(EC.presence_of_element_located((By.ID, 'id')))
    pw_input = wait.until(EC.presence_of_element_located((By.ID, 'pw')))
  except TimeoutException:
    # 혹시 아직 로그인 페이지가 아니라면 직접 이동 후 재시도
    driver.get(NAVER_LOGIN)
    id_input = wait.until(EC.presence_of_element_located((By.ID, 'id')))
    pw_input = wait.until(EC.presence_of_element_located((By.ID, 'pw')))

  id_input.clear()
  id_input.send_keys(user_id)
  pw_input.clear()
  pw_input.send_keys(user_pw + Keys.ENTER)

def get_main_title():
  mail_btn = '//*[@id="account"]/div[2]/div/div/ul/li[1]/a'
  mail_btn.click()

def main():
  user_id, user_pw = get_user_info()
  driver = open_driver()
  wait = WebDriverWait(driver, 10)

  go_login_page(driver, wait)
  do_login(driver, wait, user_id, user_pw)

  # TODO: 로그인 성공 여부를 간단히 체크하고 싶다면 아래처럼 존재하는 요소를 기다려볼 수 있어요.
  try:
    # '로그아웃' 등 로그인 후에만 보이는 요소가 나타날 때까지 대기
    WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'button.MyView-module__btn_logout___bsTOJ'))
    )
    print('로그인 성공')

    get_main_title()



  except TimeoutException:
    print('로그인 확인 실패(캡차/2단계 인증 또는 셀레니움 차단일 수 있음).')

if __name__ == '__main__':
  main()

