# -*- coding: utf-8 -*-
import Colors
from selenium.webdriver.common.by import By
import time  # ✅ 여기에 time.sleep이 포함됨
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

main_url = "http://cafe.wisemobile.kr/manager/"
limit_lot_url = "http://cafe.wisemobile.kr/manager/adm/wz_booking_admin/check_parkingLot_count.php"
additional_url = "http://cafe.wisemobile.kr/manager/adm/wz_booking_admin/check_parkingLot_limit.php"

def do_limit_lot(driver):
    main_url = "http://cafe.wisemobile.kr/manager/"
    limit_lot_url = "http://cafe.wisemobile.kr/manager/adm/wz_booking_admin/check_parkingLot_count.php"
    additional_url = "http://cafe.wisemobile.kr/manager/adm/wz_booking_admin/check_parkingLot_limit.php"

    print("➡️ 관리자 페이지 접속 중...")
    try:
        driver.get(main_url)

        # ✅ 로그인 필드가 로딩될 때까지 최대 8초 대기
        try:
            WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.ID, "ol_id")))
            WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.ID, "ol_pw")))

            # 로그인 입력
            driver.find_element(By.ID, "ol_id").send_keys("admin")
            driver.find_element(By.ID, "ol_pw").send_keys("!@#park0413")
            driver.find_element(By.ID, "ol_submit").click()
            print(Colors.GREEN + "🟢 LimitLot 로그인 시도 완료" + Colors.ENDC)
        except TimeoutException:
            print(Colors.BLUE + "ℹ️ 이미 로그인되어 있거나 로그인 폼이 없습니다. 다음 단계를 계속 진행합니다." + Colors.ENDC)

    except Exception as e:
        print(Colors.RED + f"❌ 관리자 페이지 접속 중 오류 발생: {e}" + Colors.ENDC)
        return

    # 제한 수량 페이지 접근
    try:
        time.sleep(1.5)
        driver.get(limit_lot_url)
        print(Colors.GREEN + f"✅ limit_lot_url 이동 성공" + Colors.ENDC)
    except Exception as e:
        print(Colors.RED + f"❌ limit_lot_url 이동 실패: {e}" + Colors.ENDC)

    # 추가 URL 접근
    try:
        time.sleep(1.5)
        driver.get(additional_url)
        print(Colors.GREEN + f"✅ additional_url 이동 성공" + Colors.ENDC)
    except Exception as e:
        print(Colors.RED + f"❌ additional_url 이동 실패: {e}" + Colors.ENDC)

