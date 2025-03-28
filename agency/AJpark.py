# -*- coding: utf-8 -*-
import re
import smtplib
import time
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
            25002,  # 야간권
            25001,  # 주말종일권
            139775,  # 4시간권
            42412  # 평일종일권
            ],
    # 합정역점(AJ파크)
    19157: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일종일권
            0,  # 주말종일권
            2  # 야간권
            ],
    # 논현점(AJ파크)
    19156: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일종일권
            0,  # 주말종일권 없음
            1  # 야간권
            ],

    # 강남역점(AJ파크)
    19162: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일종일권
            1,  # 주말종일권
            0  # 야간권
            ],
    # 종로관훈점
    19140: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일종일권
            2,  # 주말종일권
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
            2,  # 주말종일권
            0  # 야간권
            ],

    #정곡빌딩,
    19464: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            2,  # 평일3시간권
            1,  # 주말권
            0  # 야간권
            ],
    #하이센스빌,
    19465: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            0,  # 평일권
            0  # 평일권
            ],
    #영통동아점,
    19467: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 종일권
            0,  # 종일권
            0  # 종일권
            ],
    # 상봉점,
    19468: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일
            0,  # 주말
            1  #
            ],

    #운현프라자(하이그린)
    19490: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 주말당일
            0,  # 주말당일
            0  # 주말당일
            ],

    # 공덕역점
    19491: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 주말당일
            0,  # 주말당일
            0  # 주말당일
            ],
    #금촌
    19500: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일
            0,  # 주말당일
            0  # 주말당일
            ],

    #  금강주차빌딩점
    19502: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일
            1,  # 주말당일
            2  # 야간권
            ],
    #  노원하계점
    19506: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일
            1,  # 주말당일
            2  # 야간권
            ],
    # 신촌e편한세상4단지
    19511: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 야간권
            0,  # 야간권
            0  # 야간권
            ],
    # 신사 ICT
    19516: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            0,  # 평일권
            0  # 평일권
            ],
    # 리더스퀘어마곡점
    19521: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            1,  # 주말
            0  # 야간
            ],
    # 매그넘797점
    19522: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            3,  # 평일권
            2  # 평일권
            ],
    # M시그니처점
    19524: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            2,  # 평일권
            1  # 평일권
            ],
    #스페이스k 서울미술관점
    19525: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            0,  # 평일권
            2  # 평일권
            ],
    ##
    # AJ파크 속초점
    19533: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            1,  # 주말
            0  # 야간
            ],
    # 원주 서영 에비뉴파크 1차점
    19534: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            1,  # 주말
            2  # 야간
            ],
    # 롯데슈퍼 오남2점
    19535: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            1,  # 주말
            0  # 야간
            ],
    # 안산한미타워점
    19536: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            2  # 야간
            ],
    # 신영프라자점
    19537: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    #의왕월드비젼점
    19538: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 대전둔산점
    19540: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 건양타워점
    19541: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 대전지족점
    19542: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 옥타브상가점
    19543: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            1,  # 주말
            0  # 야간
            ],
    # 옥타브상가B동점
    19544: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 다정센타프라자2점
    19545: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 스마트큐브1차점
    19546: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 메가타워1점
    19547: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 고운드림빌딩점
    19548: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 금남프라자점
    19549: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            1,  # 주말
            0  # 야간
            ],
    # 지엘플렉스1점
    19550: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 지엘플렉스2점
    19551: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    #  영토프라자점
    19552: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 펜타포트 1블럭 상가점
    19553: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],
    # 에스엘주차타워점
    19554: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일권
            1,  # 주말
            0  # 야간
            ],
    # 청주용암점
    19555: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
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
    # if str(ticket_name).endswith('연박권') or str(ticket_name).endswith('2일권'):
    #     print("AJ파크 연박권")
    #     return False
    if park_id == 19141 and ori_car_num =='108가5701' :
        print(Colors.BLUE + "108가5701 웹할인 확인이 필요한 차량입니다" + Colors.ENDC)
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

                #Util.close_popup(driver)
                #print(Colors.BLUE + "팝업테스트" + Colors.ENDC)
                #driver.find_element_by_id('expiresChk').click()
                print(Colors.BLUE + "팝업테스트" + Colors.ENDC)

                driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(AJ_PARK_ID)
                driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(AJ_PARK_PW)


                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()
                print("로그인버튼  ")

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
    sendEmail = "email@wisemobile.co.kr"
    recvEmail = "email@wisemobile.co.kr"
    password = "password"

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
