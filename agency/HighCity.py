# -*- coding: utf-8 -*-
import Util
import Colors
from park import ParkUtil, ParkType, Parks
import WebInfo

mapIdToWebInfo = {
    # HighCity 동일타워
    15313: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('09', '', '1', '', '어플주말당일권(웹할인)', '1', '0');",
            "javascript:applyDiscount('10', '', '1', '', '어플평일당일권(웹할인)', '1', '0');",
            "javascript:applyDiscount('14', '', '1', '', '어플공휴일당일권(웹할인)', '1', '0');"],
    # 남산스퀘어
    13007: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('62', '1', '', '파킹박', '1')",
            "javascript:applyDiscount('62', '1', '', '파킹박', '1')",
            "javascript:applyDiscount('66', '1', '', '파킹박(야간)', '1') ",
            ],

    # AIA 타워
    18958: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('14', '1', '', '파킹박(평일)', '999999999', '0');",
            "javascript:applyDiscount('15', '1', '', '파킹박(주말)', '999999999', '0');",
            "javascript:applyDiscount('17', '1', '', '파킹박(야간)', '999999999', '0');"],
    # SC_BANK
    12750: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('23', '1', '16|25|', '파킹박 (web)', '999999999');",
            "javascript:applyDiscount('23', '1', '16|25|', '파킹박 (web)', '999999999');",
            ""],

    # 트윈시티남산
    16003: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('98', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('98', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('92', '1', '', '파킹박(야간)', '1', '0');"

            ],

    # 다동패스트파이브 타워
    16170: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('05', 'CP0802', '1', '', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('05', 'CP0802', '1', '', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('32', '1', '', '파킹박(야간)', '999999999', '0') ;",
            ],
    # 여의도 리버타워
    20863: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('19', '1', '20|', '파킹박');",
            "javascript:applyDiscount('19', '1', '20|', '파킹박');"
            ],
    # (하이파킹) 판교알파리움타워(1동)
    18996: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('13', '1', '14|16|17|', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('13', '1', '14|16|17|', '파킹박', '999999999', '0');"
            ],
    # EG빌딩
    19194: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('20', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('20', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('32', '1', '', 'ppark(야간)', '1', '0') ;",
            ],
    # (하이파킹) 오라카이대학로
    19181: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('21', '1', '', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('21', '1', '', 'ppark', '999999999', '0');"
            ],

    #  문정플라자
    19022: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('35', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('35', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('98', '1', '04|', 'ppark(야간)', '1', '0') ;",
            ],
    #  코리아나호텔
    19248: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('13', '1', '01|02|03|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('13', '1', '01|02|03|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('31', '1', '', 'ppark(야간)', '999999999', '0');",
            ],
    #  힐스테이트에코마곡나루역
    19272: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '17|', 'ppark', '1', '0');",
            "javascript:applyDiscount('08', '1', '17|', 'ppark', '1', '0');"
            ],

    #  동산마을공영
    19276: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            ],
    #  D타워
    19325: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('14', '1', '11|20|21|', 'ppark', 'Y');",
            "javascript:applyDiscount('14', '1', '11|20|21|', 'ppark', 'Y');",
            "javascript:applyDiscount('17', '1', '11|20|21|', 'ppark(야간)', 'Y');",  # ← 이 부분 고쳐야 함
            ],
    #  반포동방음언덕형공영
    19273: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '05|', 'PPark', '1', '0');",
            "javascript:applyDiscount('08', '1', '05|', 'PPark', '1', '0');",
            "javascript:applyDiscount('08', '1', '05|', 'PPark', '1', '0');",
            ],
    # 그랜드센트럴
    19364: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('91', '1', '', 'ppark(야간)', '999999999', '0'); ",
            ],


    # (하이파킹) 서울역 주차장
    20864: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('12', '', '5', '01|', 'ppark', '1', '0');",  # 평일1일권
            "javascript:applyDiscount('25', '', '1', '', 'ppark(연박2일)', '1', '0');",  # 연박2일권"",
            "javascript:applyDiscount('26', '', '1', '', 'ppark(연박3일)', '1', '0');",  # 연박3일권"",
            "javascript:applyDiscount('27', '', '1', '', 'ppark(연박4일)', '1', '0');",  # 연박4일권"",
            "javascript:applyDiscount('28', '', '1', '', 'ppark(연박5일)', '1', '0');",  # 연박5일권"",
            ],

    # 오라카이 청계산
    19185: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('31', '1', '', '파킹박', '1', '0')   ",  # 평일1일권
            "javascript:applyDiscount('31', '1', '', '파킹박', '1', '0')  ",  # 주말
            "javascript:applyDiscount('31', '1', '', '파킹박', '1', '0') ",
            ],

    # GS타임즈 반포2동공영(티바디쪽 뭐 안됨)
    19492: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//*[@id=""search_form""]/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('09', 'CP0802', '1', '', '24시간(유료)', '0', '0') ",  # 평일1일권
            "javascript:applyDiscount('16', 'CP0802', '1', '', '휴일 당일권', '0', '0')  ",  # 주말
            "javascript:applyDiscount('08', 'CP0801', '99', '', '12시간(유료)', '99999999', '21600')  ", #12시간권
            ],

}

def get_har_in_script(park_id, ticket_name):
    # 1. 특정 주차장 + 특정 티켓 분기
    if park_id == 12750 and ticket_name == "평일 3시간권":
        return "javascript:applyDiscount('76', '1', '', '12시간권', '999999999');"

    if park_id == 19325 and ticket_name in ["평일 심야권(일~목)", "휴일 심야권(금,토)"]:
        return "javascript:applyDiscount('17', '1', '11|20|21|', 'ppark(야간)', 'Y');"

    if park_id == 16003:
        if ticket_name in ["평일 당일권", "휴일 당일권"]:
            return "javascript:applyDiscount('98', '5', '25|29|', '파킹박', '1', '0');"
        elif ticket_name in ["평일 심야권", "휴일 심야권"]:
            return "javascript:applyDiscount('92', '1', '25|29|', '파킹박(야간)', '1', '0');"
        elif ticket_name == "평일 오후 6시간권":
            return "javascript:applyDiscount('93', '1', '', '평일오후6시간권(공유)', '1', '0');"
        elif ticket_name == "휴일 연박권":
            return "javascript:applyDiscount('80', '1', '25|29|', '2일권', '1', '0');"
        else:
            return False  # ❗️트윈시티남산에서 지정된 티켓 외는 실패 처리

    if park_id == 20863:
        if ticket_name in ["평일 당일권", "휴일 당일권"]:
            return "javascript:applyDiscount('19', '1', '05|', '파킹박');"
        else:
            return False  # ❗️20863에서 지정된 티켓 외는 실패 처리

    # 2. 공통 룰
    if ticket_name[-3:] == "심야권" or ticket_name[-3:] == "야간권":
        if park_id in mapIdToWebInfo:
            return mapIdToWebInfo[park_id][WebInfo.night]
        else:
            return False  # ❗️대상 주차장에 정보 없으면 실패

    elif ticket_name == "평일1일권":
        if park_id in mapIdToWebInfo:
            return mapIdToWebInfo[park_id][WebInfo.weekday]
        else:
            return False

    elif ticket_name in ["주말1일권", "토요일권", "일요일권"]:
        if park_id in mapIdToWebInfo:
            return mapIdToWebInfo[park_id][WebInfo.weekend]
        else:
            return False

    # 3. 기타 티켓에 대해서 평일/주말에 따른 분기
    if park_id in mapIdToWebInfo:
        if Util.get_week_or_weekend() == 0:  # 평일
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]
        else:  # 주말
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]
    else:
        return False  # ❗️최종적으로도 없으면 실패






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

                    if ParkUtil.check_same_car_num(park_id, ori_car_num, driver):
                        driver.find_element_by_id(web_info[WebInfo.btnItem]).click()
                        harin_script = get_har_in_script(park_id, ticket_name)
                        if not harin_script:
                            print("유효하지 않은 ticket_name 입니다.")  # 실패 메시지
                            return False  # 프로세스 종료 (더 진행 안 함)
                        driver.execute_script(harin_script)
                        return True
                return False

        else:
            print(Colors.BLUE + "high현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
