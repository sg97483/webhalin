# -*- coding: utf-8 -*-
import Util
import ParkType
import Colors
import ParkUtil
import WebInfo
import re

Parks = ParkType.Parks

mapIdToWebInfo = {
    # Iparking 서초 마제스타
    18966: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "1"
            ],
    # 오토웨이타워
    15309: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "4"
            ],
    # (하이파킹) 94빌딩
    18957: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "5"
            ],
    # 눈스퀘어
    12929: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "6"
            ],
    # (하이파킹) 래미안용산더센트럴 주차장
    19138: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "6"
            ],
    # (광화문)콘코디언빌딩
    12806: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "6"
            ]
}

i_parking_hi_parking = [
    Parks.MAJESTA,
    Parks.AUTOWAY_TOWER,
    Parks.NUN_SQUARE,
    Parks.BUILDING_94
]


def get_har_in_script(park_id, ticket_name):
    # todo 요일 구분이 필요없는 현장
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
            if ParkUtil.first_access(park_id, driver.current_url):
                if ParkUtil.check_first_conn(park_type):

                    driver.find_element_by_id("skip").click()

                driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
                driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])

                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()

                Util.sleep(1)
                driver.find_element_by_id("gohome").click()
                driver.find_element_by_xpath("//*[@id='start']").click()
                if park_id in i_parking_hi_parking:
                    driver.find_element_by_xpath(
                        "//*[@id = 'storeSelect'] / option[" + web_info[WebInfo.methodHarIn1] + "]").click()

                # discount_url = login_url + ParkUtil.get_park_discount_url(park_type)
                # driver.get(discount_url)

                driver.implicitly_wait(3)

                driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
                Util.sleep(3)

                driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()

                Util.sleep(1)

                tr_text = driver.find_element_by_css_selector("#notChooseCar > p:nth-child(1)").text
                text = re.sub('<.+?>', '', tr_text, 0, re.I | re.S)
                trim_text = text.strip()

                if trim_text.endswith("에 대한 검색 결과가 없습니다."):
                    print(Colors.YELLOW + "검색 결과가 없습니다." + Colors.ENDC)
                else:
                    if ParkUtil.check_same_car_num(park_id, ori_car_num, driver):
                        driver.find_element_by_id("next").click()
                        Util.sleep(3)
                        try:
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            driver.find_element_by_css_selector("#productList > tr > td:nth-child(3) > button").click()
                            driver.find_element_by_id("popupOk").click()
                        except Exception as ex:
                            print("예상치 못한 에러\n", ex)

                        return True

                return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False