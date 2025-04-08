from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
import time
import os


def get(max_retry=3):
    chrome_driver_path = './chromedriver.exe'

    for attempt in range(1, max_retry + 1):
        try:
            print(f"🚀 ChromeDriver 실행 시도 {attempt}/{max_retry}")

            options = webdriver.ChromeOptions()
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--allow-insecure-localhost")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-site-isolation-trials")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--remote-debugging-port=9222")
            # options.add_argument("--headless=new")

            # ✅ 403 우회 추가 설정
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # 기존 프로세스 종료
            os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
            os.system("taskkill /f /im chrome.exe >nul 2>&1")

            driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)

            # ✅ navigator.webdriver 숨기기
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