# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import Util
import Colors
from park import ParkUtil
import WebInfo

# 서초구 방문할인 서비스 대상 주차장 목록
HI_SEOCHO_PARK_IDS = [19273, 29196, 19236, 19237, 19456, 19453, 29195]

mapIdToWebInfo = {
    park_id: [
        "portalId", 
        "password", 
        "//button[contains(text(), '로그인')]", 
        "//input[contains(@placeholder, '차량번호') or @title='차량번호 입력']", 
        "//button[contains(text(), '검색')]"
    ]
    for park_id in HI_SEOCHO_PARK_IDS
}


def handle_alert(driver):
    """
    브라우저 기본 Alert 창 처리
    """
    try:
        WebDriverWait(driver, 2).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"DEBUG: Alert 발견 - {alert.text}")
        alert.accept()
        print("DEBUG: Alert 닫기 완료")
    except TimeoutException:
        pass
    except Exception as e:
        print(f"DEBUG: Alert 처리 중 예외: {e}")


def logout(driver):
    """
    로그아웃 버튼 클릭 및 이후 Alert/확인창 처리
    """
    try:
        logout_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='로그아웃' or contains(text(), '로그아웃')]"))
        )
        logout_btn.click()
        print("DEBUG: 로그아웃 버튼 클릭 완료.")
        time.sleep(1)
        handle_alert(driver)
        return True
    except TimeoutException:
        print("DEBUG: 로그아웃 버튼을 찾을 수 없거나 이미 로그아웃된 상태입니다.")
        return False
    except Exception as e:
        print(f"WARNING: 로그아웃 중 예외 발생: {e}")
        return False


def enter_user_id_and_pw(driver, user_id, user_password):
    """
    로그인 페이지의 아이디 및 비밀번호 입력 후 로그인 버튼 클릭
    """
    try:
        id_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "portalId"))
        )
        id_field.clear()
        id_field.send_keys(user_id)
        print(f"DEBUG: 아이디 '{user_id}' 입력 완료")

        pw_field = driver.find_element(By.ID, "password")
        pw_field.clear()
        pw_field.send_keys(user_password)
        print("DEBUG: 비밀번호 입력 완료")

        login_btn = driver.find_element(By.XPATH, "//button[normalize-space()='로그인' or contains(text(), '로그인')]")
        login_btn.click()
        print("DEBUG: 로그인 버튼 클릭 완료")

        time.sleep(2)
        handle_alert(driver)
        return True
    except TimeoutException:
        print("ERROR: 로그인 필드(portalId)를 찾을 수 없습니다.")
        return False
    except Exception as e:
        print(f"ERROR: 로그인 중 예외 발생: {e}")
        return False


def enter_car_number_and_search(driver, car_number_last4):
    """
    차량번호 4자리를 입력하고 검색 버튼 클릭.
    조회 실패 팝업('검색된 차량이 없습니다.')이 뜨면 팝업 닫고 로그아웃 후 False 반환.
    """
    try:
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, '차량번호') or @title='차량번호 입력']"))
        )
        input_field.clear()
        input_field.send_keys(car_number_last4)
        print(f"DEBUG: 차량번호 '{car_number_last4}' 입력 완료")

        search_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='검색' or contains(text(), '검색')]"))
        )
        search_button.click()
        print("DEBUG: 차량번호 검색 버튼 클릭 완료")

        # 검색 후 '검색된 차량이 없습니다.' 팝업 확인
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//p[contains(text(), '검색된 차량이 없습니다.')]"))
            )
            print("DEBUG: '검색된 차량이 없습니다.' 팝업 감지됨.")

            # 확인 버튼 클릭
            try:
                ok_button = driver.find_element(By.XPATH, "//div[@role='dialog']//button[normalize-space()='확인' or contains(text(), '확인')]")
                ok_button.click()
                print("DEBUG: '검색된 차량이 없습니다.' 팝업 확인 버튼 클릭 완료")
            except Exception:
                try:
                    close_btn = driver.find_element(By.XPATH, "//div[@role='dialog']//button[contains(@aria-label, '닫기') or contains(text(), '×')]")
                    close_btn.click()
                    print("DEBUG: '검색된 차량이 없습니다.' 팝업 닫기 버튼 클릭 완료")
                except Exception as ex:
                    print(f"DEBUG: 팝업 버튼 클릭 실패: {ex}")

            WebDriverWait(driver, 3).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[@role='dialog']//p[contains(text(), '검색된 차량이 없습니다.')]"))
            )
            print("DEBUG: 팝업 닫힘 완료. 로그아웃 후 False 반환.")
            logout(driver)
            return False

        except TimeoutException:
            print("DEBUG: '검색된 차량이 없습니다.' 팝업 없음 -> 차량 조회 성공으로 판단.")
            return True

    except Exception as e:
        print(f"ERROR: 차량번호 검색 중 예외 발생: {e}")
        logout(driver)
        return False


def handle_ticket(driver, park_id, ticket_name):
    """
    차량 조회 성공 후 할인권 버튼 클릭, 적용 버튼 클릭, 로그아웃 후 True 반환
    """
    try:
        # 할인권 버튼 영역 로드 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(), '할인시간 선택')]/following-sibling::div//button"))
        )
        print(f"DEBUG: 할인시간 선택 영역 로드 완료 (park_id={park_id}, ticket_name={ticket_name})")

        target_btn_text = ticket_name
        if park_id == 29196:
            if ticket_name == "평일 야간권":
                target_btn_text = "야간 13시간권"
            elif ticket_name == "휴일 당일권":
                target_btn_text = "전일권"
            else:
                target_btn_text = ticket_name
        else:
            target_btn_text = ticket_name

        print(f"DEBUG: 사이트에서 클릭할 할인권 버튼 명칭: '{target_btn_text}'")

        # 할인권 버튼 클릭
        try:
            ticket_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space()='{target_btn_text}' or contains(text(), '{target_btn_text}')]"))
            )
            ticket_button.click()
            print(f"DEBUG: 할인권 버튼 '{target_btn_text}' 클릭 완료.")
        except TimeoutException:
            print(f"ERROR: 할인권 버튼 '{target_btn_text}'을(를) 찾을 수 없거나 클릭할 수 없습니다.")
            logout(driver)
            return False

        time.sleep(1)  # 할인권 선택 시 적용 버튼 활성화 대기

        # 적용 버튼 클릭
        try:
            apply_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='적용' or contains(text(), '적용')]"))
            )
            apply_button.click()
            print("DEBUG: '적용' 버튼 클릭 완료.")
        except TimeoutException:
            print("ERROR: '적용' 버튼을 찾을 수 없거나 활성화되지 않았습니다.")
            logout(driver)
            return False

        time.sleep(2)
        handle_alert(driver)  # 적용 후 뜨는 Alert 창 처리

        print("DEBUG: 할인 적용 완료. 로그아웃 진행 및 True 반환.")
        logout(driver)
        return True

    except Exception as e:
        print(f"ERROR: 할인권 처리 중 예외 발생: {e}")
        logout(driver)
        return False


def web_har_in(target, driver):
    """
    서초구 방문할인 서비스 (https://parking.seocho.go.kr/visit) 메인 처리 함수
    """
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]

    if (ParkUtil.is_park_in(park_id) or park_id in HI_SEOCHO_PARK_IDS) and park_id in mapIdToWebInfo:
        login_url = ParkUtil.get_park_url(park_id) if ParkUtil.is_park_in(park_id) else "https://parking.seocho.go.kr/visit"

        print(f"DEBUG: [HiSeoCho] {login_url} 페이지로 이동합니다... (park_id: {park_id})")
        driver.get(login_url)
        time.sleep(2)

        web_har_in_info = ParkUtil.get_park_lot_option(park_id)
        user_id = web_har_in_info[WebInfo.webHarInId]
        user_password = web_har_in_info[WebInfo.webHarInPw]

        try:
            # 1. 로그인 페이지(#portalId)가 있는지 확인하여 로그인 진행
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.ID, "portalId"))
                )
                if not enter_user_id_and_pw(driver, user_id, user_password):
                    return False
            except TimeoutException:
                print("DEBUG: 로그인 페이지(#portalId) 감지되지 않음 -> 이미 로그인된 상태로 판단하여 검색 페이지 진행")

            # 2. 차량번호 4자리 검색 진행
            if not enter_car_number_and_search(driver, ori_car_num[-4:]):
                return False

            # 3. 차량 조회 성공 시 할인권 선택 및 적용 -> 로그아웃 후 True 반환
            return handle_ticket(driver, park_id, ticket_name)

        except Exception as ex:
            print(f"ERROR: [HiSeoCho] 할인 처리 중 오류 발생: {ex}")
            logout(driver)
            return False

    return False
