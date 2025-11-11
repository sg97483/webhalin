# -*- coding: utf-8 -*-
import re
import smtplib
import time
from email.mime.text import MIMEText

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import Colors
import Util
import WebInfo
from park import ParkUtil, ParkType

mapIdToWebInfo = {

    # 논현점(AJ파크)
    19156: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일종일권
            0,  # 주말종일권 없음
            1  # 야간권
            ],

    # 하이파킹 딜라이트스퀘어2차상가점
    19600: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],

    # 하이파킹 L7호텔강남
    19004: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],

    # TURU 마곡나루역캐슬파크
    19860: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],

    # 하이파킹 덕수궁롯데캐슬점
    29184: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],

    # 하이파킹 회룡역하나프라자점
    19810: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],

    # 하이파킹 L7호텔홍대
    29136: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],

    # 하이파킹 강남빌딩
    19271: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],

    # TURU KTnG타워
    19862: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],

    # ▼▼▼▼▼ 19540 (하이파킹 대전둔산점) 추가 ▼▼▼▼▼
    19540: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권 (사용하지 않지만 형식상 추가)
            0,  # 주말
            0   # 야간
            ],

    # 하이파킹 서울가든호텔점
    19148: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],

    # ▼▼▼▼▼ 19534 (하이파킹 원주서영에비뉴파크1점) 추가 ▼▼▼▼▼
    19534: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권 (사용하지 않지만 형식상 추가)
            0,  # 주말
            0   # 야간
            ],
}


def get_har_in_script(park_id, ticket_name):
    if ticket_name == "평일1일권":
        return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]
    elif ticket_name == "주말1일권":
        return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]
    elif ticket_name == "심야권":
        return mapIdToWebInfo[park_id][WebInfo.methodHarIn3]
    else:
        return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]


AJ_PARK_ID = "parkingpark@wisemobile.co.kr"
AJ_PARK_PW = "@wise0413"


def handle_ticket(driver, park_id, ticket_name):
    """
    주차장 및 주차권에 따른 할인권 처리 (19004, 19600 포함)
    """
    print(f"DEBUG: 할인 처리 시작 (park_id={park_id}, ticket_name={ticket_name})")

    if park_id == 19156:  # <<-- 여기에 실제 새 주차장의 park_id를 입력하세요.
        ticket_map = {
            "평일 6시간권": "309700",  # HTML: 평일6시간권(공유서비스)
            "평일 4시간권": "334295",  # HTML: 평일 4시간권(Online)
            "평일 3시간권": "347833",  # HTML: 3시간(공유서비스)
            "평일 2시간권": "347834",  # HTML: 2시간(공유서비스)
            "평일 1시간권": "347835",  # HTML: 1시간(공유서비스)
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: {park_id}에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_value = ticket_map[ticket_name]

        try:
            # <select> 요소를 찾습니다.
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )

            # Select 객체를 생성하고 value로 옵션을 선택합니다.
            select = Select(select_element)
            select.select_by_value(target_value)
            print(f"DEBUG: value '{target_value}' (티켓: {ticket_name}) 할인권 선택 완료.")

            # '할인 적용' 버튼 클릭
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            # 알림창 처리
            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: {park_id} 처리 중 예외 발생: {e}")
            return False

    if park_id == 19540:
        ticket_map = {
            "평일 당일권(월)": "평일당일권(공유)",
            "평일 당일권(화)": "평일당일권(공유)",
            "평일 당일권(수)": "평일당일권(공유)",
            "평일 당일권(목)": "평일당일권(공유)",
            "평일 당일권(금)": "평일당일권(공유)",
            "평일 3시간권": "평일3시간권(공유서비스)",
            "평일 2시간권": "평일2시간권(공유서비스)",
            "평일 1시간권": "평일1시간권(공유서비스)",
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: 19540에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_text = ticket_map[ticket_name]

        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )
            options = select_element.find_elements(By.TAG_NAME, "option")
            matched = False
            for option in options:
                # 텍스트가 정확히 일치하거나, 해당 텍스트로 시작하는 옵션을 찾음
                if target_text in option.text:
                    option.click()
                    print(f"DEBUG: '{option.text}' 옵션 선택 완료.")
                    matched = True
                    break

            if not matched:
                print(f"ERROR: '{target_text}' 텍스트가 포함된 옵션을 찾을 수 없습니다.")
                return False

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: 19540 처리 중 예외 발생: {e}")
            return False
            # ▲▲▲▲▲ 19540 추가 완료 ▲▲▲▲▲

    # ✅ 19534 전용 할인 처리 (하이파킹 원주서영에비뉴파크1점)
    if park_id == 19534:
        ticket_map = {
            "평일 당일권": "평일당일권(공유)",
            "주말1일권": "평일당일권(공유)",  # HTML 옵션 확인 필요
            "평일 3시간권": "평일3시간권(공유)",
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: 19534에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_text = ticket_map[ticket_name]

        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )
            options = select_element.find_elements(By.TAG_NAME, "option")
            matched = False
            for option in options:
                # 텍스트가 정확히 일치하거나, 해당 텍스트로 시작하는 옵션을 찾음
                if target_text in option.text:
                    option.click()
                    print(f"DEBUG: '{option.text}' 옵션 선택 완료.")
                    matched = True
                    break

            if not matched:
                print(f"ERROR: '{target_text}' 텍스트가 포함된 옵션을 찾을 수 없습니다.")
                return False

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: 19534 처리 중 예외 발생: {e}")
            return False

        # ✅ 19862 신규 주차장 전용 할인 처리
    if park_id == 19862:
        ticket_map = {
                "평일 당일권(월)": "201805",  # HTML: 평일당일권_(ONLINE)
                "평일 당일권(화)": "201805",  # HTML: 평일당일권_(ONLINE)
                "평일 당일권(수)": "201805",  # HTML: 평일당일권_(ONLINE)
                "평일 당일권(목)": "201805",  # HTML: 평일당일권_(ONLINE)
                "평일당일권(금)": "201805",  # HTML: 평일당일권_(ONLINE)
                "평일오후6시간권": "237809",  # HTML: 평일 오후권_(ONLINE)
                "평일오후6시간권(금)": "237809",  # HTML: 평일 오후권_(ONLINE)
                "평일 3시간권": "201804",  # HTML: 평일3시간권_(ONLINE)
                "평일 2시간권": "347857",  # HTML: 2시간(공유서비스)
                "평일 1시간권": "347858",  # HTML: 1시간(공유서비스)
                "휴일 당일권": "201806",  # HTML: 휴일당일권_(ONLINE)
                "야간권": "292451",  # HTML: 야간권(ONLINE)
        }

        if ticket_name not in ticket_map:
                # 스크린샷에 없는 '3시간(공유서비스)' 같은 케이스를 위해 예외 처리
            if "3시간" in ticket_name:
                    target_value = "347856"
            else:
                    print(f"ERROR: 19862에서 지원하지 않는 ticket_name: {ticket_name}")
                    return False
        else:
            target_value = ticket_map[ticket_name]

            try:
                # <select> 요소를 찾습니다.
                select_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "selectDiscount"))
                )

                # Select 객체를 생성하고 value로 옵션을 선택합니다.
                select = Select(select_element)
                select.select_by_value(target_value)
                print(f"DEBUG: park_id 19862: value '{target_value}' (티켓: {ticket_name}) 할인권 선택 완료.")

                # '할인 적용' 버튼 클릭
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "discountSubmit"))
                ).click()
                print("DEBUG: 할인 적용 버튼 클릭 완료.")

                # 알림창 처리
                try:
                    WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                    print("DEBUG: 알림창 확인 완료.")
                except TimeoutException:
                    print("DEBUG: 알림창 없음.")

                return True

            except Exception as e:
                print(f"ERROR: 19862 처리 중 예외 발생: {e}")
                return False

    # ✅ 19004 전용 할인 처리
    if park_id == 19004:
        ticket_map = {
            "평일 12시간권": "평일12시간권(공유서비스)",
            "평일 12시간권(월)": "평일12시간권(공유서비스)",
            "평일 12시간권(화)": "평일12시간권(공유서비스)",
            "평일 12시간권(수)": "평일12시간권(공유서비스)",
            "평일 12시간권(목)": "평일12시간권(공유서비스)",
            "평일 12시간권(금)": "평일12시간권(공유서비스)",
            "휴일 당일권": "휴일당일권(공유서비스)",
            "휴일 당일권(토~일)": "휴일당일권(공유서비스)",
            "야간권": "야간권(공유서비스)",
            "평일 3시간권": "3시간(공유서비스)",
            "평일 2시간권": "2시간(공유서비스)",
            "평일 1시간권": "1시간(공유서비스)",
            "휴일 3시간권": "3시간(공유서비스)",
            "휴일 심야권": "야간권(공유서비스)",
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: 19004에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_text = ticket_map[ticket_name]

        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )
            options = select_element.find_elements(By.TAG_NAME, "option")
            matched = False
            for option in options:
                if target_text in option.text:
                    option.click()
                    print(f"DEBUG: '{option.text}' 옵션 선택 완료.")
                    matched = True
                    break

            if not matched:
                print(f"ERROR: '{target_text}' 텍스트가 포함된 옵션을 찾을 수 없습니다.")
                return False

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: 19004 처리 중 예외 발생: {e}")
            return False



    # ✅ 29184 전용 할인 처리
    if park_id == 29184:
        ticket_map = {
            "평일 당일권": "평일당일권(공유)",
            "심야권": "야간권(공유)",
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: 29184에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_text = ticket_map[ticket_name]

        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )
            options = select_element.find_elements(By.TAG_NAME, "option")
            matched = False
            for option in options:
                if target_text in option.text:
                    option.click()
                    print(f"DEBUG: '{option.text}' 옵션 선택 완료.")
                    matched = True
                    break

            if not matched:
                print(f"ERROR: '{target_text}' 텍스트가 포함된 옵션을 찾을 수 없습니다.")
                return False

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: 29184 처리 중 예외 발생: {e}")
            return False


    # ✅ 19860 전용 할인 처리
    if park_id == 19860:
        ticket_map = {
            "평일 당일권(월, 지하 2층 전용)": "종일권(공유서비스)",
            "평일 당일권(지하 2층 전용)": "종일권(공유서비스)",
            "평일 당일권(화, 지하 2층 전용)": "종일권(공유서비스)",
            "평일 당일권(수, 지하 2층 전용)": "종일권(공유서비스)",
            "평일 당일권(목, 지하 2층 전용)": "종일권(공유서비스)",
            "평일 당일권(금, 지하 2층 전용)": "종일권(공유서비스)",
            "휴일 당일권(지하 2층 전용,토)": "종일권(공유서비스)",
            "휴일 당일권(지하 2층 전용,일)": "종일권(공유서비스)",
            "평일 오후권(지하 2층 전용)": "평일오후권(공유서비스)",
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: 19860에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_text = ticket_map[ticket_name]

        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )
            options = select_element.find_elements(By.TAG_NAME, "option")
            matched = False
            for option in options:
                if target_text in option.text:
                    option.click()
                    print(f"DEBUG: '{option.text}' 옵션 선택 완료.")
                    matched = True
                    break

            if not matched:
                print(f"ERROR: '{target_text}' 텍스트가 포함된 옵션을 찾을 수 없습니다.")
                return False

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: 19860 처리 중 예외 발생: {e}")
            return False

        # ✅ 19271 하이파킹 강남빌딩 전용 할인 처리
    if park_id == 19271:
            ticket_map = {
                '야간권(금,토)': "231168",  # HTML: 야간권(공유서비스)
                '평일 야간권(일~목)': "231168",  # HTML: 야간권(공유서비스)
                '휴일 당일권': "249245"  # HTML: 주말권(공유서비스)
            }

            if ticket_name not in ticket_map:
                print(f"ERROR: 19271에서 지원하지 않는 ticket_name: {ticket_name}")
                return False

            target_value = ticket_map[ticket_name]

            try:
                # <select> 요소를 찾습니다.
                select_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "selectDiscount"))
                )

                # Select 객체를 생성하고 value로 옵션을 선택합니다.
                select = Select(select_element)
                select.select_by_value(target_value)
                print(f"DEBUG: park_id 19271: value '{target_value}' (티켓: {ticket_name}) 할인권 선택 완료.")

                # '할인 적용' 버튼 클릭
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "discountSubmit"))
                ).click()
                print("DEBUG: 할인 적용 버튼 클릭 완료.")

                # 알림창 처리
                try:
                    WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                    print("DEBUG: 알림창 확인 완료.")
                except TimeoutException:
                    print("DEBUG: 알림창 없음.")

                return True

            except Exception as e:
                print(f"ERROR: 19271 처리 중 예외 발생: {e}")
                return False


    # ✅ 19148 전용 할인 처리 (29136 스타일로 수정)
    if park_id == 19148:
        ticket_map = {
            "평일 당일권": "25009",  # 평일종일권_(ONLINE)
            "평일 당일권(월)": "25009",  # 평일종일권_(ONLINE)
            "평일 당일권(화)": "25009",
            "평일 당일권(수)": "25009",
            "평일 당일권(목)": "25009",
            "평일 당일권(금)": "25009",
            "휴일 야간권": "345516",  # 휴일야간권(공유서비스)
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: 19148에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_value = ticket_map[ticket_name]

        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )
            select = Select(select_element)
            select.select_by_value(target_value)
            print(f"DEBUG: value '{target_value}' 할인권 선택 완료.")

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: 19148 처리 중 예외 발생: {e}")
            return False

    # ✅ 29136 전용 할인 처리
    if park_id == 29136:
        ticket_map = {
            # 종일권(공유서비스)
            "평일 당일권": "종일권(공유서비스)",
            "평일 당일권(월)": "종일권(공유서비스)",
            "평일 당일권(화)": "종일권(공유서비스)",
            "평일 당일권(수)": "종일권(공유서비스)",
            "평일 당일권(목)": "종일권(공유서비스)",
            "평일 당일권(금)": "종일권(공유서비스)",

            # 3시간권(공유서비스)
            "평일 3시간권(월~금)": "3시간권(공유서비스)",
            "휴일 3시간권": "3시간권(공유서비스)",

            # 주말권(공유서비스)
            "휴일 당일권(토~일)": "주말권(공유서비스)",

            # 야간권(공유서비스)
            "야간권(월~금,일)": "야간권(공유서비스)",
            "휴일 야간권(토)": "야간권(공유서비스)",
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: 29136에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_text = ticket_map[ticket_name]

        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )
            options = select_element.find_elements(By.TAG_NAME, "option")
            matched = False
            for option in options:
                if target_text in option.text:
                    option.click()
                    print(f"DEBUG: '{option.text}' 옵션 선택 완료.")
                    matched = True
                    break

            if not matched:
                print(f"ERROR: '{target_text}' 텍스트가 포함된 옵션을 찾을 수 없습니다.")
                return False

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: 29136 처리 중 예외 발생: {e}")
            return False


    # ✅ 19810 전용 할인 처리
    if park_id == 19810:
        ticket_map = {
            "평일 당일권": "종일권(공유서비스)",
            "휴일 당일권": "종일권(공유서비스)",
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: 19810에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_text = ticket_map[ticket_name]

        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )
            options = select_element.find_elements(By.TAG_NAME, "option")
            matched = False
            for option in options:
                if target_text in option.text:
                    option.click()
                    print(f"DEBUG: '{option.text}' 옵션 선택 완료.")
                    matched = True
                    break

            if not matched:
                print(f"ERROR: '{target_text}' 텍스트가 포함된 옵션을 찾을 수 없습니다.")
                return False

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: 19810 처리 중 예외 발생: {e}")
            return False


    # ✅ 19600 전용 할인 처리
    if park_id == 19600:
        ticket_map = {
            "평일 당일권": "평일당일권(공유서비스)",
            "평일 당일권(월)": "평일당일권(공유서비스)",
            "평일 당일권(화)": "평일당일권(공유서비스)",
            "평일 당일권(수)": "평일당일권(공유서비스)",
            "평일 당일권(목)": "평일당일권(공유서비스)",
            "평일 당일권(금)": "평일당일권(공유서비스)",
            "평일 3시간권": "평일3시간권(공유서비스)",
            "평일 5시간권": "평일5시간권(공유서비스)",
            "평일 12시간권": "평일12시간권(공유서비스)",
            "휴일 3시간권": "휴일3시간권(공유서비스)",
            "휴일 12시간권": "휴일12시간권(공유서비스)",
            "평일 심야권": "평일심야권(공유서비스)",
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: 19600에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_text = ticket_map[ticket_name]

        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )
            options = select_element.find_elements(By.TAG_NAME, "option")
            matched = False
            for option in options:
                if target_text in option.text:
                    option.click()
                    print(f"DEBUG: '{option.text}' 옵션 선택 완료.")
                    matched = True
                    break

            if not matched:
                print(f"ERROR: '{target_text}' 텍스트가 포함된 옵션을 찾을 수 없습니다.")
                return False

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: 19600 처리 중 예외 발생: {e}")
            return False

    print(f"ERROR: handle_ticket에서 처리되지 않은 park_id: {park_id}")
    return False



def web_har_in(target, driver, lotName):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]
    park_type = ParkType.get_park_type(park_id)

    trim_car_num = Util.all_trim(ori_car_num)
    search_id = trim_car_num[-4:]

    print("parkId = " + str(park_id) + ", " + "searchId = " + search_id)
    print(Colors.BLUE + ticket_name + Colors.ENDC)

    if ParkUtil.is_park_in(park_id):
        if park_id in mapIdToWebInfo:
            login_url = ParkUtil.get_park_url(park_id)
            driver.implicitly_wait(3)
            driver.get(login_url)

            web_info = mapIdToWebInfo[park_id]

            # todo 현재 URL을 가지고와서 비교 후 자동로그인
            # print(driver.current_url)
            # 재접속이 아닐 때, 그러니까 처음 접속할 때


            if ParkUtil.first_access(park_id, driver.current_url):

                driver.find_element(By.ID, web_info[WebInfo.inputId]).send_keys(AJ_PARK_ID)
                driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(AJ_PARK_PW)
                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()
                print("로그인버튼  ")

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "webdiscount"))
            ).click()
            driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
            driver.find_element_by_id('searchSubmitByDate').click()

            # 차량 검색 결과가 로딩될 때까지 대기 (예: 결과 내 첫 <dl> 등장 대기)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//section/div/section/div[1]/div/dl"))
                )
                print("DEBUG: 차량 검색 결과 로딩 완료.")
            except TimeoutException:
                print("ERROR: 차량 검색 결과가 로딩되지 않았습니다.")
                return False

            count = len(driver.find_elements(By.XPATH, "/html/body/div[1]/section/div/section/div"))
            for index in range(1, count + 1):
                sale_table = driver.find_element_by_xpath("/html/body/div[1]/section/div/section/div[" + str(index) + "]")
                searched_car_number = driver.find_element_by_xpath(
                     "/html/body/div[1]/section/div/section/div[" + str(index) + "]/div/dl[1]/dd").text
                print("나누기전 : " + searched_car_number)
                td_car_num_1 = re.sub('<.+?>', '', searched_car_number, 0, re.I | re.S)
                td_car_num_2 = td_car_num_1.strip()
                td_car_num_3 = td_car_num_2.split('\n')

                global td_car_num
                if len(td_car_num_3[0].split(' ')) > 1:
                    td_car_num = td_car_num_3[0].split(' ')[0][-7:]
                else:
                    td_car_num = td_car_num_3[0][-7:]

                print("검색된 차량번호 : " + td_car_num + " == " + "기존 차량번호 : " + ori_car_num + " / " + ori_car_num[-7:])

                if ori_car_num[-7:] == td_car_num or ori_car_num == td_car_num:
                    driver.find_element(By.XPATH, f"/html/body/div[1]/section/div/section/div[{index}]").find_element(By.CLASS_NAME, "selectCarInfo").click()

                    # ✅ 19004, 19600은 handle_ticket() 함수로 별도 처리
                    if park_id in [19004, 19600, 19860, 29184, 29136,19148,19156, 19271, 19862, 19540, 19534]:
                        return handle_ticket(driver, park_id, ticket_name)

                    select = Select(driver.find_element_by_id('selectDiscount'))
                    select.select_by_index(get_har_in_script(park_id, ticket_name))
                    Util.sleep(2)
                    aj_ticket_info = select.first_selected_option.text
                    print(Colors.BLUE + aj_ticket_info + Colors.ENDC)
                    aj_ticket_cnt_txt = aj_ticket_info[-6:]
                    aj_ticket_cnt = int(re.findall('[0-9]+', aj_ticket_cnt_txt)[0])

                    if aj_ticket_cnt == 1 or aj_ticket_cnt == 2:
                        sendmail_ajCount0(str(lotName) + " 지점 " + ticket_name + " 할인권 구매부탁드립니다.")
                        print(Colors.RED + "주차권이 부족합니다." + Colors.ENDC)
                        driver.implicitly_wait(3)
                        driver.find_element_by_id('discountSubmit').click()
                        driver.implicitly_wait(2)
                        driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/button[2]').click()

                        return True
                    try:
                        if aj_ticket_cnt < 1:  # 주차권이 0매인 경우
                            sendmail_ajCount0(str(lotName) + " 지점 " + ticket_name + " 할인권 구매부탁드립니다.")
                            print(Colors.RED + "주차권이 부족합니다." + Colors.ENDC)
                            return False

                        else:  # 주차권이 부족하지 않을 때
                            driver.implicitly_wait(3)
                            driver.find_element_by_id('discountSubmit').click()
                            driver.implicitly_wait(2)
                            driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/button[2]').click()
                            return True
                    except ValueError as ex:
                        print(Colors.RED + "잘못된 주차권 갯수입니다. : " + ex + Colors.ENDC)
                        return False

                else:
                    print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)
                    continue
                return False
            return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False


def sendmail_ajCount0(text):
    sendEmail = "email@wisemobile.co.kr"
    recvEmail = "email@wisemobile.co.kr"
    password = "password"

    smtpName = "smtp.worksmobile.com"  # smtp 서버 주소
    smtpPort = 587  # smtp 포트 번호

    msg = MIMEText(text)  # MIMEText(text , _charset = "utf8")

    msg['Subject'] = "  AJ파크 주차권 구매사항   "
    msg['From'] = sendEmail
    msg['To'] = recvEmail
    print(msg.as_string())

    s = smtplib.SMTP(smtpName, smtpPort)  # 메일 서버 연결
    s.starttls()  # TLS 보안 처리
    s.login(sendEmail, password)  # 로그인
    s.sendmail(sendEmail, recvEmail, msg.as_string())  # 메일 전송, 문자열로 변환하여 보냅니다.
    s.quit()  # smtp 서버 연결을 종료합니다.