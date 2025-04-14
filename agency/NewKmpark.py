 # -*- coding: utf-8 -*-
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymysql
import Util
import Colors
from park import ParkUtil, ParkType
import WebInfo
import time

# DB 연결 정보
DB_CONFIG = {
    'host': '49.236.134.172',
    'port': 3306,
    'user': 'root',
    'password': '#orange8398@@',
    'db': 'parkingpark',
    'charset': 'utf8'
}

# 로그인 버튼 및 네비게이션 버튼 XPath
btn_confirm_xpath = "/html/body/mhp-console/div/div[2]/div/div/main/div[2]/div[1]/div[2]/div/div/div/div[2]/div[1]/div/div/div[2]/button[2]"
side_nav_xpath = "/html/body/div[3]/table/tbody/tr/td[2]/button"

# 대상 URL 리스트
TARGET_URLS = ["http://kmp0000798.iptime.org/","http://kmp0000601.iptime.org/","http://kmp0000483.iptime.org/"
    ,"http://kmp0000575.iptime.org/","http://kmp0000854.iptime.org/","http://kmp0000774.iptime.org/"
    ,"http://kmp0000089.iptime.org/","http://kmp0000403.iptime.org/","http://kmp0000131.iptime.org/"]

def get_park_ids_by_urls(target_urls):
    """
    DB에서 특정 URL 리스트와 매칭된 park_id를 가져옴.
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        curs = conn.cursor()
        format_strings = ','.join(['%s'] * len(target_urls))
        sql = f"SELECT parkId FROM T_PARKING_WEB WHERE url IN ({format_strings})"
        curs.execute(sql, target_urls)
        rows = curs.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"DB 쿼리 실패: {e}")
        return []
    finally:
        if conn:
            conn.close()

# DB에서 park_id 동적 조회
dynamic_park_ids = get_park_ids_by_urls(TARGET_URLS)


# 🚨 TARGET_URLS가 park_id 리스트로 바뀌었으면 원래 URL 리스트로 복구
if isinstance(TARGET_URLS, list) and all(isinstance(url, int) for url in TARGET_URLS):
    #print("🚨 DEBUG: TARGET_URLS가 park_id 리스트로 변경됨! 원래 URL 리스트로 복구")
    TARGET_URLS = ["http://kmp0000798.iptime.org/","http://kmp0000601.iptime.org/","http://kmp0000483.iptime.org/"
        ,"http://kmp0000575.iptime.org/","http://kmp0000854.iptime.org/","http://kmp0000774.iptime.org/"
        ,"http://kmp0000089.iptime.org/","http://kmp0000403.iptime.org/","http://kmp0000131.iptime.org/"]

# mapIdToWebInfo 동적 생성
mapIdToWebInfo = {park_id: ["form-login-username", "form-login-password", "//*[@id='form-login']/div[3]/button", "//*[@id='visit-lpn']", "//*[@id='btn-find']"]
                  for park_id in dynamic_park_ids}


def enter_user_id(driver, user_id):
    """
    로그인 페이지의 ID 입력 필드가 로드될 때까지 대기한 후 값을 입력
    """
    try:
        id_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='form-login-username']"))
        )
        driver.execute_script("arguments[0].removeAttribute('readonly')", id_field)
        driver.execute_script("arguments[0].removeAttribute('disabled')", id_field)
        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                              id_field, user_id)
        print(f"DEBUG: 아이디 '{user_id}' 입력 성공")

    except TimeoutException:
        print("ERROR: ID 입력 필드를 찾을 수 없음.")
    except Exception as e:
        print(f"ERROR: ID 입력 중 예외 발생: {e}")

def handle_alert(driver):
    """
    로그인 과정에서 Alert 창이 뜰 경우 자동으로 닫음.
    """
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"DEBUG: Alert 발견 - {alert.text}")
        alert.accept()
        print("DEBUG: Alert 닫기 완료")
    except TimeoutException:
        print("DEBUG: Alert이 감지되지 않음")

def close_vehicle_number_popup(driver):
    """
    차량번호 입력 후 뜨는 '2자리 이상 입력하세요' 팝업을 감지하고 자동으로 닫음.
    """
    try:
        popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "modal-window"))
        )
        print("DEBUG: 차량번호 입력 오류 팝업 감지됨.")

        # "OK" 버튼 클릭
        ok_button = popup.find_element(By.XPATH, ".//a[@class='modal-btn']")
        ok_button.click()
        print("DEBUG: '차량번호 2자리 이상 입력' 팝업 닫기 완료.")

        # 팝업이 완전히 사라질 때까지 대기
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element((By.ID, "modal-window"))
        )
        print("DEBUG: 팝업이 완전히 사라짐.")

    except TimeoutException:
        print("DEBUG: 차량번호 입력 팝업이 감지되지 않음.")  # 팝업이 없으면 문제없음.




def handle_no_search_results_popup(driver):
    """
    차량 검색 후 '검색 결과가 없습니다.' 팝업을 감지하고 OK 버튼을 클릭한 뒤 로그아웃.
    """
    try:
        popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-box"))
        )
        print("DEBUG: '검색 결과 없음' 팝업 감지됨.")

        # "OK" 버튼 클릭
        ok_button = popup.find_element(By.XPATH, ".//a[@class='modal-btn']")
        ok_button.click()
        print("DEBUG: '검색 결과 없음' 팝업 OK 버튼 클릭 완료.")

        # 팝업이 완전히 닫힐 때까지 대기
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element((By.CLASS_NAME, "modal-box"))
        )
        print("DEBUG: '검색 결과 없음' 팝업이 닫혔음.")

        # 🚀 로그아웃 버튼 클릭
        try:
            logout_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, side_nav_xpath))
            )
            logout_button.click()
            print("DEBUG: 로그아웃 버튼 클릭 완료.")
        except TimeoutException:
            print("ERROR: 로그아웃 버튼을 찾을 수 없음.")

        return False  # 🚀 검색 결과가 없으면 종료

    except TimeoutException:
        print("DEBUG: '검색 결과 없음' 팝업이 감지되지 않음.")
        return True  # 🚀 검색 성공했으면 할인 진행

def enter_car_number(driver, car_number_last4, park_id):
    """
    차량번호 뒤 4자리를 입력하고 '검색' 버튼 클릭.
    park_id에 따라 검색 버튼 다른 처리
    """
    try:
        close_vehicle_number_popup(driver)  # 차량번호 입력 전 팝업 닫기

        # 차량번호 입력 필드 찾기
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='visit-lpn']"))
        )

        input_field.clear()
        print("DEBUG: 차량번호 입력 필드 초기화 완료.")

        # 차량번호 입력
        input_field.send_keys(car_number_last4)
        print(f"DEBUG: 차량번호 '{car_number_last4}' 입력 완료.")

        # park_id별 검색 버튼 처리
        if park_id in [18938, 18577, 19906,19258,19239,19331]:  # 두 park_id 모두 class 기반
            # 18938 전용 검색 버튼
            search_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@class='btnS1_1 btn' and @value='검색']"))
            )
        else:
            # 기본 검색 버튼
            search_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='btn-find']"))
            )

        search_button.click()
        print("DEBUG: 차량번호 검색 버튼 클릭 완료.")

        # 🚀 "검색 결과가 없습니다." 팝업 확인 후 처리
        return handle_no_search_results_popup(driver)

    except TimeoutException as e:
        print(f"DEBUG: 차량번호 입력 중 TimeoutException 발생: {e}")
        return False


def handle_notice_popup_and_redirect(driver, park_id):
    """
    park_id == 29118 일 때 로그인 후 '안내' 팝업 닫고, 할인 페이지로 이동하는 함수
    """
    if park_id != 29118:
        return  # 다른 주차장은 처리하지 않음

    try:
        # 팝업 상위 div (modal-window) 감지
        popup_window = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "modal-window"))
        )
        print("DEBUG: '안내' 팝업 (modal-window) 감지됨.")

        # 내부 '닫기' 버튼 찾기
        close_button = popup_window.find_elements(By.CLASS_NAME, "modal-btn")[1]  # 두 번째 버튼이 '닫기'
        close_button.click()
        print("DEBUG: '안내' 팝업 닫기 버튼 클릭 완료.")

        # 팝업이 사라질 때까지 대기
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "modal-window"))
        )
        print("DEBUG: '안내' 팝업 사라짐.")

    except TimeoutException:
        print("DEBUG: '안내' 팝업이 감지되지 않음. 할인 페이지로 바로 이동 시도.")

    # 팝업 유무와 관계없이 할인 페이지 이동
    try:
        discount_url = "https://a18822.pweb.kr/discount/registration"
        driver.get(discount_url)
        print("DEBUG: 할인 페이지로 이동 완료.")

        # 할인 페이지 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='visit-lpn']"))
        )
        print("DEBUG: 할인 페이지 로딩 완료.")
    except TimeoutException:
        print("ERROR: 할인 페이지 로딩 실패.")


def process_ticket_and_logout(driver, button_id, park_id):
    """
    할인권 클릭 및 로그아웃까지 처리하는 함수
    """
    try:
        driver.find_element(By.ID, button_id).click()
        print(f"DEBUG: 할인권 버튼(id={button_id}) 클릭 완료.")
        WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
        print("DEBUG: 할인권 적용 확인 알림 닫기 완료.")
    except TimeoutException:
        print("DEBUG: 할인권 적용 알림 없음 (정상일 수 있음).")
    except Exception as e:
        print(f"ERROR: 할인권 클릭 중 예외 발생: {e}")

    # 팝업 처리
    try:
        popup = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-box"))
        )
        popup.find_element(By.XPATH, ".//a[@class='modal-btn']").click()
        WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CLASS_NAME, "modal-box")))
        print("DEBUG: 할인 이후 팝업 닫기 완료.")
    except TimeoutException:
        print("DEBUG: 할인 이후 팝업 감지되지 않음.")

    # 🚨 주차장에 따른 로그아웃 분기
    return logout(driver, park_id)


def enter_password_standard(driver, user_password):
    """
    로그인 페이지의 비밀번호 입력 필드가 로드될 때까지 대기한 후 값을 입력
    """
    try:
        pw_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='form-login-password']"))
        )
        driver.execute_script("arguments[0].removeAttribute('readonly')", pw_field)
        driver.execute_script("arguments[0].removeAttribute('disabled')", pw_field)
        driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));",
            pw_field, user_password
        )
        print(f"DEBUG: 비밀번호 입력 성공")
    except TimeoutException:
        print("ERROR: 비밀번호 입력 필드를 찾을 수 없음.")
    except Exception as e:
        print(f"ERROR: 비밀번호 입력 중 예외 발생: {e}")



def wait_and_click_discount_button(driver, button_id):
     """
     18938 전용 - 차량 검색 후 버튼 대기 후 클릭
     """
     try:
         print(f"DEBUG: 18938 전용 할인 버튼 대기 시작 (id={button_id})")

         # 최대 10초 대기 (버튼이 나타날 때까지)
         button = WebDriverWait(driver, 10).until(
             EC.element_to_be_clickable((By.ID, button_id))
         )
         print(f"DEBUG: 할인 버튼(id={button_id}) 활성화 확인")

         button.click()
         print(f"DEBUG: 할인 버튼(id={button_id}) 클릭 완료")
         return True

     except TimeoutException:
         print(f"ERROR: 할인 버튼(id={button_id})을 찾을 수 없음.")
         return False


def search_car_number_and_wait_discount(driver, car_number_last4, discount_button_id):
    """
    18938 전용: 차량번호 검색 후 할인권 버튼이 나타날 때까지 대기
    """
    try:
        close_vehicle_number_popup(driver)  # 팝업 닫기

        # 차량번호 입력 필드
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "schCarNo"))
        )
        input_field.clear()
        print("DEBUG: 차량번호 입력 필드 초기화 완료.")
        input_field.send_keys(car_number_last4)
        print(f"DEBUG: 차량번호 '{car_number_last4}' 입력 완료.")

        # 검색 버튼 클릭
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='sForm']/input[3]"))
        )
        search_button.click()
        print("DEBUG: 차량번호 검색 버튼 클릭 완료.")

        # "검색 결과가 없습니다." 팝업 감지
        if not handle_no_search_results_popup(driver):
            print("DEBUG: 차량 검색 결과 없음으로 종료.")
            return False

        # 🔑 할인권 버튼이 나타날 때까지 대기
        print(f"DEBUG: 할인권 버튼(id={discount_button_id}) 나타날 때까지 대기 중...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, discount_button_id))
        )
        print(f"DEBUG: 할인권 버튼(id={discount_button_id}) 감지 완료.")
        return True

    except Exception as e:
        print(f"ERROR: 차량 검색 또는 할인권 대기 중 오류: {e}")
        return False

def enter_memo_for_18577(driver):
    """
    18577 전용 - 메모란에 '파킹박' 입력
    """
    try:
        memo_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "memo"))
        )
        print("DEBUG: 메모 필드(memo) 감지됨.")

        # 값 설정
        memo_field.clear()
        memo_field.send_keys("파킹박")
        print("DEBUG: 메모 필드에 '파킹박' 입력 완료.")
        return True
    except TimeoutException:
        print("ERROR: 메모 필드(memo)를 찾을 수 없음.")
        return False


def select_car_in_table(driver, ori_car_num):
    """
    차량번호가 복수 검색되었을 때 <div id="page-view"> 안의 <tr>에서 전체 차량번호와 일치하는 항목을 클릭
    이후 할인권 목록 로딩까지 대기
    """
    try:
        rows = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#page-view tbody.gbox-body tr.gbox-body-row"))
        )

        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td.gbox-body-cell")
            if cells:
                found_car_num = cells[0].text.strip().replace(" ", "")
                print(f"DEBUG: 감지된 차량번호 → '{found_car_num}'")
                if found_car_num == ori_car_num.replace(" ", ""):
                    print(f"✅ 정확히 일치하는 차량번호 '{found_car_num}' 클릭 시도")
                    row.click()

                    # 🚨 클릭 후 할인권 로딩까지 잠시 대기
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody.gbox-body > tr.gbox-body-row"))
                        )
                        print("DEBUG: 할인권 리스트 로딩 확인 완료")
                    except TimeoutException:
                        print("WARNING: 차량 선택 후 할인권 리스트가 나타나지 않음")

                    return True

        print("❌ 일치하는 차량번호를 찾지 못했습니다.")
        return False

    except TimeoutException:
        print("❌ 차량 목록을 찾을 수 없습니다.")
        return False



def handle_ticket(driver, park_id, ticket_name, ori_car_num):
    """
    주차장 및 주차권에 따른 할인권 처리 (19081, 19610, 19588 포함)
    """
    print(f"DEBUG: 할인 처리 시작 (park_id={park_id}, ticket_name={ticket_name})")

    if park_id == 19463:
        print(f"DEBUG: 19463 전용 할인 처리 시작 (ticket_name={ticket_name})")
        if ticket_name == "평일1일권":
            try:
                ticket_xpath = '//*[@id="page-view"]/table/tbody/tr[5]/td/button'
                return click_discount_and_handle_popup(driver, ticket_xpath)
            except Exception as e:
                print(f"ERROR: 19463 - 할인 버튼 처리 중 예외 발생: {e}")
                return False
        else:
            print(f"ERROR: 19463에서 지원하지 않는 ticket_name: {ticket_name}")
            logout(driver)
            return False


    # ✅ 19081 전용 할인 처리
    if park_id == 19081:
        print(f"DEBUG: 19081 전용 할인 처리 시작 (ticket_name={ticket_name})")
        if ticket_name in ["평일1일권", "주말1일권"]:
            ticket_xpath = "//button[contains(text(), '24시간(무료)지하')]"
        elif ticket_name == "심야권":
            ticket_xpath = "//button[contains(text(), '12시간(무료)지하')]"
        else:
            print(f"ERROR: 19081에서 지원하지 않는 ticket_name: {ticket_name}")
            logout(driver)
            return False
        return click_discount_and_handle_popup(driver, ticket_xpath)


        # ✅ 19616 전용 할인 처리
    if park_id == 19616:
        print(f"DEBUG: 19616 전용 할인 처리 시작 (ticket_name={ticket_name})")
        if ticket_name in ["평일 1일권"]:
            ticket_xpath = "//button[contains(text(), '24시간(무료) [무제한]')]"
        elif ticket_name == "평일 3시간권":
            ticket_xpath = "//button[contains(text(), '3시간(무료) [무제한]')]"
        else:
            print(f"ERROR: 19616에서 지원하지 않는 ticket_name: {ticket_name}")
            logout(driver)
            return False
        return click_discount_and_handle_popup(driver, ticket_xpath)

    if park_id == 19019:
        print(f"DEBUG: 19019 전용 할인 처리 시작 (ticket_name={ticket_name})")
        if ticket_name == "평일1일권":
            ticket_xpath = '//*[@id="page-view"]/table/tbody/tr[5]/td/button'
            return click_discount_and_handle_popup(driver, ticket_xpath)
        else:
            print(f"ERROR: 19019에서 지원하지 않는 ticket_name: {ticket_name}")
            logout(driver)
            return False

    # ✅ 19457 전용 할인 처리
    if park_id == 19457:
        print(f"DEBUG: 19457 전용 할인 처리 시작 (ticket_name={ticket_name})")

        if ticket_name not in ["평일1일권", "주말1일권"]:
            print(f"ERROR: 19457에서 지원하지 않는 ticket_name: {ticket_name}")
            logout(driver)
            return False

        try:
            rows = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody.gbox-body > tr.gbox-body-row"))
            )

            success = False
            for row in rows:
                cells = row.find_elements(By.CLASS_NAME, "gbox-body-cell")
                if cells and "24시간할인" in cells[0].text:
                    print(f"DEBUG: 24시간할인 텍스트 확인됨: {cells[0].text}")
                    row.click()
                    print("DEBUG: 할인권 클릭 완료")

                    # 팝업 처리
                    try:
                        popup = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "modal-box"))
                        )
                        popup.find_element(By.XPATH, ".//a[@class='modal-btn']").click()
                        WebDriverWait(driver, 5).until(
                            EC.invisibility_of_element((By.CLASS_NAME, "modal-box"))
                        )
                        print("DEBUG: 팝업 닫기 완료")
                    except TimeoutException:
                        print("DEBUG: 팝업 감지되지 않음")

                    success = True
                    break

            logout(driver)

            if success:
                return True
            else:
                print("ERROR: 19457 - '24시간할인' 할인권을 찾지 못함")
                return False

        except TimeoutException:
            print("ERROR: 19457 - 할인권 목록 로딩 실패")
            logout(driver)
            return False

    # ✅ 19477 전용 할인 처리
    if park_id == 19477:
        try:
            # 차량 검색 결과가 복수인 경우 → 차량 선택 필요
            rows = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#page-view tbody.gbox-body tr.gbox-body-row"))
            )
            print(f"DEBUG: 차량 목록 {len(rows)}건 발견됨 → 차량 선택 시도")

            if not select_car_in_table(driver, ori_car_num):
                print("❌ 19477 - 차량 선택 실패, 로그아웃 후 종료")
                logout(driver)
                return False

            # 차량 클릭 후 할인권 페이지 로딩 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "btn-visit-coupon"))
            )
            print("DEBUG: 차량 선택 후 할인권 페이지 로딩 완료")

        except TimeoutException:
            # 차량 검색 결과가 1건이라 차량 선택 생략되는 경우
            print("DEBUG: 차량 검색 결과가 1건 → 차량 선택 생략하고 바로 할인 처리 진입")

        print(f"DEBUG: 19477 전용 할인 처리 시작 (ticket_name={ticket_name})")

        if ticket_name == "평일1일권":
            try:
                rows = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody.gbox-body > tr.gbox-body-row"))
                )
                print("DEBUG: 할인권 리스트 로딩 확인 완료")

                success = False
                for row in rows:
                    try:
                        button = row.find_element(By.TAG_NAME, "button")
                        raw_text = button.text.strip().replace(" ", "")
                        print(f"DEBUG: 버튼 내부 텍스트: '{raw_text}'")

                        if "24시간(무료)" in raw_text:
                            driver.execute_script("arguments[0].click();", button)
                            print("DEBUG: 할인 버튼 강제 클릭 완료")

                            # 팝업 처리 (있으면 처리, 없으면 패스)
                            try:
                                popup = WebDriverWait(driver, 3).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "modal-box"))
                                )
                                popup.find_element(By.XPATH, ".//a[@class='modal-btn']").click()
                                WebDriverWait(driver, 3).until(
                                    EC.invisibility_of_element((By.CLASS_NAME, "modal-box"))
                                )
                                print("DEBUG: 팝업 닫기 완료")
                            except TimeoutException:
                                print("WARNING: 팝업 감지되지 않음 → 무시하고 성공 처리")

                            success = True  # 팝업 없어도 성공으로 간주
                            break

                    except Exception as e:
                        print(f"WARNING: <button> 처리 중 예외 발생: {e}")

                logout(driver)

                if success:
                    return True
                else:
                    print("ERROR: 19477 - '24시간(무료)' 할인권을 찾지 못함")
                    return False

            except TimeoutException:
                print("ERROR: 19477 - 할인권 목록 로딩 실패")
                logout(driver)
                return False


        else:
            print(f"ERROR: 19477에서 지원하지 않는 ticket_name: {ticket_name}")
            logout(driver)
            return False

    # ✅ 19588 전용 할인 처리 (19477 방식과 동일)
    if park_id == 19588:
        print(f"DEBUG: 19588 전용 할인 처리 시작 (ticket_name={ticket_name})")
        cleaned_ticket_name = ticket_name.strip()

        if cleaned_ticket_name in ["평일1일권", "주말1일권"]:
            try:
                buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "btn-visit-coupon"))
                )
                print(f"DEBUG: 할인 버튼 {len(buttons)}개 발견됨")

                success = False
                for button in buttons:
                    try:
                        text = button.text.strip().replace("\n", "").replace(" ", "")
                        print(f"DEBUG: 버튼 텍스트 = '{text}'")

                        if "24시간(유료)" in text and "무제한" in text:
                            if button.is_enabled():
                                # 강제 클릭
                                driver.execute_script("arguments[0].click();", button)
                                print("DEBUG: 할인 버튼 강제 클릭 완료")

                                # 팝업 있으면 처리, 없으면 무시
                                try:
                                    popup = WebDriverWait(driver, 3).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, "modal-box"))
                                    )
                                    popup.find_element(By.XPATH, ".//a[@class='modal-btn']").click()
                                    WebDriverWait(driver, 3).until(
                                        EC.invisibility_of_element((By.CLASS_NAME, "modal-box"))
                                    )
                                    print("DEBUG: 팝업 닫기 완료")
                                except TimeoutException:
                                    print("WARNING: 팝업 감지되지 않음 → 무시하고 성공 처리")

                                success = True
                                break
                            else:
                                print("WARNING: 버튼 비활성화 상태입니다")
                    except Exception as e:
                        print(f"ERROR: 버튼 내부 처리 중 예외 발생: {e}")

                logout(driver)
                return success  # 팝업 없어도 success=True면 성공 반환

            except TimeoutException:
                print("ERROR: 할인 버튼 로딩 실패")
                logout(driver)
                return False
        else:
            print(f"ERROR: ticket_name '{cleaned_ticket_name}' 은 19588에서 지원되지 않음")
            logout(driver)
            return False

    # ✅ 19610 전용 할인 처리
    if park_id == 19610:
        print(f"DEBUG: 19610 전용 할인 처리 시작 (ticket_name={ticket_name})")
        if ticket_name in ["평일1일권", "주말1일권"]:
            ticket_xpath = '//*[@id="page-view"]/table/tbody/tr[6]/td/button'
        elif ticket_name == "심야권":
            ticket_xpath = '//*[@id="page-view"]/table/tbody/tr[5]/td/button'
        else:
            print(f"ERROR: 19610에서 지원하지 않는 ticket_name: {ticket_name}")
            logout(driver)
            return False
        return click_discount_and_handle_popup(driver, ticket_xpath)

        # ✅ 19588 전용 할인 처리 먼저!
    if park_id == 19588:
        print(f"DEBUG: 19588 전용 할인 처리 시작 (ticket_name={ticket_name})")
        cleaned_ticket_name = ticket_name.strip()

        if cleaned_ticket_name in ["평일1일권", "주말1일권"]:
            try:
                buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "btn-visit-coupon"))
                )
                print(f"DEBUG: 할인 버튼 {len(buttons)}개 발견됨")

                for button in buttons:
                    text = button.text.strip().replace("\n", "").replace(" ", "")
                    print(f"DEBUG: 버튼 텍스트 = '{text}'")
                    if "24시간(유료)" in text and "무제한" in text:
                        if button.is_enabled():
                            button.click()
                            print("DEBUG: 할인 버튼 클릭 완료")

                            # 팝업 처리
                            try:
                                popup = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "modal-box"))
                                )
                                popup.find_element(By.XPATH, ".//a[@class='modal-btn']").click()
                                WebDriverWait(driver, 5).until(
                                    EC.invisibility_of_element((By.CLASS_NAME, "modal-box"))
                                )
                                print("DEBUG: 팝업 닫기 완료")
                            except TimeoutException:
                                print("DEBUG: 팝업 감지되지 않음")

                            return logout(driver)
                        else:
                            print("WARNING: 버튼 비활성화 상태입니다")
                print("ERROR: 원하는 할인권 버튼을 찾지 못함")
                logout(driver)
                return False

            except TimeoutException:
                print("ERROR: 할인 버튼 로딩 실패")
                logout(driver)  # ✅ 로그아웃 추가
                return False
        else:
            print(f"ERROR: ticket_name '{cleaned_ticket_name}' 은 19588에서 지원되지 않음")
            logout(driver)  # ✅ 로그아웃 추가
            return False


    # ✅ 기타 주차장 할인 처리 (버튼 ID 기반)
    ticket_map = {
        19892: {"평일 심야권": "15", "주말 심야권": "15", "휴일 당일권": "8"},
        19489: {"평일1일권": "8", "주말1일권": "10", "평일 심야권": "9"},
        19130: {"평일1일권": "14", "평일 심야권": "15"},
    }

    if park_id not in ticket_map or ticket_name not in ticket_map[park_id]:
        print(f"ERROR: No matching ticket found for park_id={park_id}, ticket_name={ticket_name}")
        return False

    button_id = ticket_map[park_id][ticket_name]
    return process_ticket_and_logout(driver, button_id, park_id)


def click_discount_and_handle_popup(driver, ticket_xpath):
    """
    XPath로 할인 버튼 클릭 후 팝업 처리, 로그아웃까지 일괄 수행
    """
    # 할인 버튼 클릭
    try:
        discount_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, ticket_xpath))
        )
        discount_button.click()
        print(f"DEBUG: 할인 버튼 클릭 완료 (XPath: {ticket_xpath})")
    except TimeoutException:
        print(f"ERROR: 할인 버튼을 찾을 수 없음 (XPath: {ticket_xpath})")
        return False

    # 할인 후 팝업 처리
    try:
        popup = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-box"))
        )
        popup.find_element(By.XPATH, ".//a[@class='modal-btn']").click()
        WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CLASS_NAME, "modal-box")))
        print("DEBUG: 할인 이후 팝업 닫기 완료.")
    except TimeoutException:
        print("DEBUG: 할인 이후 팝업 감지되지 않음.")  # 팝업 없을 수도 있음

    # ✅ 로그아웃 수행
    return logout(driver)



def logout(driver):
    """
    통합 로그아웃 처리 (모든 주차장 공통, 19610 포함 - MENU 버튼 포함 + Alert 처리)
    """
    try:
        # 메뉴 열기
        menu_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='btn-mobile-menu']"))
        )
        menu_button.click()
        print("DEBUG: MENU 버튼 클릭 완료. 로그아웃 메뉴 열림 확인.")

        # 로그아웃 버튼 대기 및 클릭
        logout_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn-logout"))
        )
        logout_button.click()
        print("DEBUG: 로그아웃 버튼 클릭 완료.")

        # ✅ 로그아웃 Alert 처리
        try:
            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
            print(f"DEBUG: 로그아웃 Alert 감지됨: {alert.text}")
            alert.accept()  # Alert 닫기
            print("DEBUG: 로그아웃 Alert 닫기 완료.")
        except TimeoutException:
            print("DEBUG: 로그아웃 Alert 감지되지 않음. (정상일 수 있음)")

        return True

    except TimeoutException:
        print("ERROR: 로그아웃 또는 메뉴 버튼을 찾을 수 없음.")
        return False




def web_har_in(target, driver):
    """
    주차권 할인을 처리하는 메인 함수
    """
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]

    if ParkUtil.is_park_in(park_id) and park_id in mapIdToWebInfo:
        login_url = ParkUtil.get_park_url(park_id)
        driver.get(login_url)

        web_har_in_info = ParkUtil.get_park_lot_option(park_id)
        user_id = web_har_in_info[WebInfo.webHarInId]
        user_password = web_har_in_info[WebInfo.webHarInPw]

        try:
            # ✅ 사전 로그인 상태 확인
            current_url = driver.current_url
            if ParkUtil.first_access(park_id, current_url):
                enter_user_id(driver, user_id)
                enter_password_standard(driver, user_password)

                print("로그인 버튼 클릭 전 3초 대기...")
                time.sleep(3)

                login_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='form-login']/div[3]/button"))
                )
                login_button.click()
                print("로그인 버튼 클릭 완료!")

                handle_alert(driver)
            else:
                print("DEBUG: 이미 로그인된 상태로 판단됨 → 로그인 생략")

            # ✅ 29118인 경우 팝업 처리 및 할인 페이지 이동
            handle_notice_popup_and_redirect(driver, park_id)

            close_vehicle_number_popup(driver)

            driver.car_number_last4 = ori_car_num[-4:]

            # ✅ 차량번호 검색 수행 후 실패 시 로그아웃 처리
            car_number_result = enter_car_number(driver, ori_car_num[-4:], park_id)

            if not car_number_result:
                print("DEBUG: 차량번호 검색 실패 또는 검색 결과 없음 → 로그아웃 후 종료")
                try:
                    logout_success = logout(driver)
                    if not logout_success:
                        # 로그아웃 실패했을 경우 강제로 로그인 페이지 재접근 시도
                        driver.get(ParkUtil.get_park_url(park_id))
                        print("DEBUG: 로그아웃 실패 시 강제로 로그인 페이지 재접근 시도")
                except Exception as e:
                    print(f"WARNING: 로그아웃 처리 중 예외 발생: {e}")
                    try:
                        driver.get(ParkUtil.get_park_url(park_id))
                        print("DEBUG: 예외 발생 시 강제로 로그인 페이지 재접근 시도")
                    except:
                        pass
                return False

            # 검색 성공 시 할인권 처리
            return handle_ticket(driver, park_id, ticket_name, ori_car_num)

        except NoSuchElementException as ex:
            print(f"할인 처리 중 오류 발생: {ex}")
            return False

    return False
