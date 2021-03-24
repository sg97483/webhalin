# -*- coding: utf-8 -*-
import re
import smtplib
from email.mime.text import MIMEText

from selenium.webdriver.support.select import Select

import Colors
import Util
import WebInfo
from park import ParkUtil, ParkType

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
            2,  # 평일종일권
            0,  # 주말종일권
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
            ],
    # 	AJ방배점
    19219: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일1일권
            0,  # 주말1일권 안팜
            1  # 야간권
            ],
    # 	AJ하우스디비즈
    19218: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일1일권
            0,  # 주말1일권 안팜
            1  # 야간권
            ],
    # 	AJ이화주차장점
    19212: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일1일권
            0,  # 주말1일권
            2  # 야간권
            ],
    # AJ파크 서울가든호텔점
    19148: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            2,  # 평일종일권
            0,  # 주말종일권
            1  # 야간권
            ],
    # AJ파크 영등포 JNS 빌딩점
    19142: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            2,  # 평일종일권
            0,  # 주말종일권
            1  # 야간권
            ],
    # AJ파크 홍익스포츠스파
    19226: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일종일권
            0,  # 주말종일권
            2  # 야간권
            ],
    # AJ파크 구월중앙점
    16434: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일종일권
            0,  # 주말종일권
            2  # 야간권
            ],
    # AJ파크 암사점
    19221: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일종일권
            0,  # 주말종일권
            2  # 야간권
            ],

    # 더피나클강남
    19227: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 야간권
            0,  # 야간권
            0  # 야간권
            ],
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


def web_har_in(target, driver, lotName):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]
    park_type = ParkType.get_park_type(park_id)

    trim_car_num = Util.all_trim(ori_car_num)
    search_id = trim_car_num[-4:]

    print("parkId = " + str(park_id) + ", " + "searchId = " + search_id)
    print(Colors.BLUE + ticket_name + Colors.ENDC)
    if str(ticket_name).endswith('연박권'):
        print("AJ파크 연박권")
        return False
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

            driver.implicitly_wait(3)

            count = len(driver.find_elements_by_xpath("/html/body/div[1]/section/div/section/div"))
            for index in range(1, count + 1):
                sale_table = driver.find_element_by_xpath("/html/body/div[1]/section/div/section/div[" + str(index) + "]")
                searched_car_number = driver.find_element_by_xpath(
                     "/html/body/div[1]/section/div/section/div[" + str(index) + "]/div/dl[1]/dd").text
                print("나누기전 : " + searched_car_number)
                td_car_num_1 = re.sub('<.+?>', '', searched_car_number, 0, re.I | re.S)
                td_car_num_2 = td_car_num_1.strip()
                td_car_num_3 = td_car_num_2.split('\n')

                global td_car_num
                if len(td_car_num_3[0].split(' ')) > 1:
                    td_car_num = td_car_num_3[0].split(' ')[0][-7:]
                else:
                    td_car_num = td_car_num_3[0][-7:]

                print("검색된 차량번호 : " + td_car_num + " == " + "기존 차량번호 : " + ori_car_num + " / " + ori_car_num[-7:])

                if ori_car_num[-7:] == td_car_num or ori_car_num == td_car_num:
                    driver.find_element_by_xpath("/html/body/div[1]/section/div/section/div["+str(index)+"]").find_element_by_class_name("selectCarInfo").click()

                    select = Select(driver.find_element_by_id('selectDiscount'))
                    select.select_by_index(get_har_in_script(park_id, ticket_name))
                    Util.sleep(2)
                    aj_ticket_info = select.first_selected_option.text
                    print(Colors.BLUE + aj_ticket_info + Colors.ENDC)
                    aj_ticket_cnt_txt = aj_ticket_info[-6:]
                    aj_ticket_cnt = int(re.findall('[0-9]+', aj_ticket_cnt_txt)[0])

                    if aj_ticket_cnt == 1 or aj_ticket_cnt == 2:
                        sendmail_ajCount0(str(lotName) + " 지점 " + ticket_name + " 할인권 구매부탁드립니다.")
                        print(Colors.RED + "주차권이 부족합니다." + Colors.ENDC)
                        driver.implicitly_wait(3)
                        driver.find_element_by_id('discountSubmit').click()
                        driver.implicitly_wait(2)
                        driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/button[2]').click()

                        return True
                    try:
                        if aj_ticket_cnt < 1:  # 주차권이 0매인 경우
                            sendmail_ajCount0(str(lotName) + " 지점 " + ticket_name + " 할인권 구매부탁드립니다.")
                            print(Colors.RED + "주차권이 부족합니다." + Colors.ENDC)
                            return False

                        else:  # 주차권이 부족하지 않을 때
                            driver.implicitly_wait(3)
                            driver.find_element_by_id('discountSubmit').click()
                            driver.implicitly_wait(2)
                            driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/button[2]').click()
                            return True
                    except ValueError as ex:
                        print(Colors.RED + "잘못된 주차권 갯수입니다. : " + ex + Colors.ENDC)
                        return False

                else:
                    print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)
                    continue
                return False
            return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False


def sendmail_ajCount0(text):
    sendEmail = "parkingpark_dev_daseulkim@wisemobile.co.kr"
    recvEmail = "parkingpark@wisemobile.co.kr"
    password = "!k4850218"

    smtpName = "smtp.worksmobile.com"  # smtp 서버 주소
    smtpPort = 587  # smtp 포트 번호

    msg = MIMEText(text)  # MIMEText(text , _charset = "utf8")

    msg['Subject'] = "  AJ파크 주차권 구매사항   "
    msg['From'] = sendEmail
    msg['To'] = recvEmail
    print(msg.as_string())

    s = smtplib.SMTP(smtpName, smtpPort)  # 메일 서버 연결
    s.starttls()  # TLS 보안 처리
    s.login(sendEmail, password)  # 로그인
    s.sendmail(sendEmail, recvEmail, msg.as_string())  # 메일 전송, 문자열로 변환하여 보냅니다.
    s.quit()  # smtp 서버 연결을 종료합니다.
