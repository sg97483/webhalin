# -*- coding: utf-8 -*-
from telnetlib import EC

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import Util
import Colors
from park import ParkUtil, ParkType
import WebInfo

mapIdToWebInfo = {

    # (하이파킹)서울역 서울스퀘어
    12903: ["TextBox_ID", "TextBox_Pwd", "//*[@id='Button_Login']",
            "TextBox_CarNum", "//*[@id='Button_Search']",
            "#DataGrid1 > tbody > tr:nth-child(2) > td:nth-child(3) > a"
            ],

    # 하이파킹 삼성화재서초타워 (요소 수정)
    19919: ["login_id", "login_pw", "//input[@value='로그인']",  # 로그인 버튼 수정
            "searchCarNo", "//*[@id='btnSearch']",  # 차량 번호 입력 필드, 검색 버튼
            "//td/a[contains(text(), '{car_number}')]"
            ],

}


def get_har_in_script(park_id, ticket_name):
    try:
        if park_id not in mapIdToWebInfo:
            print(Colors.RED + f"해당 park_id({park_id})에 대한 할인 정보가 없습니다." + Colors.ENDC)
            return False  # 해당 주차장에 정보 없으면 실패

        # WebInfo.methodHarIn1이 정수인지 확인
        if not hasattr(WebInfo, 'methodHarIn1') or not isinstance(WebInfo.methodHarIn1, int):
            print(Colors.RED + f"WebInfo.methodHarIn1이 올바른 정수가 아닙니다: {WebInfo.methodHarIn1}" + Colors.ENDC)
            return False

        # 디버깅: mapIdToWebInfo의 내용 확인
        print(f"mapIdToWebInfo[{park_id}] = {mapIdToWebInfo[park_id]}")

        # 리스트 인덱스 유효성 확인
        if WebInfo.methodHarIn1 >= len(mapIdToWebInfo[park_id]):
            print(Colors.RED + f"mapIdToWebInfo[{park_id}]에 유효한 인덱스({WebInfo.methodHarIn1})가 없습니다." + Colors.ENDC)
            return False

        return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]

    except Exception as e:
        print(Colors.RED + f"할인 스크립트 가져오는 중 오류 발생: {e}" + Colors.ENDC)
        return False


def web_har_in(target, driver):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]
    park_type = ParkType.get_park_type(park_id)

    trim_car_num = Util.all_trim(ori_car_num)
    search_id = trim_car_num[-4:]  # 차량번호 마지막 4자리

    print(f"parkId = {park_id}, searchId = {search_id}")
    print(Colors.BLUE + ticket_name + Colors.ENDC)

    if ParkUtil.is_park_in(park_id):
        if park_id == 19919:  # 삼성화재서초타워
            login_url = ParkUtil.get_park_url(park_id)
            driver.get(login_url)
            driver.implicitly_wait(5)

            try:
                # 로그인
                login_info = ParkUtil.get_park_lot_option(park_id)
                print("DEBUG login_info:", login_info)
                print("DEBUG type:", type(login_info))

                user_id = login_info[1]
                user_pw = login_info[2]

                driver.find_element(By.ID, "login_id").send_keys(user_id)
                driver.find_element(By.ID, "login_pw").send_keys(user_pw)
                driver.find_element(By.XPATH, "//input[@value='로그인']").click()

                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "searchCarNo"))
                )

                # 차량번호 입력 및 확인
                driver.find_element(By.ID, "searchCarNo").send_keys(search_id)
                driver.find_element(By.ID, "btnSearch").click()

                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "divAjaxCarList"))
                )

                # 차량번호 링크 찾기
                car_list_xpath = '//*[@id="divAjaxCarList"]//a'
                all_links = driver.find_elements(By.XPATH, car_list_xpath)
                matched = False
                for link in all_links:
                    car_text = link.text.strip()
                    if ori_car_num in car_text:
                        print("DEBUG: 차량번호 매칭됨:", car_text)
                        driver.execute_script("arguments[0].click();", link)
                        matched = True
                        break

                if not matched:
                    print(Colors.RED + "차량번호가 포함된 링크를 찾을 수 없음." + Colors.ENDC)
                    return False

                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "divAjaxFreeDiscount"))
                )

                # 할인권 버튼 XPath 선택
                if ticket_name == "평일 12시간권(지하 6층 전용)":
                    discount_button_xpath = '//*[@id="divAjaxFreeDiscount"]/div/div/button[1]'
                elif ticket_name == "휴일 당일권(지하 6층 전용)":
                    discount_button_xpath = '//*[@id="divAjaxFreeDiscount"]/div/div/button[2]'
                elif ticket_name in ["평일 야간권(지하 6층 전용,금~토)", "평일 야간권(지하 6층 전용,일~목)"]:
                    discount_button_xpath = '//*[@id="divAjaxFreeDiscount"]/div/div/button[3]'
                else:
                    print(Colors.RED + f"지원되지 않는 할인권: {ticket_name}" + Colors.ENDC)
                    return False

                # 할인 버튼 클릭
                try:
                    discount_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, discount_button_xpath))
                    )
                    discount_button.click()
                    try:
                        WebDriverWait(driver, 3).until(EC.alert_is_present())
                        driver.switch_to.alert.accept()
                    except TimeoutException:
                        print("DEBUG: 할인 적용 후 알림창 없음.")
                    print(Colors.GREEN + f"{ticket_name} 할인 적용 완료!" + Colors.ENDC)
                except Exception as e:
                    print(Colors.RED + f"할인 버튼 클릭 실패: {e}" + Colors.ENDC)
                    return False

                # 로그아웃
                try:
                    logout_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '로그아웃')]"))
                    )
                    logout_button.click()
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "login_id")))
                    print(Colors.GREEN + "로그아웃 완료, 다음 차량 진행!" + Colors.ENDC)
                except Exception as e:
                    print(Colors.RED + f"로그아웃 실패: {e}" + Colors.ENDC)

                return True

            except TimeoutException:
                print(Colors.RED + "페이지 로딩이 너무 오래 걸렸습니다." + Colors.ENDC)
                return False
            except NoSuchElementException as e:
                print(Colors.RED + f"요소를 찾을 수 없습니다: {e}" + Colors.ENDC)
                return False

        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False



