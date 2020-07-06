# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoSuchElementException

import Parks
import ParkType
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

    return park_search_css


check_searched_car_number_self = [
    Parks.T_TOWER,
    Parks.PODO_MALL,
    Parks.ORAKAI_DAEHAKRO
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

        tr_text = driver.find_element_by_css_selector(park_search_css).text
        text = re.sub('<.+?>', '', tr_text, 0, re.I | re.S)
        trim_text = text.strip()
        # print(trim_text)
        if trim_text.startswith("검색") or trim_text.startswith("입차") or trim_text.startswith("차량"):
            print(Colors.YELLOW + "미입차" + Colors.ENDC)
            return False
        else:
            return True
    except NoSuchElementException:
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

    if element_car_num == "":
        print(Colors.YELLOW + "해당 엘리멘트가 존재하지 않습니다." + Colors.ENDC)
        return False
    else:
        td_car_num_0 = driver.find_element_by_css_selector(element_car_num).text
        td_car_num_1 = re.sub('<.+?>', '', td_car_num_0, 0, re.I | re.S)
        td_car_num_2 = td_car_num_1.strip()
        td_car_num_3 = td_car_num_2.split('\n')
        td_car_num = td_car_num_3[0][-7:]

        print("검색된 차량번호 : " + td_car_num + " == " + "기존 차량번호 : " + oriCarNum + " / " + oriCarNum[-7:])

        if oriCarNum[-7:] == td_car_num:
            return True
        else:
            print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)
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
