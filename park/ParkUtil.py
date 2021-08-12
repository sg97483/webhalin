# -*- coding: utf-8 -*-
import datetime

from selenium.common.exceptions import NoSuchElementException

from agency import Gs
from park import ParkType, Parks
import re
import Colors
import time

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
   # if park_id != 19415 : park_search_css = ParkType.type_to_search_css[park_type]
   # elif park_id == 19415 : park_search_css = "#divAjaxCarList > tr"


    return park_search_css


check_searched_car_number_self = [
    Parks.T_TOWER,
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
    try:
        park_search_css = get_park_search_css(park_id)

        tr_text = driver.find_element_by_css_selector(park_search_css).text #서치된 텍스트
        print(Colors.GREEN + tr_text + Colors.ENDC)
        text = re.sub('<.+?>', '', tr_text, 0, re.I | re.S)

        trim_text = text.strip()

        # print(trim_text)
        if trim_text.startswith("검색") or trim_text.startswith("입차") or trim_text.startswith("차량"):
            print(Colors.YELLOW + "미입차" + Colors.ENDC)
            Gs.log_out_web(driver)
            return False
        else:
            return True
    except NoSuchElementException:
        print(Colors.GREEN + "체크 서치" + Colors.ENDC)
        print(Colors.GREEN + "해당 엘리멘트가 존재하지 않습니다." + Colors.ENDC)
        return True


def check_same_car_num(parkId, oriCarNum, driver):
    element_car_num = get_park_css(parkId)

    # park_type = ParkType.get_park_type(parkId)
    #
    # if parkId == Parks.T_TOWER or parkId == Parks.PODO_MALL:
    #     element_car_num = ParkType.mapToAgency[parkId]
    # else:
    #     element_car_num = ParkType.mapToAgency[park_type]
    #     # print(element_car_num)
    print("차량번호 길이 : " + str(len(oriCarNum)))
    print("차량번호 길이 -7 : " + str((oriCarNum[-7:])))
    print("차량번호 길이 -8 : " + str((oriCarNum[-8:])))

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

        print("검색된 차량번호 : " + td_car_num + " == " + "기존 차량번호 : " + oriCarNum + " / " + oriCarNum[-7:])
        if len(oriCarNum) == 8:
            if oriCarNum[-8:] == td_car_num:
                return True
            else:
                print(Colors.MARGENTA + "차량번호가 틀립니다.1" + Colors.ENDC)
                return False
        elif len(oriCarNum) == 7:
            if oriCarNum[-7:] == td_car_num:
                return True
            else:
                print(Colors.MARGENTA + "차량번호가 틀립니다.2" + Colors.ENDC)
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
        print(Colors.YELLOW + "해당 엘리멘트가 존재하지 않습니다." + Colors.ENDC)
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


def check_nice_date(parkId, create_date, driver):
    if parkId == Parks.NICE_HONG_MUN_KWAN:
        date_xpath = "//*[@id='entryDate']"
        text_0 = driver.find_element_by_xpath(date_xpath).text
        text_1 = re.sub('<.+?>', '', text_0, 0, re.I | re.S)
        date_time_in_car_time = datetime.datetime.strptime(text_1, '%Y-%m-%d %H:%M:%S')

        if create_date <= date_time_in_car_time:
            print("입차 전 결제입니다. / createDate : " + str(create_date) + " / inCarTime : " + text_1)
            return True
        else:
            print("입차 후 결제입니다. / createDate : " + str(create_date) + " / inCarTime : " + text_1)
            return False

def timeCheck(nowTime, targetTime):
    now = int(nowTime[0:2])*60 + int(nowTime[2:4])
    target = int(targetTime[0:2])*60 + int(targetTime[2:4])
    if(now>target):
        return True
    else:
        return False