# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoSuchElementException

import Util
import Colors
from park import ParkUtil, ParkType
import WebInfo

mapIdToWebInfo = {
    # IP TIME 이대 APM
    18959: ["TextBox_ID", "TextBox_Pwd", "//*[@id='Button_Login']",
            "TextBox_CarNum", "//*[@id='Button_Search']",
            "#DataGrid1 > tbody > tr:nth-child(2) > td:nth-child(3) > a"
            ],
    # (하이파킹)삼성 서울의료원 강남분원
    18963: ["TextBox_ID", "TextBox_Pwd", "//*[@id='Button_Login']",
            "TextBox_CarNum", "//*[@id='Button_Search']",
            "#DataGrid1 > tbody > tr:nth-child(2) > td:nth-child(3) > a"
            ],
    # (하이파킹)서울역 서울스퀘어
    12903: ["TextBox_ID", "TextBox_Pwd", "//*[@id='Button_Login']",
            "TextBox_CarNum", "//*[@id='Button_Search']",
            "#DataGrid1 > tbody > tr:nth-child(2) > td:nth-child(3) > a"
            ],
    # (하이파킹) V-PLEX
    18964: ["TextBox_ID", "TextBox_Pwd", "//*[@id='Button_Login']",
            "TextBox_CarNum", "//*[@id='Button_Search']",
            "#DataGrid1 > tbody > tr:nth-child(2) > td:nth-child(3) > a"
            ]
}


def get_har_in_script(park_id, ticket_name):
    return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]
    # if Util.get_week_or_weekend() == 0:
    #     return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]
    # else:
    #     return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]


def web_har_in(target, driver):
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
            web_har_in_info = ParkUtil.get_park_lot_option(park_id)
            # todo 현재 URL을 가지고와서 비교 후 자동로그인
            # print(driver.current_url)
            # 재접속이 아닐 때, 그러니까 처음 접속할 때
            if ParkUtil.first_access(park_id, driver.current_url):

                driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
                driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])

                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()

                driver.implicitly_wait(3)

                driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
                Util.sleep(3)

                driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()

                Util.sleep(1)

                if ParkUtil.check_search(park_id, driver):
                    try:
                        if ParkUtil.check_same_day(park_id, driver):
                            if ParkUtil.check_same_car_num(park_id, ori_car_num, driver):
                                driver.find_element_by_css_selector(web_info[WebInfo.btnItem]).click()
                                driver.find_element_by_id("Button_Discount").click()
                                Util.sleep(1)
                                driver.find_element_by_id("Button_Discount").click()
                                Util.sleep(1)
                                return True
                            else:
                                print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)
                                return False
                        else:
                            print(Colors.MARGENTA + "입차날짜가 틀립니다." + Colors.ENDC)
                            return False

                    except NoSuchElementException as ex:
                        print(Colors.BLUE + "검색결과가 없습니다." + Colors.ENDC)
                        print('에러가 발생 했습니다', ex)  # ex는 발생한 에러의 이름을 받아오는 변수
                        return False

                return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
