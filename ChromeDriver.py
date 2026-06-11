from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
import time
import os
import tempfile

# webdriver-manager: Chrome 버전에 맞는 ChromeDriver 자동 다운로드
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WDM_AVAILABLE = True
except ImportError:
    WDM_AVAILABLE = False


def _create_chrome_options():
    """Chrome 옵션 설정 (공통)"""
    options = webdriver.ChromeOptions()

    # ✅ 세션 저장 방지를 위한 임시 user-data-dir
    #temp_profile_dir = tempfile.mkdtemp()
    #options.add_argument(f"user-data-dir={temp_profile_dir}")

    options.add_argument("--guest")

    options.add_argument("--disable-features=AutofillServerCommunication,PasswordManagerEnabled,AutofillEnableAccountWalletStorage")
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--disable-web-security")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)

    return options


def _setup_driver(driver):
    """드라이버 초기 설정 (공통)"""
    # navigator.webdriver 숨김
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    driver.implicitly_wait(3)
    driver.maximize_window()


def get(max_retry=3):
    chrome_driver_path = './chromedriver.exe'

    # 기존 프로세스 종료
    os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
    os.system("taskkill /f /im chrome.exe >nul 2>&1")

    options = _create_chrome_options()

    for attempt in range(1, max_retry + 1):
        try:
            print(f"ChromeDriver 실행 시도 {attempt}/{max_retry}")

            # ── 1차: webdriver-manager로 자동 매칭 시도 ──
            if WDM_AVAILABLE:
                try:
                    driver_path = ChromeDriverManager().install()
                    print(f"✅ webdriver-manager가 ChromeDriver를 자동 설치했습니다: {driver_path}")
                    service = Service(driver_path)
                    driver = webdriver.Chrome(service=service, options=options)
                    _setup_driver(driver)
                    print("ChromeDriver 실행 성공 (자동 버전 매칭)")
                    return driver
                except Exception as wdm_err:
                    print(f"⚠️ webdriver-manager 자동 설치 실패, 로컬 chromedriver.exe로 폴백: {wdm_err}")

            # ── 2차: 로컬 chromedriver.exe 사용 (기존 방식) ──
            if os.path.exists(chrome_driver_path):
                print(f"로컬 ChromeDriver 사용: {chrome_driver_path}")
                service = Service(chrome_driver_path)
                driver = webdriver.Chrome(service=service, options=options)
                _setup_driver(driver)
                print("ChromeDriver 실행 성공 (로컬 chromedriver.exe)")
                return driver
            else:
                print(f"⚠️ 로컬 chromedriver.exe를 찾을 수 없습니다: {chrome_driver_path}")

        except (SessionNotCreatedException, WebDriverException) as e:
            print(f"ChromeDriver 실행 실패 (시도 {attempt}/{max_retry}): {e}")
            time.sleep(2)

    print("모든 ChromeDriver 실행 시도 실패")
    return None