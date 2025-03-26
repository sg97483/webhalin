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

        # AMANO인 경우 별도 처리
        if ParkType.get_park_type(park_id) == AMANO:
            print("AMANO 타입 주차장 처리 중...")
            try:
                # 팝업 메시지를 확인하거나 별도의 처리
                modal_text_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#modal-window > div > div > div.modal-text"))
                )
                modal_text = modal_text_element.text.strip()
                print(f"DEBUG: modal_text = {modal_text}")

                # 텍스트 조건에 따라 처리
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

        # AMANO가 아닌 경우 기존 CSS Selector 방식
        park_search_css = get_park_search_css(park_id)
        print(f"DEBUG: park_search_css = {park_search_css}")

        # 요소 대기
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, park_search_css))
        )
        tr_text = element.text  # 서치된 텍스트
        print(f"DEBUG: tr_text = {tr_text}")

        # 텍스트 정제
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

    element_car_num = get_park_css(parkId)

    if element_car_num == "":
        print(Colors.YELLOW + "엘리멘트 카넘버" + Colors.ENDC)
        print(Colors.YELLOW + "해당 엘리멘트가 존재하지 않습니다." + Colors.ENDC)
        return False

    try:
        # ✅ 1. input hidden value로 가져오기
        hidden_inputs = driver.find_elements_by_css_selector("input[type='hidden']")

        matched_car_number = None  # 찾은 차량번호 초기화

        for input_elem in hidden_inputs:
            value = input_elem.get_attribute('value')  # ex) '195서1916|19'
            car_number = value.split('|')[0].strip()  # 차량번호만 추출

            # 비교용으로 추출
            matched_car_number = car_number

            # 비교 로직
            ori_car_num_last7 = oriCarNum[-7:]  # '95서1916'
            car_number_last7 = car_number[-7:]  # '95서1916' (from site)

            print(f"사이트 차량번호: {car_number}, 비교 대상 차량번호: {oriCarNum}")

            # 1. 정확히 일치
            if oriCarNum == car_number:
                print(Colors.GREEN + "차량번호 정확 일치" + Colors.ENDC)
                return True

            # 2. 7자리 비교
            if ori_car_num_last7 == car_number_last7:
                print(Colors.GREEN + "차량번호 7자리 일치" + Colors.ENDC)
                return True

            # 3. 앞 한자리 제외 후 비교 (예: 195서1916 vs 95서1916)
            if ori_car_num_last7[1:] == car_number_last7[1:]:
                print(Colors.GREEN + "앞자리 제외 일치 (예: 195서1916 == 95서1916)" + Colors.ENDC)
                return True

        # 만약 하나도 일치하지 않으면
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