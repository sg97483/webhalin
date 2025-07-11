# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoSuchElementException

import Util
import Colors
from park import ParkUtil, ParkType, Parks
import WebInfo

mapIdToWebInfo = {
    # 2형태 경복궁 BLUE
    4588: ["login_id", "login_pw", "/html/body/div/div/form/center/button[1]",
           "carNumber", "/html/body/div[2]/ul/li/button",
           "",
           "chk_info1",
           "chk_info1",
           ""],
    # 동화빌딩
    19082: ["login_id", "login_pw", "/html/body/div/div/form/center/button[1]",
            "carNumber", "/html/body/div[2]/ul/li/button",
            "",
            "chk_info1",
            "chk_info1"
            ],
    # 키움 나대지
    19063: ["login_id", "login_pw", "/html/body/div/div/form/center/button[1]",
            "carNumber", "/html/body/div[2]/ul/li/button",
            "",
            "chk_info1",
            "chk_info1"

            ],
    # 삼성화재서비스빌딩
    19048: ["login_id", "login_pw", "/html/body/div/div/form/center/button[1]",
            "carNumber", "/html/body/div[2]/ul/li/button",
            "",
            "chk_info1",  # 파킹박
            "chk_info1"  #
            ],
    # (하이파킹) 밀레니엄 서울 힐튼 주차장(서울역)
    14541: ["login_id", "login_pw", "/html/body/div/div/form/center/button[1]",
            "carNumber", "/html/body/div[2]/ul/li/button",
            "",
            "chk_info1",  # 파킹박
            "chk_info1"
            ],
    # (하이파킹)우림로데오스위트
    45009: ["login_id", "login_pw", "/html/body/div/div/form/center/button[1]",
            "carNumber", "/html/body/div[2]/ul/li/button",
            "",
            "chk_info1",  # 파킹박
            "chk_info1"
            ],
    #청담에비뉴
    19416: ["login_id", "login_pw", "/html/body/div/div/form/center/button[1]",
            "carNumber", "/html/body/div[2]/ul/li/button",
            "",
            "chk_info1",  # 1일권
            "chk_info1",  # 주말1일권
            ],
    # 메타랩스 아비스타
    19423: ["login_id", "login_pw", "/html/body/div/div/form/center/button[1]",
            "carNumber", "/html/body/div[2]/ul/li/button",
            "",
            "chk_info1",  # 1일권
            "",
            ],
}

blue_pass = [
    Parks.KIUM_NADEGI,
    Parks.SAMSUNG_SERVICE_BUILDING,
    Parks.MILLENNIUM_SEOUL_HILTON,
    Parks.URIM_RODEO_SWEET,

]
def log_out_web(driver):
    Util.sleep(1)

    element = driver.find_element_by_xpath("//a[contains(@href, 'doLogout')]")
    driver.execute_script("arguments[0].click();",element)
    print(Colors.BLUE + "로그아웃" + Colors.ENDC)

    driver.implicitly_wait(3)
    Util.sleep(3)

def get_har_in_script(park_id, ticket_name):
    if Util.get_week_or_weekend() == 0:
        return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]
    else:
        return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]


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

            driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
            driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])

            driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()
            driver.implicitly_wait(3)

            driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
            Util.sleep(3)

            driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()

            Util.sleep(3)

            if ParkUtil.check_search(park_id, driver):
                try:
                    driver.find_element_by_css_selector("#divAjaxCarList > tr > td:nth-child(2) > a").click()
                except NoSuchElementException:
                    log_out_web(driver)
                    return False

                if ParkUtil.check_same_car_num(park_id, ori_car_num, driver):
                    driver.implicitly_wait(3)

                    driver.find_element_by_id(get_har_in_script(park_id,ticket_name)).click()

                    if park_id in blue_pass:
                        #pass
                        driver.find_element_by_id("scbutton").click()
                    else:
                        driver.find_element_by_id("scbutton").click()

                    Util.sleep(3)

                    if park_id == Parks.GYEONG_BOK_GUNG:
                        pass
                    else:
                        try:
                            driver.implicitly_wait(3)
                            driver.switch_to.alert.accept()
                        except Exception as ex:
                            print("예상치 못한 에러\n", ex)
                    log_out_web(driver)
                    return True
                else:
                    log_out_web(driver)

            return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
