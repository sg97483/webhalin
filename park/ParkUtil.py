# -*- coding: utf-8 -*-
import datetime
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from agency import Gs
from park import ParkType, Parks
import re
import Colors
import time

from park.ParkType import AMANO

connParkId = []


def is_park_in(park_id):

    if park_id in Parks.mapIdToUrl:
        return True
    else:
        return False


def get_park_url(park_id):
    return Parks.mapIdToUrl[park_id]


def get_park_lot_option(park_id):
    return Parks.lotOptionList[park_id]


def get_park_discount_url(park_type):
    return ParkType.mapToHarinUrl[park_type]


def check_first_conn(park_id):
    if park_id in connParkId:
        return False
    else:
        connParkId.append(park_id)
        return True


def first_access(park_id, current_url):
    harin_url = ParkType.mapToHarinUrl[ParkType.get_park_type(park_id)]

    if park_id in ParkType.parkTypeNoRequestMain:
        # 첫 연결이면
        if check_first_conn(park_id):
            return True
        else:
            return False

    if str(current_url).endswith(harin_url):
        return False
    else:
        return True


def get_park_search_css(park_id):

    if park_id == 19492:
        return "#tbData > tbody > tr"

    park_type = ParkType.get_park_type(park_id)


    park_search_css = ParkType.type_to_search_css[park_type]


    return park_search_css


check_searched_car_number_self = [
    Parks.ORAKAI_DAEHAKRO,
    18973
]


def get_park_css(park_id):
    park_type = ParkType.get_park_type(park_id)

    if park_id in check_searched_car_number_self:
        park_css = ParkType.mapToAgency[park_id]
    else:
        park_css = ParkType.mapToAgency[park_type]

    return park_css


def check_search(park_id, driver):
    print(Colors.GREEN + "체크 서치1" + Colors.ENDC)
    try:
        print(Colors.GREEN + "체크 서치2" + Colors.ENDC)

        # TURU 을지트윈타워 전용 처리
        if park_id == 19174:
            possible_ids = [
                "BTN_공유서비스 종일",
                "BTN_공유서비스 주말",
                "BTN_공유서비스 야간",
                "BTN_12시간권_O2O",
                "BTN_공유서비스 (3시간)"
            ]
            for btn_id in possible_ids:
                if driver.find_elements(By.ID, btn_id):
                    print(Colors.GREEN + f"✅ 차량 검색 성공 (버튼 {btn_id} 존재 확인됨)" + Colors.ENDC)
                    return True
            print(Colors.YELLOW + "❌ 차량 검색 결과 없음 (버튼 없음)" + Colors.ENDC)
            return False

        # AMANO인 경우 별도 처리
        if ParkType.get_park_type(park_id) == AMANO:
            print("AMANO 타입 주차장 처리 중...")
            try:
                modal_text_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#modal-window > div > div > div.modal-text"))
                )
                modal_text = modal_text_element.text.strip()
                print(f"DEBUG: modal_text = {modal_text}")

                if "미입차" in modal_text or "차량 정보 없음" in modal_text:
                    print(Colors.YELLOW + "미입차 상태로 확인됨." + Colors.ENDC)
                    Gs.log_out_web(driver)
                    return False
                else:
                    print(Colors.GREEN + "AMANO 타입에서 차량 정보 확인됨." + Colors.ENDC)
                    return True
            except TimeoutException:
                print("ERROR: AMANO 팝업 로드 시간 초과.")
                return False
            except Exception as e:
                print(f"ERROR: AMANO 처리 중 오류 발생: {e}")
                return False

        # check_search() 내에 추가
        if park_id == 16159:
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//td[h3[contains(text(), '차량 정보')]]"))
                )
                if "차량번호:" in element.text:
                    print(Colors.GREEN + "✅ 차량 검색 성공 (16159)" + Colors.ENDC)
                    return True
                else:
                    print(Colors.YELLOW + "❌ 차량 정보 없음 (16159)" + Colors.ENDC)
                    return False
            except TimeoutException:
                print("ERROR: 16159 차량 정보 영역 로딩 시간 초과")
                return False

        # 기본 CSS Selector 기반 검색
        park_search_css = get_park_search_css(park_id)
        print(f"DEBUG: park_search_css = {park_search_css}")

        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, park_search_css))
        )
        tr_text = element.text
        print(f"DEBUG: tr_text = {tr_text}")

        text = re.sub('<.+?>', '', tr_text, 0, re.I | re.S)
        trim_text = text.strip()

        if trim_text.startswith("검색") or trim_text.startswith("입차") or trim_text.startswith("차량"):
            print(Colors.YELLOW + "미입차" + Colors.ENDC)
            Gs.log_out_web(driver)
            return False
        else:
            return True
    except NoSuchElementException:
        print(Colors.GREEN + "체크 서치3" + Colors.ENDC)
        print(Colors.GREEN + "ERROR: 해당 엘리먼트가 존재하지 않습니다." + Colors.ENDC)
        return False
    except TimeoutException:
        print("ERROR: 요소 로드가 시간 초과로 실패했습니다.")
        return False
    except Exception as e:
        print(f"ERROR: check_search 처리 중 예기치 않은 오류 발생: {e}")
        return False



def check_same_car_num(parkId, oriCarNum, driver):
    """
    차량번호 비교 (앞자리 한 자리 차이도 인정)
    - 예: '195서1916' == '95서1916' 도 True
    """

    # 🎯 19174 전용 처리
    if parkId == 19174:
        try:
            info_td = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//td[h3[contains(text(), '차량 정보')]]"))
            )
            text = info_td.text.strip()  # 전체 텍스트
            print(f"DEBUG: 차량 정보 영역 텍스트:\n{text}")

            # 차량번호 줄 찾기
            for line in text.splitlines():
                if "차량번호:" in line:
                    site_car_num = line.split("차량번호:")[1].strip()
                    print(f"DEBUG: 사이트 표시 차량번호: {site_car_num}")

                    ori_last7 = oriCarNum[-7:]
                    site_last7 = site_car_num[-7:]

                    if oriCarNum == site_car_num:
                        print(Colors.GREEN + "차량번호 정확 일치 (19174)" + Colors.ENDC)
                        return True
                    if ori_last7 == site_last7:
                        print(Colors.GREEN + "차량번호 7자리 일치 (19174)" + Colors.ENDC)
                        return True
                    if ori_last7[1:] == site_last7[1:]:
                        print(Colors.GREEN + "앞자리 제외 일치 (19174)" + Colors.ENDC)
                        return True

                    print(Colors.MARGENTA + f"차량번호가 일치하지 않습니다. (19174, 찾은 번호: {site_car_num})" + Colors.ENDC)
                    return False

            print(Colors.RED + "차량번호 텍스트 줄을 찾을 수 없습니다. (19174)" + Colors.ENDC)
            return False

        except Exception as e:
            print(Colors.RED + f"ERROR: 차량번호 확인 중 오류 발생 (19174): {e}" + Colors.ENDC)
            return False


    elif parkId == 19492:
        try:
            td = driver.find_element(By.CSS_SELECTOR, "#tbData > tbody > tr > td:nth-child(3)")
            full_text = td.get_attribute("innerText").strip()
            car_num_line = full_text.split("\n")[0].strip()  # "35가7062"만 추출
            print(f"DEBUG: 추출된 차량번호: {car_num_line}")

            ori_last7 = oriCarNum[-7:]
            site_last7 = car_num_line[-7:]

            if oriCarNum == car_num_line:
                print(Colors.GREEN + "차량번호 정확 일치 (19492)" + Colors.ENDC)
                return True
            if ori_last7 == site_last7:
                print(Colors.GREEN + "차량번호 7자리 일치 (19492)" + Colors.ENDC)
                return True
            if ori_last7[1:] == site_last7[1:]:
                print(Colors.GREEN + "앞자리 제외 일치 (19492)" + Colors.ENDC)
                return True

            print(Colors.MARGENTA + f"차량번호 불일치 (사이트: {car_num_line})" + Colors.ENDC)
            return False
        except Exception as e:
            print(Colors.RED + f"ERROR: 차량번호 추출 실패 (19492): {e}" + Colors.ENDC)
            return False


    elif parkId == 16159:
        try:
            info_td = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//td[h3[contains(text(), '차량 정보')]]"))
            )
            text = info_td.text.strip()
            print(f"DEBUG: 차량 정보 영역 텍스트:\n{text}")

            for line in text.splitlines():
                if "차량번호:" in line:
                    site_car_num = line.split("차량번호:")[1].strip()
                    print(f"DEBUG: 사이트 표시 차량번호: {site_car_num}")

                    ori_last7 = oriCarNum[-7:]
                    site_last7 = site_car_num[-7:]

                    if oriCarNum == site_car_num:
                        print(Colors.GREEN + "차량번호 정확 일치 (16159)" + Colors.ENDC)
                        return True
                    if ori_last7 == site_last7:
                        print(Colors.GREEN + "차량번호 7자리 일치 (16159)" + Colors.ENDC)
                        return True
                    if ori_last7[1:] == site_last7[1:]:
                        print(Colors.GREEN + "앞자리 제외 일치 (16159)" + Colors.ENDC)
                        return True

                    print(Colors.MARGENTA + f"차량번호 불일치 (16159, 찾은 번호: {site_car_num})" + Colors.ENDC)
                    return False

            print(Colors.RED + "차량번호 줄을 찾을 수 없습니다. (16159)" + Colors.ENDC)
            return False

        except Exception as e:
            print(Colors.RED + f"ERROR: 차량번호 확인 중 오류 발생 (16159): {e}" + Colors.ENDC)
            return False

    # ✅ 일반 케이스 (기존 로직)
    element_car_num = get_park_css(parkId)

    if element_car_num == "":
        print(Colors.YELLOW + "엘리멘트 카넘버" + Colors.ENDC)
        print(Colors.YELLOW + "해당 엘리멘트가 존재하지 않습니다." + Colors.ENDC)
        return False

    try:
        hidden_inputs = driver.find_elements_by_css_selector("input[type='hidden']")
        matched_car_number = None

        for input_elem in hidden_inputs:
            value = input_elem.get_attribute('value')
            car_number = value.split('|')[0].strip()
            matched_car_number = car_number

            ori_last7 = oriCarNum[-7:]
            site_last7 = car_number[-7:]

            print(f"사이트 차량번호: {car_number}, 비교 대상 차량번호: {oriCarNum}")

            if oriCarNum == car_number:
                print(Colors.GREEN + "차량번호 정확 일치" + Colors.ENDC)
                return True
            if ori_last7 == site_last7:
                print(Colors.GREEN + "차량번호 7자리 일치" + Colors.ENDC)
                return True
            if ori_last7[1:] == site_last7[1:]:
                print(Colors.GREEN + "앞자리 제외 일치 (예: 195서1916 == 95서1916)" + Colors.ENDC)
                return True

        print(Colors.MARGENTA + f"차량번호가 일치하지 않습니다. (마지막 확인된 번호: {matched_car_number})" + Colors.ENDC)
        return False

    except Exception as e:
        print(Colors.RED + f"ERROR: 차량번호 가져오기 실패: {e}" + Colors.ENDC)
        return False





def check_same_car_num_origin(parkId, oriCarNum, driver):
    element_car_num = get_park_css(parkId)



    # park_type = ParkType.get_park_type(parkId)
    #
    # if parkId == Parks.T_TOWER or parkId == Parks.PODO_MALL:
    #     element_car_num = ParkType.mapToAgency[parkId]
    # else:
    #     element_car_num = ParkType.mapToAgency[park_type]
    #     # print(element_car_num)
    # print("차량번호 길이 : " + str(len(oriCarNum)))
    # print("차량번호 길이 -7 : " + str((oriCarNum[-7:])))
    # print("차량번호 길이 -8 : " + str((oriCarNum[-8:])))

    if element_car_num == "":
        print(Colors.YELLOW + "엘리멘트 카넘버" + Colors.ENDC)
        print(Colors.YELLOW + "해당 엘리멘트가 존재하지 않습니다." + Colors.ENDC)
        return False
    else:
        td_car_num_0 = driver.find_element_by_css_selector(element_car_num).text
        print("나누기전 : " + td_car_num_0)
        td_car_num_1 = re.sub('<.+?>', '', td_car_num_0, 0, re.I | re.S)
        td_car_num_2 = td_car_num_1.strip()
        td_car_num_3 = td_car_num_2.split('\n')
        global td_car_num
        if(len(td_car_num_3[0].split(' '))>1):
            td_car_num = td_car_num_3[0].split(' ')[0][-7:]
        else:
            td_car_num = td_car_num_3[0][-7:]

        # Remove whitespaces from oriCarNum
        oriCarNum = oriCarNum.strip()

        print("검색된 차량번호 : " + td_car_num + " == " + "기존 차량번호 : " + oriCarNum + " / " + oriCarNum[-7:])
        # if len(oriCarNum) == 8:
        #     if oriCarNum[-8:] == td_car_num:
        #         return True
        #     else:
        #         print(Colors.MARGENTA + "차량번호가 틀립니다.1" + Colors.ENDC)
        #         return False
        # if len(oriCarNum) == 7:
        if oriCarNum[-7:] == td_car_num:
                return True
        else:
                print(Colors.MARGENTA + "차량번호가 틀립니다. 이건가" + Colors.ENDC)
                return False


def is_night_time():
    f_seconds = time.time()
    s_time = int(f_seconds % 60)
    f_seconds //= 60
    m_time = f_seconds % 60
    f_seconds //= 60
    h_time = f_seconds % 24
    h_time = (h_time + 9) % 24
    print(h_time, " 시", m_time, " 분", s_time, " 초")

    if h_time >= 18:
        return True
    else:
        return False


def get_type_to_day_css(park_id):
    park_type = ParkType.get_park_type(park_id)
    return ParkType.type_to_day_css[park_type]


def check_same_day(parkId, driver):
    day_css = get_type_to_day_css(parkId)

    if day_css == "":
        print(Colors.YELLOW + "day_css해당 엘리멘트가 존재하지 않습니다." + Colors.ENDC)
        return False
    else:
        text_0 = driver.find_element_by_css_selector(day_css).text
        text_1 = re.sub('<.+?>', '', text_0, 0, re.I | re.S)
        text_2 = text_1.strip()
        text_3 = text_2.split('\n')
        text = text_3[0]

        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d')
        print("검색된 입차날짜 : " + text + " == " + "현재 입차날짜 : " + now_date)

        if text.startswith(now_date):
            return True
        else:
            print(Colors.MARGENTA + "입차날짜가 틀립니다." + Colors.ENDC)
            return False


def timeCheck(nowTime, targetTime):
    now = int(nowTime[0:2])*60 + int(nowTime[2:4])
    target = int(targetTime[0:2])*60 + int(targetTime[2:4])
    if(now>target):
        return True
    else:
        return False