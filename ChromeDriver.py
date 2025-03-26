# ChromeDriver.py

from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
import time
import os


def get(max_retry=3):
    chrome_driver_path = './chromedriver.exe'

    for attempt in range(1, max_retry + 1):
        try:
            print(f"🚀 ChromeDriver 실행 시도 {attempt}/{max_retry}")

            # 크롬 옵션 설정
            options = webdriver.ChromeOptions()
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--allow-insecure-localhost")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-site-isolation-trials")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--remote-debugging-port=9222")  # DevToolsActivePort 오류 회피
            #options.add_argument("--headless=new")  # 필요 시 headless

            # 기존 chrome, chromedriver 종료 시도 (유령 프로세스 방지)
            os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
            os.system("taskkill /f /im chrome.exe >nul 2>&1")

            driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
            driver.implicitly_wait(3)
            driver.maximize_window()
            print("✅ ChromeDriver 실행 성공")
            return driver

        except (SessionNotCreatedException, WebDriverException) as e:
            print(f"⚠️ ChromeDriver 실행 실패: {e}")
            time.sleep(2)

    print("❌ 모든 ChromeDriver 실행 시도 실패")
    return None  # 호출부에서 None 체크해서 처리해야 함
