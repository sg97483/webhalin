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

# DB 연결 정보
DB_CONFIG = {
    'host': '49.236.134.172',
    'port': 3306,
    'user': 'root',
    'password': '#orange8398@@',
    'db': 'parkingpark',
    'charset': 'utf8'
}

# 동일한 정보로 통합된 mapIdToWebInfo
DEFAULT_WEB_INFO = ["mf_wfm_body_ibx_empCd", "mf_wfm_body_sct_password", "mf_wfm_body_btn_login",
                    "mf_wfm_body_carNo", "mf_wfm_body_mobileOkBtn"]

# 대상 URL 리스트
TARGET_URLS = [
    "https://npdc-i.nicepark.co.kr/",
    "https://npdc-i.nicepark.co.kr",
    "http://npdc-i.nicepark.co.kr/",
    "http://npdc-i.nicepark.co.kr",
    "https://npdc.nicepark.co.kr/npdc/login",
    "http://npdc.nicepark.co.kr"
]

def get_park_ids_by_urls(target_urls):
    """
    DB에서 특정 URL 리스트와 매칭된 park_id를 가져옵니다.
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        curs = conn.cursor()
        # SQL 쿼리 실행
        format_strings = ','.join(['%s'] * len(target_urls))
        sql = f"SELECT parkId FROM T_PARKING_WEB WHERE url IN ({format_strings})"
        curs.execute(sql, target_urls)
        rows = curs.fetchall()
        return [row[0] for row in rows]  # park_id 리스트로 반환
    except Exception as e:
        print(f"DB 쿼리 실패: {e}")
        return []
    finally:
        if conn:
            conn.close()

# DB에서 park_id 동적 조회
dynamic_park_ids = get_park_ids_by_urls(TARGET_URLS)

# mapIdToWebInfo 동적 생성
mapIdToWebInfo = {
    park_id: DEFAULT_WEB_INFO
    for park_id in dynamic_park_ids
}

btn_confirm_xpath = "/html/body/mhp-console/div/div[2]/div/div/main/div[2]/div[1]/div[2]/div/div/div/div[2]/div[1]/div/div/div[2]/button[2]"
side_nav_xpath = "mf_wfm_header_btn_logout"


def find_emp_cd_field(driver, user_id, user_password):
    """
    ID와 비밀번호 입력 필드 처리 (강제 입력 방식 추가)
    """
    try:
        id_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mf_wfm_body_ibx_empCd"))
        )
        pw_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mf_wfm_body_sct_password"))
        )

        # 기존 방식으로 입력 시도
        id_field.clear()
        id_field.send_keys(user_id)
        pw_field.clear()
        pw_field.send_keys(user_password)

        print(f"DEBUG: send_keys로 입력 시도 완료. (아이디: {user_id})")

        # 강제 방식으로 재확인
        force_input(driver, "mf_wfm_body_ibx_empCd", user_id)
        force_input(driver, "mf_wfm_body_sct_password", user_password)
        print(f"DEBUG: 강제 입력 완료. (아이디: {user_id})")

        # 입력 후 잠깐 대기
        time.sleep(1)

    except TimeoutException:
        print("DEBUG: 아이디/비밀번호 필드 찾기 실패.")

def force_input(driver, element_id, value):
    """
    JavaScript로 값 강제 설정 및 이벤트 트리거
    """
    script = """
    var input = document.getElementById(arguments[0]);
    if (input) {
        input.focus();
        input.value = arguments[1];
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'a' }));
        input.dispatchEvent(new KeyboardEvent('keypress', { bubbles: true, key: 'a' }));
        input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: 'a' }));
        input.blur();
    }
    """
    driver.execute_script(script, element_id, value)


def set_input_value_with_events(driver, element, value):
    driver.execute_script("""
        var element = arguments[0];
        var value = arguments[1];
        element.focus();
        element.value = value;
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        element.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'a' }));
        element.dispatchEvent(new KeyboardEvent('keypress', { bubbles: true, key: 'a' }));
        element.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: 'a' }));
        element.blur();
    """, element, value)


def handle_password_reset_popup(driver, timeout=3):
    """
    비밀번호 초기화 팝업 발생 시 '아니오' 클릭 처리 (timeout 초 이내 대기)
    """
    try:
        popup = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "mf_wfm_body_ui_initPwdPop_contents"))
        )
        print("DEBUG: 비밀번호 초기화 팝업 감지됨.")

        cancel_button = popup.find_element(By.ID, "mf_wfm_body_btn_cancel")
        driver.execute_script("arguments[0].click();", cancel_button)
        print("DEBUG: 비밀번호 초기화 팝업 '아니오' 버튼 클릭 완료.")

        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.ID, "mf_wfm_body_ui_initPwdPop_contents"))
        )
        print("DEBUG: 비밀번호 초기화 팝업 닫힘 확인 완료.")

    except TimeoutException:
        print("DEBUG: 비밀번호 초기화 팝업이 감지되지 않음. (정상일 수 있음)")




def handle_invalid_ticket(driver):
    """
    유효하지 않은 ticket_name을 처리하는 공통 함수.
    """
    try:
        driver.implicitly_wait(3)
        driver.find_element_by_xpath(side_nav_xpath).click()
        print(Colors.BLUE + "유효하지않은 ticket_name입니다. " + Colors.ENDC)
    except Exception as ex:
        print(f"Error during process: {ex}")
    return False


def handle_popup(driver):
    """
    로그인 후 나타나는 팝업을 처리하는 함수.
    """
    try:
        # 첫 번째 팝업의 "확인" 버튼 처리
        confirm_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@value='확인' and @type='button']"))
        )
        confirm_button.click()
        print("첫 번째 팝업이 닫혔습니다.")

        # 두 번째 팝업의 "나중에 변경하기" 버튼 처리
        cancel_change_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mf_wfm_body_DCWD009P01_wframe_btn_cancelChg"))
        )
        cancel_change_button.click()
        print("비밀번호 변경 팝업에서 '나중에 변경하기' 버튼이 클릭되었습니다.")

    except TimeoutException:
        print("팝업이 나타나지 않았거나 처리 중 오류가 발생했습니다.")


def handle_init_password_popup(driver, timeout=3):
    try:
        popup = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "w2popup_window"))
        )
        print("DEBUG: 알림 또는 비밀번호 초기화 팝업 감지됨.")

        try:
            confirm_button = popup.find_element(By.XPATH, ".//input[@value='확인']")
            driver.execute_script("arguments[0].click();", confirm_button)
            print("DEBUG: 팝업 '확인' 버튼 JS로 강제 클릭 완료.")

            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "w2popup_window"))
            )
            print("DEBUG: 팝업 닫힘 완료.")
        except NoSuchElementException:
            print("DEBUG: 팝업에는 '확인' 버튼이 없음 (무시하고 진행).")
    except TimeoutException:
        print("DEBUG: '알림/비밀번호 초기화' 팝업이 감지되지 않음 (정상일 수 있음).")





def handle_password_change_popup(driver, timeout=3):
    try:
        popup = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "mf_wfm_body_DCWD009P01"))
        )
        print("DEBUG: '비밀번호 변경' 팝업 감지됨.")

        later_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "mf_wfm_body_DCWD009P01_wframe_btn_cancelChg"))
        )
        later_button.click()
        print("DEBUG: '비밀번호 변경' 팝업 '나중에 변경하기' 클릭 완료.")

        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.ID, "mf_wfm_body_DCWD009P01"))
        )
        print("DEBUG: '비밀번호 변경' 팝업 닫힘 확인 완료.")
    except TimeoutException:
        print("DEBUG: '비밀번호 변경' 팝업이 감지되지 않음 (정상일 수 있음).")




def select_discount_and_confirm(driver, radio_xpath):
    """
    주차권 선택 버튼 클릭 및 로그아웃 처리 함수 (재탐색 포함)
    """
    try:
        # 🚨 할인 버튼이 새로 뜰 때까지 대기 (화면 새로고침/변화 고려)
        print("할인 버튼 로드 대기 중...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, radio_xpath))
        )
        print("할인 버튼 감지됨. 클릭 시도.")

        # 재탐색 후 클릭
        discount_button = driver.find_element(By.XPATH, radio_xpath)
        discount_button.click()
        print(Colors.BLUE + "할인 처리 완료" + Colors.ENDC)

        # 할인권 클릭 이후
        driver.execute_script("document.getElementById('___processbar2').style.display='none';")
        print("DEBUG: 로딩 모달 강제로 숨김.")

        # _modal 대기
        try:
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.ID, "_modal"))
            )
            print("DEBUG: _modal 사라짐 감지 완료.")
        except TimeoutException:
            print("DEBUG: _modal이 사라지지 않음. 강제 숨김 시도.")
            driver.execute_script("document.getElementById('_modal').style.display='none';")
            print("DEBUG: _modal 강제 숨김 완료.")

        # 로그아웃 버튼 클릭 전 대기
        print("로그아웃 버튼 클릭 전 대기 중...")
        logout_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "mf_wfm_header_btn_logout"))  # 로그아웃 버튼 ID
        )
        logout_button.click()
        print("로그아웃 완료!")
        return True

    except TimeoutException:
        print("로그아웃 버튼 또는 할인 버튼을 찾을 수 없습니다. DOM 구조를 다시 확인하세요.")
        return False

    except NoSuchElementException as ex:
        print(f"할인 처리 중 요소를 찾을 수 없음: {ex}")
        return False

    except Exception as ex:
        print(f"할인 처리 중 오류 발생: {ex}")
        return False






import time

def enter_car_number(driver, car_number_last4):
    """
    차량번호 뒤 4자리를 키패드로 입력하고 'OK' 버튼 클릭.
    """
    try:
        # 🚨 키패드가 뜰 때까지 대기 (확인용으로 상단의 고유 div 사용)
        WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.ID, "mf_wfm_body_wq_uuid_133"))
        )
        print("DEBUG: 차량번호 키패드 감지됨.")

        # 차량번호 숫자 키패드 버튼 클릭
        for digit in car_number_last4:
            button_xpath = f"//input[@value='{digit}' and contains(@class, 'carNumBtn')]"
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            button.click()
            print(f"DEBUG: 숫자 {digit} 입력 완료.")

        # OK 버튼 클릭
        ok_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='OK' and @type='button']"))
        )
        ok_button.click()
        print("DEBUG: 'OK' 버튼 클릭 완료.")

        # 🚨 화면 안정화를 위한 짧은 대기 (2~3초)
        time.sleep(1)  # 또는 필요한 경우 WebDriverWait로 특정 요소 기다리기
        print("DEBUG: 차량번호 처리 이후 화면 안정화 대기 완료.")

    except TimeoutException as e:
        print(f"DEBUG: 차량번호 키패드 입력 중 TimeoutException 발생: {e}")

    except Exception as e:
        print(f"DEBUG: 차량번호 키패드 입력 중 예상치 못한 오류 발생: {e}")




def handle_login_alert_popup(driver):
    """
    로그인 직후 나타나는 알림 팝업에서 '확인' 버튼을 클릭하는 함수.
    """
    try:
        # 알림 팝업 감지 및 '확인' 버튼 대기
        confirm_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@value='확인' and contains(@class, 'w2trigger')]"))
        )
        confirm_button.click()
        print("DEBUG: 로그인 후 알림 팝업 '확인' 버튼 클릭 완료.")
    except TimeoutException:
        print("DEBUG: 로그인 알림 팝업이 감지되지 않음. (정상일 수도 있음)")


def handle_notice_popup(driver, timeout=3):
    try:
        close_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@type='button' and @value='닫기' and contains(@id, '_wframe_btn_close')]")
            )
        )
        driver.execute_script("arguments[0].click();", close_button)
        print("DEBUG: 공지사항 팝업 닫기 버튼 클릭 완료.")
    except TimeoutException:
        print("DEBUG: 공지사항 팝업이 감지되지 않음. (정상일 수 있음)")



def handle_search_error_popup(driver):
    """
    차량번호 검색 실패 후 나타나는 팝업을 처리하고, 로그아웃 버튼 클릭.
    """
    try:
        # 팝업을 감지하는 공통 클래스 기반
        popup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "w2popup_window"))  # 공통 클래스 사용
        )
        print("DEBUG: 팝업이 감지되었습니다.")

        # 팝업 '확인' 버튼 처리
        confirm_button = popup.find_element(By.XPATH, ".//input[@value='확인']")
        confirm_button.click()
        print("DEBUG: 팝업의 '확인' 버튼이 클릭되었습니다.")

        # 팝업이 닫힐 때까지 대기
        WebDriverWait(driver, 5).until_not(
            EC.presence_of_element_located((By.CLASS_NAME, "w2popup_window"))
        )
        print("DEBUG: 팝업이 닫혔습니다.")

        # 로그아웃 버튼 클릭
        try:
            logout_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "mf_wfm_header_btn_logout"))  # 로그아웃 버튼 ID
            )
            logout_button.click()
            print("DEBUG: 로그아웃 버튼이 클릭되었습니다.")
        except NoSuchElementException:
            print("DEBUG: 로그아웃 버튼을 찾을 수 없습니다. DOM 구조를 확인하세요.")
            raise

        # 로그아웃 후 다음 동작으로 이동
        return True

    except TimeoutException as te:
        print(f"DEBUG: 팝업 처리 중 TimeoutException 발생: {te}")
        return False
    except Exception as ex:
        print(f"DEBUG: 팝업 또는 로그아웃 처리 중 예외 발생: {ex}")
        return False

def check_search_failed_and_logout(driver):
    """
    차량번호 검색 실패 시 나타나는 팝업 감지 후 '확인' 클릭 및 로그아웃 처리.
    실패 시 False 반환.
    """
    print("DEBUG: check_search_failed_and_logout() 함수 진입 시도")
    try:
        # 차량 검색 실패 팝업 감지
        popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "w2popup_window"))
        )
        print("DEBUG: 차량번호 검색 실패 팝업 감지됨.")

        # '확인' 버튼 클릭
        confirm_button = popup.find_element(By.XPATH, ".//input[@type='button' and @value='확인']")
        driver.execute_script("arguments[0].click();", confirm_button)
        print("DEBUG: 팝업 '확인' 버튼 클릭 완료.")

        # 팝업 닫힘 대기
        try:
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "w2popup_window"))
            )
            print("DEBUG: 검색 실패 팝업 닫힘 완료.")
        except TimeoutException:
            print("DEBUG: 팝업 닫힘 대기 실패 → 강제 로그아웃 시도 진행.")

        # 로그아웃 시도 (모달 가림 방지 포함)
        try:
            driver.execute_script(
                "var modal = document.getElementById('_modal'); if(modal) modal.style.display='none';"
            )
            logout_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "mf_wfm_header_btn_logout"))
            )
            logout_button.click()
            print(Colors.YELLOW + "DEBUG: 차량 검색 실패 후 로그아웃 성공 (False 반환)" + Colors.ENDC)
        except Exception as logout_ex:
            print(f"DEBUG: 로그아웃 버튼 클릭 실패: {logout_ex}")

        return False

    except TimeoutException:
        print("DEBUG: 차량 검색 실패 팝업이 감지되지 않음. (정상일 수 있음)")
        return True  # 팝업이 없으면 정상 진행

    except Exception as ex:
        print(f"DEBUG: check_search_failed_and_logout() 예외 발생: {ex}")
        return False


def handle_all_optional_popups(driver, park_id):
    """
    주차장에 따라 필요한 팝업만 선택적으로 처리하며, 각 팝업 대기 시간을 최소화함.
    """
    try:
        if park_id in [19768, 19398, 19208, 19973]:  # 실제로 비밀번호 초기화 팝업 뜨는 park_id
            handle_password_reset_popup(driver, timeout=2)
            handle_init_password_popup(driver, timeout=2)
            handle_password_change_popup(driver, timeout=2)

        if park_id in [19768, 19796, 19399]:  # 공지사항 팝업 뜨는 park_id
            handle_notice_popup(driver, timeout=2)

        # 공통 처리 (팝업 없을 가능성 높음)
        handle_popup(driver, timeout=2)

    except Exception as e:
        print(f"DEBUG: 선택 팝업 처리 중 예외 발생: {e}")



def web_har_in(target, driver):
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

            find_emp_cd_field(driver, user_id, user_password)

            print("로그인 버튼 클릭 전 3초 대기...")
            time.sleep(3)

            login_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "mf_wfm_body_btn_login"))
            )
            login_button.click()

            print("로그인 성공!")

            # 최적화된 팝업 처리
            handle_all_optional_popups(driver, park_id)

            # 비밀번호 초기화 팝업 감지 시 '아니오' 처리
            handle_password_reset_popup(driver)

            # 비밀번호 초기화 팝업 처리
            handle_init_password_popup(driver)

            # 로그인 알림 팝업 처리
            handle_login_alert_popup(driver)

            handle_password_change_popup(driver)

            # 🔽 여기서 호출
            handle_notice_popup(driver)

            # 팝업 처리
            handle_popup(driver)

            # 차량번호 뒤 4자리 추출
            car_number_last4 = ori_car_num[-4:]  # 차량번호 뒤 4자리
            print(f"입력할 차량번호 마지막 4자리: {car_number_last4}")

            # 차량번호 입력
            enter_car_number(driver, car_number_last4)

            # 차량 검색 실패 팝업 감지 → 로그아웃 → 실패 처리
            print("DEBUG: check_search_failed_and_logout() 함수 진입 시도")  # <-- 이 줄을 추가
            if not check_search_failed_and_logout(driver):
                print("DEBUG: check_search_failed_and_logout() 함수에서 False 반환됨 → 종료")  # Optional
                return False

        except TimeoutException as e:
            print(f"로그인 과정에서 문제가 발생했습니다: {e}")
            return False

        # park_id 및 ticket_name에 따른 처리
        if park_id == 19742:
            if ticket_name == "3시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "1일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "연박2일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name == "연박3일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_3_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19768:
            if ticket_name in ["평일1일권", "주말1일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19208:
            if ticket_name in ["평일1일권", "주말1일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_4_discountTkGrp']"
                )
            elif ticket_name == "2시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "4시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "8시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name == "심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_3_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19280:
            if ticket_name == "평일1일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "평일 심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19338:
            if ticket_name == "평일1일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_5_discountTkGrp']"
                )
            elif ticket_name == "주말1일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_5_discountTkGrp']"
                )
            elif ticket_name == "2시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "4시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "8시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name == "심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_3_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19539:
            if ticket_name in ["평일1일권", "주말1일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name in ["평일 3시간권", "주말 3시간권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name in ["심야권(일~목)", "심야권(금~토)"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19973:
            if ticket_name in ["평일 당일권", "휴일 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_4_discountTkGrp']"
                )
            elif ticket_name == "저녁권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_3_discountTkGrp']"
                )
            elif ticket_name == "5시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "3시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19288:
            if ticket_name == "평일1일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "평일 심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19330:
            if ticket_name == "주말1일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "심야권(일~목)":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19971:
            if ticket_name in ["평일 당일권", "휴일 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name in ["심야권(일~목)", "심야권(금~토)"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19400:
            if ticket_name == "평일 1일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name == "평일오후권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "주말1일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19306:
            if ticket_name in ["평일 당일권", "주말 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "평일 심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19398:
            if ticket_name == "당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name == "심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "3시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19399:
            if ticket_name in ["평일1일권", "주말1일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name in ["심야권(일~목)", "심야권(금~토)"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19791:
            if ticket_name in ["평일 1일권", "주말1일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name == "심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19964:
            if ticket_name == "평일 당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19796:
            if ticket_name == "평일 당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19362:
            if ticket_name in ["평일 당일권", "휴일 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "평일 심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19478:
            if ticket_name == "심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19982:
            if ticket_name in ["평일 당일권", "주말 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name == "평일 심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 29050:
            if ticket_name in ["평일 당일권", "휴일 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_4_discountTkGrp']"
                )
            elif ticket_name == "2일 연박권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "3일 연박권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "4일 연박권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name == "5일 연박권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_3_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19967:
            if ticket_name in ["평일 당일권", "휴일 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "평일 3시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "평일 심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        else:
            try:
                driver.implicitly_wait(3)
                driver.find_element_by_xpath(side_nav_xpath).click()

                print(Colors.BLUE + "제휴주차장없음" + Colors.ENDC)
                return False
            except Exception as ex:
                print(f"Error during process: {ex}")
                return False

    return False

