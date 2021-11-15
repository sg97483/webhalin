# -*- coding: utf-8 -*-
from selenium.webdriver.support.wait import WebDriverWait

import Util
import Colors
from park import ParkUtil, ParkType, Parks
import WebInfo
import re
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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
            ],
    # 성수 우리 W타워
    18968: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "6"
            ],
    # (하이파킹) 디아뜨센트럴
    19183: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "6"
            ],
    # (하이파킹) 비트플렉스몰
    19241: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "6"
            ],
    # 여의도 NH농협캐피탈
    12532: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    # 이수공영주차장
    19236: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],

    # KT 구로지밸리
   19425: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],

    # 서초 꽃마을
    19433: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    # 예전빌딩
    19448: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    # 	강남헤븐리치더써밋761
    19449: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    #미래에셋플러스
    19446: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],


    #바토프라자
     19458: ["id", "password", "//*[@id='login']",
             "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
             "#carList > tr",
             "2"
             ],
    #동양프라자
    19459: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    #다산법조메디컬타워
    19461: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    #화광빌딩
    19462: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    #영등포주차장
    19463: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    #에이스골드타워
    19470: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    #미래에셋대우여의도빌딩
    19473: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    # 영동프라자
    19475: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],

    # 이마트TR송림점
    19476: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    # 이마트TR구성점
    19477: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],

    #GS타임즈 미래에셋대우여의도빌딩
    19473: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],


}

i_parking_hi_parking = [
    Parks.MAJESTA,
    Parks.AUTOWAY_TOWER,
    Parks.NUN_SQUARE,
    Parks.BUILDING_94,
    Parks.YEOUIDO_NH_CAPITAL
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
    Util.sleep(2)
    if park_id == 15309 and ticket_name == "심야권":
        print(Colors.RED + "오토웨이 타워 심야권 이용 고객입니다." + Colors.ENDC)
        return False

    park_type = ParkType.get_park_type(park_id)

    trim_car_num = Util.all_trim(ori_car_num)
    search_id = trim_car_num[-4:]

    print("parkId = " + str(park_id) + ", " + "searchId = " + search_id)
    print(Colors.BLUE + ticket_name + Colors.ENDC)

    if ParkUtil.is_park_in(park_id):
        if park_id in mapIdToWebInfo:
            login_url = ParkUtil.get_park_url(park_id)
            driver.implicitly_wait(3)
            Util.sleep(2)
            driver.get(login_url)

            web_info = mapIdToWebInfo[park_id]
            web_har_in_info = ParkUtil.get_park_lot_option(park_id)
            # todo 현재 URL을 가지고와서 비교 후 자동로그인

            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='popupOk']"))).click()
            except:
                print("팝업창 없음")

            if ParkUtil.first_access(park_id, driver.current_url):
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "skip"))).click()
                    print("skip")
                except:
                    print("skip 불가능")
                try:
                    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//*[@id='popupOk']"))).click()
                except:
                    print("팝업창 없음")

                driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
                driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])
                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()
                Util.sleep(2)


                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gohome"))).click()

                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='start']"))).click()

                if park_id in i_parking_hi_parking:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id = 'storeSelect'] / option[" + web_info[WebInfo.methodHarIn1] + "]"))).click()
                    # driver.find_element_by_xpath(
                    #     "//*[@id = 'storeSelect'] / option[" + web_info[WebInfo.methodHarIn1] + "]").click()

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

                        try:
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, "next"))).click()
                            Util.sleep(3)
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                            if park_id == 19446:
                               print(Colors.YELLOW +"분당"+ Colors.ENDC)
                               WebDriverWait(driver, 10).until(
                               EC.presence_of_element_located(
                                       (By.XPATH, "//*[@id='productList']/tr[3]/td[3]/button"))).click()
                            else:
                                WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "#productList > tr > td:nth-child(3) > button"))).click()
                            Util.sleep(2)
                            driver.find_element_by_id("popupOk").click()
                            return True
                        except Exception as ex:
                            print("예상치 못한 에러\n", ex)
                            return False

                return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False