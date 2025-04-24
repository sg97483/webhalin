from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
import time
import os
import tempfile


def get(max_retry=3):
    chrome_driver_path = './chromedriver.exe'

    for attempt in range(1, max_retry + 1):
        try:
            print(f"🚀 ChromeDriver 실행 시도 {attempt}/{max_retry}")

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

            # 기존 프로세스 종료
            os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
            os.system("taskkill /f /im chrome.exe >nul 2>&1")

            driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)

            # navigator.webdriver 숨김
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })

            driver.implicitly_wait(3)
            driver.maximize_window()
            print("✅ ChromeDriver 실행 성공")
            return driver

        except (SessionNotCreatedException, WebDriverException) as e:
            print(f"⚠️ ChromeDriver 실행 실패: {e}")
            time.sleep(2)

    print("❌ 모든 ChromeDriver 실행 시도 실패")
    return None