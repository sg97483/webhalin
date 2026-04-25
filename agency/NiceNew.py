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
import re
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

        # stale element 방지를 위해 직접 요소를 다시 찾기
        cancel_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "mf_wfm_body_btn_cancel"))
        )
        driver.execute_script("arguments[0].click();", cancel_button)
        print("DEBUG: 비밀번호 초기화 팝업 '아니오' 버튼 클릭 완료.")

        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.ID, "mf_wfm_body_ui_initPwdPop_contents"))
        )
        print("DEBUG: 비밀번호 초기화 팝업 닫힘 확인 완료.")

    except TimeoutException:
        print("DEBUG: 비밀번호 초기화 팝업이 감지되지 않음. (정상일 수 있음)")
    except Exception as e:
        print(f"DEBUG: 비밀번호 초기화 팝업 처리 중 오류: {e}")




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
            # stale element 방지를 위해 직접 요소를 다시 찾기
            confirm_button = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='확인']"))
            )
            driver.execute_script("arguments[0].click();", confirm_button)
            print("DEBUG: 팝업 '확인' 버튼 JS로 강제 클릭 완료.")

            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "w2popup_window"))
            )
            print("DEBUG: 팝업 닫힘 완료.")
        except NoSuchElementException:
            print("DEBUG: 팝업에는 '확인' 버튼이 없음 (무시하고 진행).")
        except Exception as e:
            print(f"DEBUG: 팝업 '확인' 버튼 처리 중 오류: {e}")
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
            EC.visibility_of_element_located((By.XPATH, radio_xpath))
        )
        print("할인 버튼 감지됨. 클릭 시도.")

        # 재탐색 후 클릭 (JavaScript로 강제 클릭)
        discount_button = driver.find_element(By.XPATH, radio_xpath)
        driver.execute_script("arguments[0].click();", discount_button)
        print(Colors.BLUE + "할인 처리 완료" + Colors.ENDC)

        # 할인권 클릭 후 실제 적용 여부 검증 (HTML 분석 기반, 최대 5초 대기)
        try:
            # '적용된 할인권' 영역(apply_ticket_box)이 DOM에 생성되는지 확인
            # 제공해주신 HTML: <div ... class="w2group apply_ticket_box blue etc">
            verify_xpath = "//*[contains(@class, 'apply_ticket_box')]"
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, verify_xpath))
            )
            print(Colors.BLUE + "검증 성공: 할인권이 정상적으로 목록에 등록되었습니다." + Colors.ENDC)
            
            # 검증 성공 후 화면 UI 안정화를 위해 잠시 대기
            time.sleep(1)

        except TimeoutException:
            print(Colors.RED + "검증 실패: 할인 버튼을 눌렀으나 '적용된 할인권'이 나타나지 않음. (할인 미적용)" + Colors.ENDC)
            # 할인 적용이 안 됐으므로 로그아웃 전 False 반환
            return False

        # 할인권 클릭 이후
        driver.execute_script("document.getElementById('___processbar2').style.display='none';")
        print("DEBUG: 로딩 모달 강제로 숨김.")

        # _modal 팝업 강제 제거
        try:
            # 먼저 _modal이 있는지 확인
            modal = driver.find_element(By.ID, "_modal")
            if modal.is_displayed():
                print("DEBUG: _modal 팝업 감지됨. 강제 제거 시도.")
                driver.execute_script("document.getElementById('_modal').style.display='none';")
                driver.execute_script("document.getElementById('_modal').remove();")
                print("DEBUG: _modal 강제 제거 완료.")
        except NoSuchElementException:
            print("DEBUG: _modal 팝업이 없음.")
        
        # 추가 대기 및 확인
        time.sleep(1)

        # 로그아웃 버튼 클릭 전 대기
        print("로그아웃 버튼 클릭 전 대기 중...")
        logout_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mf_wfm_header_btn_logout"))  # 로그아웃 버튼 ID
        )
        driver.execute_script("arguments[0].click();", logout_button)
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
        # 할인 실패 시 강제 로그아웃 및 세션 정리
        try:
            # _modal 팝업 강제 제거
            try:
                modal = driver.find_element(By.ID, "_modal")
                if modal.is_displayed():
                    driver.execute_script("document.getElementById('_modal').style.display='none';")
                    driver.execute_script("document.getElementById('_modal').remove();")
                    print("DEBUG: 예외 처리 중 _modal 강제 제거 완료.")
            except NoSuchElementException:
                pass

            logout_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "mf_wfm_header_btn_logout"))
            )
            driver.execute_script("arguments[0].click();", logout_button)
            print("DEBUG: 할인 실패 후 로그아웃 시도 완료.")

        except Exception as logout_ex:

            print(f"DEBUG: 할인 실패 후 로그아웃도 실패: {logout_ex}")

        try:

            driver.delete_all_cookies()
            driver.get("about:blank")
            print("DEBUG: 세션 초기화 완료.")

        except Exception as clear_ex:

            print(f"DEBUG: 세션 초기화 중 오류: {clear_ex}")

        return False


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

        # stale element 방지를 위해 직접 요소를 다시 찾기
        confirm_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='확인']"))
        )
        driver.execute_script("arguments[0].click();", confirm_button)
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
            driver.execute_script("arguments[0].click();", logout_button)
            print("DEBUG: 로그아웃 버튼이 클릭되었습니다.")
        except NoSuchElementException:
            print("DEBUG: 로그아웃 버튼을 찾을 수 없습니다. DOM 구조를 확인하세요.")
            raise
        except Exception as e:
            print(f"DEBUG: 로그아웃 버튼 클릭 중 오류: {e}")

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
    차량번호 검색 실패 시 나타나는 팝업 감지 후 '확인' 클릭 및 로그아웃, 세션 초기화까지 포함.
    실패 시 False 반환. 정상 진행 가능 시 True.
    """
    print("DEBUG: check_search_failed_and_logout() 함수 진입 시도")
    
    # 먼저 팝업이 있는지 확인
    popup_detected = False
    try:
        # 1. 차량 검색 실패 팝업 감지 (messagebox class 포함)
        popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.w2popup_window.messagebox"))
        )
        print("DEBUG: 차량번호 검색 실패 팝업 감지됨.")
        popup_detected = True

        # 2. '확인' 버튼 클릭
        confirm_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.w2popup_window.messagebox input[type='button'][value='확인']"))
        )
        driver.execute_script("arguments[0].click();", confirm_button)
        print("DEBUG: 팝업 '확인' 버튼 클릭 완료.")

        # 3. 팝업 닫힘 대기
        time.sleep(1)  # 확인 버튼 클릭 후 잠시 대기
        
        print("DEBUG: 검색 실패 팝업 처리 완료.")

    except TimeoutException:
        print("DEBUG: 차량 검색 실패 팝업이 감지되지 않음.")

    except Exception as ex:
        print(f"DEBUG: 팝업 처리 중 예외 발생: {ex}")

    # 팝업이 감지되었다면 로그아웃하고 False 반환
    if popup_detected:
        # 로그아웃 시도
        try:
            driver.execute_script(
                "var modal = document.getElementById('_modal'); if(modal) modal.style.display='none';"
            )
            logout_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "mf_wfm_header_btn_logout"))
            )
            driver.execute_script("arguments[0].click();", logout_button)
            print("DEBUG: 로그아웃 버튼 클릭 성공")
        except Exception as logout_ex:
            print(f"DEBUG: 로그아웃 버튼 클릭 실패: {logout_ex}")

        # 세션 정리
        try:
            driver.delete_all_cookies()
            driver.get("about:blank")
            print("DEBUG: 세션 쿠키 제거 및 빈 페이지 로딩 완료")
        except Exception as clear_ex:
            print(f"DEBUG: 세션 정리 중 예외 발생: {clear_ex}")

        print(Colors.YELLOW + "DEBUG: 차량 검색 실패 후 로그아웃 및 세션 초기화 완료 (False 반환)" + Colors.ENDC)
        return False
    
    # 팝업이 없었다면 할인권 화면이 있는지 확인
    try:
        WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "used_ticket_box"))
        )
        print("DEBUG: 할인권 화면 감지됨 → 정상 진행")
        return True
    except:
        # 할인권 화면이 없더라도, 차량 선택 팝업이 떠 있다면 정상 진행으로 간주
        if is_car_selection_popup_present(driver, timeout=1):
            print("DEBUG: 할인권 화면은 없으나 차량 선택 팝업 감지됨 → 정상 진행")
            return True

        print("DEBUG: 할인권 화면도 없고 차량 선택 팝업도 없음 → 검색 실패로 판단")
        # 여기서도 로그아웃 처리
        try:
            driver.execute_script(
                "var modal = document.getElementById('_modal'); if(modal) modal.style.display='none';"
            )
            logout_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "mf_wfm_header_btn_logout"))
            )
            driver.execute_script("arguments[0].click();", logout_button)
            print("DEBUG: 할인권 화면 없음 → 로그아웃")
        except Exception as logout_ex:
            print(f"DEBUG: 로그아웃 실패: {logout_ex}")
        return False


def click_matching_car_number(driver, ori_car_num):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "mf_wfm_body_list_carGridView_body_table"))
        )
        print("DEBUG: 차량 선택 팝업 테이블 감지됨")

        rows = driver.find_elements(By.CSS_SELECTOR, "#mf_wfm_body_list_carGridView_body_table > tbody > tr")

        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells or len(cells) < 4:
                    continue

                full_car_num = cells[1].text.strip()

                # 차량번호 비교: 최소 6자리 이상 일치해야 함 (예: 12소1234 → 2소1234까지)
                full_clean = full_car_num.replace(" ", "")
                ori_clean = ori_car_num.replace(" ", "")
                
                # 최소 6자리부터 전체까지 비교
                min_match_length = 6
                max_match_length = min(len(full_clean), len(ori_clean))
                
                match_found = False
                for match_length in range(min_match_length, max_match_length + 1):
                    if full_clean[-match_length:] == ori_clean[-match_length:]:
                        print(f"✅ 차량번호 끝 {match_length}자리 일치: {full_car_num} → 선택 버튼 클릭")
                        match_found = True
                        break
                
                if match_found:
                    select_button = cells[3].find_element(By.TAG_NAME, "button")
                    driver.execute_script("arguments[0].click();", select_button)
                    return True
            except Exception as e:
                print(f"DEBUG: 각 행 처리 중 오류: {e}")
                continue

        print("⚠️ 일치하는 차량번호를 찾을 수 없습니다.")
        return False

    except TimeoutException:
        print("DEBUG: 차량 선택 테이블이 감지되지 않음 (팝업이 뜨지 않았을 수도 있음)")
        return True


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
        handle_popup(driver)

    except Exception as e:
        print(f"DEBUG: 선택 팝업 처리 중 예외 발생: {e}")


def is_car_selection_popup_present(driver, timeout=2):
    """
    차량 선택 팝업이 실제로 떠 있는지 확인합니다.
    (단순 존재 여부가 아니라, 표시되고 있는지까지 확인)
    """
    try:
        table = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "mf_wfm_body_list_carGridView_body_table"))
        )
        if table.is_displayed():
            return True
        else:
            return False
    except TimeoutException:
        return False




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

            # 차량번호 뒤 4자리 추출 (숫자만)
            # 숫자만 추출
            numbers_only = re.sub(r'[^0-9]', '', ori_car_num)
            car_number_last4 = numbers_only[-4:] if len(numbers_only) >= 4 else numbers_only
            print(f"입력할 차량번호 마지막 4자리 (숫자만): {car_number_last4}")

            # 차량번호 입력
            enter_car_number(driver, car_number_last4)

            # 차량 검색 실패 팝업 감지 → 로그아웃 → 실패 처리
            print("DEBUG: check_search_failed_and_logout() 함수 진입 시도")  # <-- 이 줄을 추가
            if not check_search_failed_and_logout(driver):
                print("DEBUG: check_search_failed_and_logout() 함수에서 False 반환됨 → 종료")  # Optional
                return False


            # 차량 선택 팝업이 뜬 경우 → 정확히 일치하는 차량 선택
            if is_car_selection_popup_present(driver):
                print("DEBUG: 차량 선택 팝업 감지됨 → 차량 선택 시도")
                if not click_matching_car_number(driver, ori_car_num):
                    print("DEBUG: 차량 선택 실패 → 종료")
                    return False
            else:
                print("DEBUG: 차량 선택 팝업이 뜨지 않음 → 단일 차량 검색으로 판단하고 진행")


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
            if ticket_name == "평일 당일권":
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
            elif ticket_name == "휴일 당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19966:
            if ticket_name == "심야권(일~목)":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "심야권(금~토)":
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
            elif ticket_name in ["심야권(일~목)", "심야권(금~토)"]:
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
            if ticket_name in ["평일 당일권", "주말 당일권", "휴일 당일권"]:
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

        elif park_id == 19988:
            if ticket_name in ["평일 1일권", "주말 1일권"]:
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

        elif park_id == 19770:
            if ticket_name in ["평일1일권", "주말1일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name == "평일3시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 29214:
            if ticket_name in ["평일 당일권", "휴일 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_5_discountTkGrp']"
                )
            elif ticket_name in ["휴일 심야권", "평일 심야권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_4_discountTkGrp']"
                )
            elif ticket_name == "평일 3시간권(기계식,승용전용)":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "평일 5시간권(기계식,승용전용)":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19966:
            if ticket_name in ["심야권(일~목)", "심야권(금~토)"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19981:
            if ticket_name in ["평일 당일권", "휴일 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name == "평일 주간권":
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

        elif park_id == 19297:
            if ticket_name in ["심야권(일~목)", "심야권(금~토)"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "주말1일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19307:
            if ticket_name in ["심야권(일~목)", "심야권(금~토)"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "주말1일권 (일요일권)":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19309:
            if ticket_name in ["평일1일권", "주말1일권"]:
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


        elif park_id == 19979:
            if ticket_name in ["평일 당일권", "휴일 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            elif ticket_name == "3시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19974:

            if ticket_name == "평일 심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "토요일 당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 29235:

            if ticket_name == "평일 3시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "평일 당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19976:
            if ticket_name in ["평일 당일권", "휴일 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_3_discountTkGrp']"
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
            elif ticket_name == "야간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_2_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 29095:

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


        elif park_id == 19975:

            if ticket_name == "평일 3시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "주말 3시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "주말 당일권":
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

        elif park_id == 19295:

            if ticket_name == "평일1일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "주말1일권":
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

        elif park_id == 19970:

            if ticket_name == "평일 당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "휴일 당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )

            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19991:

            if ticket_name == "2시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "4시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "심야권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_3_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19284:

            if ticket_name == "평일 저녁권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name in ["평일1일권", "주말1일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 19832:

            if ticket_name in ["평일심야권", "주말심야권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 29116:

            if ticket_name in ["평일 1일권", "주말 1일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name == "5시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19958:

            if ticket_name in ["평일 당일권", "휴일 당일권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name in ["평일 3시간권", "휴일 3시간권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19781:

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

        elif park_id == 19765:

            if ticket_name == "평일1일권":
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

        elif park_id == 29272:

            if ticket_name == "평일 당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name == "주말 당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 29317:

            if ticket_name == "평일 당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_1_discountTkGrp']"
                )
            elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)



        elif park_id == 19792:

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


        elif park_id == 29590:

            if ticket_name == "평일 3시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            elif ticket_name in ["평일 당일권", "휴일 당일권"]:
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


        elif park_id == 29171:

            if ticket_name == "평일 주간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
                )
            else:
                return handle_invalid_ticket(driver)


        elif park_id == 29168:
            if ticket_name == "평일 주간권(승용전용)":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='mf_wfm_body_gen_dcTkList_0_discountTkGrp']"
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

