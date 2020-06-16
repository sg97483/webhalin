# -*- coding: utf-8 -*-
from selenium.webdriver.support.select import Select

import Util
import ParkType
import Colors
import ParkUtil
import WebInfo

Parks = ParkType.Parks

mapIdToWebInfo = {
    # AJ파크 공덕효성해링턴스퀘어점
    19146: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            2,  # 평일종일권
            0,  # 주말종일권
            1  # 야간권
            ],
    # AJ파크 무교동점
    19147: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일종일권
            2,  # 주말종일권
            1  # 야간권
            ],
    # AJ파크 교원명동빌딩점
    19145: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            2,  # 평일종일권
            0,  # 주말종일권
            1  # 야간권
            ],
    # AJ파크 MDM타워점
    19143: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            2,  # 평일종일권
            0,  # 주말종일권
            1  # 야간권
            ],
    # 합정역점(AJ파크)
    19157: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일종일권
            2,  # 주말종일권
            0  # 야간권
            ],
    # 논현점(AJ파크)
    19156: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일종일권
            0,  # 주말종일권 없음
            1  # 야간권
            ],
    # AJ파크 을지로3가점
    19139: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            2,  # 평일종일권
            0,  # 주말종일권
            1  # 야간권
            ],
    # 강남역점(AJ파크)
    19162: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            2,  # 평일종일권
            1,  # 주말종일권
            0  # 야간권
            ],
    # 문정프라비다점
    19160: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일종일권
            0  # 주말종일권
            ],
    # 미스터홈즈 선정릉점
    19161: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일종일권
            0,  # 주말종일권
            2  # 야간권
            ],
    # 종로관훈점
    19140: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            2,  # 평일종일권
            0,  # 주말종일권
            1  # 야간권
            ],
    # 	AJ파크 티마크그랜드호텔점
    19141: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            2,  # 평일종일권
            0,  # 주말종일권
            1  # 야간권
            ],
    # 	AJ파크 신덕빌딩
    19230: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일심야권
            0,  # 평일심야권
            0  # 평일심야권
            ],
    # 	AJ파크 홍대아일렉스스퀘어점
    19159: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일1일권
            0,  # 주말1일권
            2  # 야간권
            ],
    # 	AJ파크 논현웰스톤
    19215: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일1일권
            0,  # 주말1일권
            1  # 야간권
            ]
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

            # todo 현재 URL을 가지고와서 비교 후 자동로그인
            # print(driver.current_url)
            # 재접속이 아닐 때, 그러니까 처음 접속할 때
            if ParkUtil.first_access(park_id, driver.current_url):

                driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(AJ_PARK_ID)
                driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(AJ_PARK_PW)

                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()

            driver.find_element_by_id('webdiscount').click()

            driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
            driver.find_element_by_id('searchSubmitByDate').click()

            driver.implicitly_wait(10)

            if ParkUtil.check_search(park_id, driver):
                if ParkUtil.check_same_car_num(park_id, ori_car_num, driver):
                    driver.find_element_by_class_name('selectCarInfo').click()

                    select = Select(driver.find_element_by_id('selectDiscount'))
                    select.select_by_index(get_har_in_script(park_id, ticket_name))
                    driver.implicitly_wait(3)
                    driver.find_element_by_id('discountSubmit').click()
                    return True

            return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
