# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoAlertPresentException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import Util
import Colors
from park import ParkUtil, ParkType, Parks
import WebInfo

mapIdToWebInfo = {
    # 파이낸스 타워 GS
    12539: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div[2]/div[2]/table/tbody/tr[1]/td/div/div/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            ""],
    # 안녕인사동
    19166: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/div[2]/div/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('83:24시간무료(웹)', '1');",
            "javascript:fnDisCount('83:24시간무료(웹)', '1');",
            "javascript:fnDisCount('83:24시간무료(웹)', '1');",
            ""],
    # SI 타워
    19136: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/div/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            "javascript:fnDisCount('55:24시간무료(웹)', '1');"],
    # DMC-S CITY
    19044: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 98173');",
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 98173');",
            ""],
    # DMCC
    15639: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div[2]/div[2]/table/tbody/tr[1]/td/div/div/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            ""],
    # 메가박스성수
    19168: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div[2]/div[2]/table/tbody/tr[1]/td/div/div/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            ""],
    # 논현빌딩
    11290: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div[2]/div[2]/table/tbody/tr[1]/td/div/div/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            "javascript:fnDisCount('55:24시간무료(웹)', '1');",
            ""],
    # 	당산역 이레빌딩
    19100: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/div/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9968', '2');",
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9968', '2');",
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9968', '2');",
            ""],
    # KDB생명(연박권 따로빼기)
    45655: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9549');",  # 1일권
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9549');",  #
            "javascript:fnDisCount('75:전액무료(웹) / 잔여수량 9956');",  # 전액 무료
            "",
            "javascript:fnDisCount('79:전액무료(웹) / 잔여수량 9956');","javascript:fnDisCount('80:전액무료(웹) / 잔여수량 9956');"],
    # (하이파킹) 파크빌딩
    19180: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('33:파킹박', '1');",
            "javascript:fnDisCount('33:파킹박', '1');",
            "javascript:fnDisCount('33:파킹박', '1');",
            ""],
    # (하이파킹) 어바니엘천호
    19196: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('56:전액무료(웹)', '1');",
            "javascript:fnDisCount('56:전액무료(웹)', '1');",
            ""],
    # 상봉듀오트리스
    19240: ["login_id", "login_pw",
            """//*[@id="third"]/div/div/div/div[5]/div/input""",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('56:전액무료(웹) / 잔여수량 99996', '1');",
            "javascript:fnDisCount('56:전액무료(웹) / 잔여수량 99996', '1');",
            ""],
    # 현대계동사옥 주차장
    12749: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('79:당일권');",
            "javascript:fnDisCount('79:당일권');",
            ""],
    # 머큐어앰버서더 홍대호텔
    19199: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('57:전액무료(웹)', '1');",
            "javascript:fnDisCount('57:전액무료(웹)', '1');",
            "javascript:fnDisCount('57:전액무료(웹)', '1');",
            ""],

    #마곡스프링파크타워
    19081: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');", #1일권
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');",
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');",
            ""],

    # 강동홈플러스(GS타임즈)
    19243: ["login_id", "login_pw",
            """//*[@id="bodyCSS"]/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]""",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');", #1일권
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');",
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');",
            ""],

    # KB금융타워
    19400: ["login_id", "login_pw",
            """//*[@id="bodyCSS"]/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]""",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 99999706');", #1일권
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 99999706');", #1일권
            ""],

    # 중앙로공영주차장
    19237: ["login_id", "login_pw", "//*[@id='bodyCSS']/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",
            "javascript:fnDisCount('56:전액무료(웹)', '1');", # 평일1일권
            "javascript:fnDisCount('56:전액무료(웹)', '1');", # 주말1일권
            "javascript:fnDisCount('56:전액무료(웹)', '1');", # 심야권
            ],
    # 더에셋
    19415: ["login_id", "login_pw", "//*[@id='bodyCSS']/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",
            "javascript:fnDisCount('54:12시간무료(플랫폼)', '1');", # 12시간 무료 (6)
            "javascript:fnDisCount('55:24시간무료(플랫폼)', '1');", # 24시간무료
            "javascript:fnDisCount('56:14시간무료(플랫폼)', '1');", # 14시간 무료(심야,주말)
            ],

    # TnS빌딩
    19430: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('78:ppark(웹)', '1');",
            "javascript:fnDisCount('78:ppark(웹)', '1');",
            ],
    #D타워
    19401: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "fnDisCount('75:24시간유료(웹) / 잔여수량 999999994', '2');",  #24시간무료
            "fnDisCount('75:24시간유료(웹) / 잔여수량 999999994', '2');",  # 24시간무료
            "fnDisCount('64:3시간유료(웹) / 잔여수량 999999999', '2');",  #3시간무료
            ],
    # 포스트빌
    19447: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "fnDisCount('75:24시간유료(웹) / 잔여수량 999999994', '2');",  # 24시간무료
            "fnDisCount('75:24시간유료(웹) / 잔여수량 999999994', '2');",  # 24시간무료
            "fnDisCount('64:3시간유료(웹) / 잔여수량 999999999', '2');",  # 3시간무료
            ],
    # 강남역(GS타임즈)
    19392: ["login_id", "login_pw",
            """//*[@id="bodyCSS"]/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input""",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');",  # 1일권
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');",
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');",
            ""],
    #한국경제신문
    19450: ["login_id", "login_pw",
            "//*[@id='third']/div/div/div/div[5]/div/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');",  # 1일권
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');",
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 999978');",
            ""],
    # 부천 국민차 매매단지
    19436: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('3:파킹박 / 잔여수량 999999953');",  # 1일권
            "javascript:fnDisCount('3:파킹박 / 잔여수량 999999969');",
            "javascript:fnDisCount('3:파킹박 / 잔여수량 999999969');",
            ""],
    # 파스텔시티
    19460: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('74:12시간유료(웹) / 잔여수량 999', '2');",  # 1일권
            "javascript:fnDisCount('74:12시간유료(웹) / 잔여수량 999', '2');",
            "javascript:fnDisCount('74:12시간유료(웹) / 잔여수량 999', '2');",
            ""],
    #서브원강남빌딩
    19021: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('58:24시간할인(웹)무료 / 잔여수량 9999999');",  # 1일권
            "javascript:fnDisCount('58:24시간할인(웹)무료 / 잔여수량 9999999');",
            "javascript:fnDisCount('58:24시간할인(웹)무료 / 잔여수량 9999999');",
            ""],
    #롯데시네마도곡
    19474:  ["login_id", "login_pw",
            """//*[@id="bodyCSS"]/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input""",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('48:6시간무료(웹) / 잔여수량 1000', '1');",  # 6시간
            "javascript:fnDisCount('48:6시간무료(웹) / 잔여수량 1000', '1');", #
            "javascript:fnDisCount('45:3시간무료(웹) / 잔여수량 1000', '1');",
            ""],
    #포스트빌
    19447:  ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('75:24시간유료(웹)');",  # 1일권
            "javascript:fnDisCount('75:24시간유료(웹)');", #1일권
            "javascript:fnDisCount('74:12시간유료(웹)');", #12시간권
            ""],

    # 헤리츠웨딩홀
    19125: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9976');",  # 1일권
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9976');",
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9976');",
            ""],
    # 시티타워
    13044: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('77:어플할인(웹)', '1');",  # 1일권
            "javascript:fnDisCount('77:어플할인(웹)', '1');",
            "javascript:fnDisCount('77:어플할인(웹)', '1');",
            ""],
    #판교아이스퀘어C1
    19493: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",  # 1일권
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",
            ""],
    # 판교아이스퀘어C1
    19494: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",  # 1일권
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",
            ""],


}

def get_har_in_script(park_id, ticket_name):

    if park_id == 19415:
        if str(ticket_name).endswith("심야권"):
            return mapIdToWebInfo[park_id][WebInfo.night]
        elif str(ticket_name).endswith("주말1일권"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn3]
        elif str(ticket_name).endswith("평일 1일권"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]  #평일
        elif str(ticket_name).endswith("평일 12시간권"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]  #주말
    elif park_id == 45655: #KDB 연박
        if str(ticket_name).endswith("평일1일권"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]
        elif str(ticket_name).endswith("연박권(2일)"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn4]
        elif str(ticket_name).endswith("연박권(3일)"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn5]
        elif str(ticket_name).endswith("주말1일권"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]
        elif str(ticket_name).endswith("평일심야권"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn3]

    else:
        if str(ticket_name).endswith("심야권"):
            return mapIdToWebInfo[park_id][WebInfo.night]
        elif str(ticket_name).endswith("주말3시간권"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn3]
        elif Util.get_week_or_weekend() == 0:
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]  #평일
        else:
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]  #주말


def log_out_web(driver):
    Util.sleep(1)

    element = driver.find_element_by_xpath("//a[contains(@href, 'doLogout')]")
    driver.execute_script("arguments[0].click();",element)
    print(Colors.BLUE + "로그아웃" + Colors.ENDC)

    driver.implicitly_wait(3)
    Util.sleep(3)



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
    if park_id == Parks.MAGOK_SPRINGTOWER and ticket_name != "1일권":
        print("마곡스프링파크 1일권 아님")
        return False
    if str(ticket_name).endswith("연박권"):
        print("GS 연박권")
        return False





    if ParkUtil.is_park_in(park_id):
        if park_id in mapIdToWebInfo:
            login_url = ParkUtil.get_park_url(park_id)
            driver.implicitly_wait(3)
            driver.get(login_url)

            web_info = mapIdToWebInfo[park_id]
            web_har_in_info = ParkUtil.get_park_lot_option(park_id)
            # todo 현재 URL을 가지고와서 비교 후 자동로그인

            if park_id == Parks.DMC_S_CITY or park_id == Parks.MEGABOX_SUNGSU:
                driver.find_element_by_id(web_info[WebInfo.inputId]).clear()

            driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])

            if park_id == Parks.DMC_S_CITY or park_id == Parks.MEGABOX_SUNGSU:
                driver.find_element_by_id(web_info[WebInfo.inputPw]).clear()

            driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])

            driver.implicitly_wait(3)

            if park_id == Parks.FINANCE_TOWER \
                    or park_id == Parks.DMC_S_CITY \
                    or park_id == Parks.NONHYEON_BUILDING \
                    or park_id == Parks.KDB_LIFE \
                    or park_id == Parks.MODERN_GYEDONG_BUILDING \
                    or park_id == Parks.KB_TOWER \
                    or park_id == Parks.MERCURE_AMBASSADOR :
                Util.click_element_xpath(web_info[WebInfo.btnLogin], driver)
            else:
                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()

            driver.implicitly_wait(3)

            if park_id == Parks.DMC_S_CITY \
                    or park_id == Parks.KDB_LIFE\
                    or park_id == Parks.FINANCE_TOWER:
                Util.sleep(3)
                Util.input_element_id("searchCarNo", driver, search_id)
            #     옆으로 이동
            else:
                driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)

            Util.sleep(3)

            if park_id == Parks.FINANCE_TOWER \
                    or park_id == Parks.DMC_S_CITY \
                    or park_id == Parks.DMCC\
                    or park_id == Parks.NONHYEON_BUILDING \
                    or park_id == Parks.MEGABOX_SUNGSU \
                    or park_id == Parks.KDB_LIFE \
                    or park_id == Parks.MODERN_GYEDONG_BUILDING \
                    or park_id == Parks.KB_TOWER \
                    or park_id == Parks.MAGOK_SPRINGTOWER:
                driver.implicitly_wait(3)

                Util.click_element_id('btnSearch', driver)
            else:
                try:
                    driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()
                except NoSuchElementException:
                    log_out_web(driver)
                    return False

            Util.sleep(3)
            if park_id == Parks.MAGOK_SPRINGTOWER:
                driver.find_element_by_id('Reserve4').send_keys('1')

            # 차량 검색
            if ParkUtil.check_search(park_id, driver):
                if ParkUtil.check_same_car_num(park_id, ori_car_num, driver):
                    if park_id == 19447:
                        try:
                            Util.click_element_selector("#divAjaxCarList > tbody > tr > td > a", driver)
                        except NoSuchElementException:
                            log_out_web(driver)
                            return False

                    elif park_id == 19415 or park_id == 19430 or park_id == 19401:
                        try:
                            Util.click_element_selector("#divAjaxCarList > tr > td > a", driver)
                        except NoSuchElementException:
                            log_out_web(driver)
                            return False

                    else:
                        try:
                            Util.click_element_selector("#divAjaxCarList > tbody> tr > td > a", driver)
                        except NoSuchElementException:
                            log_out_web(driver)
                            return False
                    Util.sleep(3)
                    harin_script = get_har_in_script(park_id, ticket_name)
                    driver.execute_script(harin_script)

                    if park_id == Parks.HI_INSADONG:
                        driver.find_element_by_css_selector(
                            "#tr_dislist > td > table > tbody > tr:nth-child(3) > td > input.btn.btn-info").click()
                    Util.sleep(2)
                    try:
                        # wait for the alert to show up
                        WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                                        'Timed out waiting for PA creation ' +
                                                        'confirmation popup to appear.')
                        # if it does
                        driver.switch_to.alert.accept()
                        print
                        "alert accepted"
                    except TimeoutException:
                        print
                        "no alert"

                    log_out_web(driver)
                    Util.sleep(3)
                    return True
                log_out_web(driver)
                return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
