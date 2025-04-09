# -*- coding: utf-8 -*-
import re
import smtplib
import time
from email.mime.text import MIMEText

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import Colors
import Util
import WebInfo
from park import ParkUtil, ParkType

mapIdToWebInfo = {

    # 논현점(AJ파크)
    19156: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            0,  # 평일종일권
            0,  # 주말종일권 없음
            1  # 야간권
            ],

    # 하이파킹 딜라이트스퀘어2차상가점
    19600: ["email", "password", "//*[@id='login']",
            "carNo", "searchSubmitByDate",
            "",
            1,  # 평일권
            0,  # 주말
            0  # 야간
            ],

    # 하이파킹 L7호텔강남
    19004: ["email", "password", "//*[@id='login']",
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


def handle_ticket(driver, park_id, ticket_name):
    """
    주차장 및 주차권에 따른 할인권 처리 (19004, 19600 포함)
    """
    print(f"DEBUG: 할인 처리 시작 (park_id={park_id}, ticket_name={ticket_name})")

    # ✅ 19004 전용 할인 처리
    if park_id == 19004:
        ticket_map = {
            "평일 당일권(월)": "평일당일권(공유서비스)",
            "평일 당일권(화)": "평일당일권(공유서비스)",
            "평일 당일권(수)": "평일당일권(공유서비스)",
            "평일 당일권(목)": "평일당일권(공유서비스)",
            "평일 당일권(금)": "평일당일권(공유서비스)",
            "휴일 당일권": "휴일당일권(공유서비스)",
            "평일 심야권": "야간권(공유서비스)",
            "휴일 심야권": "야간권(공유서비스)",
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: 19004에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_text = ticket_map[ticket_name]

        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )
            options = select_element.find_elements(By.TAG_NAME, "option")
            matched = False
            for option in options:
                if target_text in option.text:
                    option.click()
                    print(f"DEBUG: '{option.text}' 옵션 선택 완료.")
                    matched = True
                    break

            if not matched:
                print(f"ERROR: '{target_text}' 텍스트가 포함된 옵션을 찾을 수 없습니다.")
                return False

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: 19004 처리 중 예외 발생: {e}")
            return False

    # ✅ 19600 전용 할인 처리
    if park_id == 19600:
        ticket_map = {
            "평일 당일권(월)": "평일당일권(공유서비스)",
            "평일 당일권(화)": "평일당일권(공유서비스)",
            "평일 당일권(수)": "평일당일권(공유서비스)",
            "평일 당일권(목)": "평일당일권(공유서비스)",
            "평일 당일권(금)": "평일당일권(공유서비스)",
            "평일 3시간권": "평일3시간권(공유서비스)",
            "평일 5시간권": "평일5시간권(공유서비스)",
            "평일 12시간권": "평일12시간권(공유서비스)",
            "휴일 3시간권": "휴일3시간권(공유서비스)",
            "휴일 12시간권": "휴일12시간권(공유서비스)",
            "평일 심야권": "평일심야권(공유서비스)",
        }

        if ticket_name not in ticket_map:
            print(f"ERROR: 19600에서 지원하지 않는 ticket_name: {ticket_name}")
            return False

        target_text = ticket_map[ticket_name]

        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectDiscount"))
            )
            options = select_element.find_elements(By.TAG_NAME, "option")
            matched = False
            for option in options:
                if target_text in option.text:
                    option.click()
                    print(f"DEBUG: '{option.text}' 옵션 선택 완료.")
                    matched = True
                    break

            if not matched:
                print(f"ERROR: '{target_text}' 텍스트가 포함된 옵션을 찾을 수 없습니다.")
                return False

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "discountSubmit"))
            ).click()
            print("DEBUG: 할인 적용 버튼 클릭 완료.")

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
                print("DEBUG: 알림창 확인 완료.")
            except TimeoutException:
                print("DEBUG: 알림창 없음.")

            return True

        except Exception as e:
            print(f"ERROR: 19600 처리 중 예외 발생: {e}")
            return False

    print(f"ERROR: handle_ticket에서 처리되지 않은 park_id: {park_id}")
    return False



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

                driver.find_element(By.ID, web_info[WebInfo.inputId]).send_keys(AJ_PARK_ID)
                driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(AJ_PARK_PW)
                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()
                print("로그인버튼  ")

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "webdiscount"))
            ).click()
            driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
            driver.find_element_by_id('searchSubmitByDate').click()

            driver.implicitly_wait(3)

            count = len(driver.find_elements(By.XPATH, "/html/body/div[1]/section/div/section/div"))
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
                    driver.find_element(By.XPATH, f"/html/body/div[1]/section/div/section/div[{index}]").find_element(By.CLASS_NAME, "selectCarInfo").click()

                    # ✅ 19004, 19600은 handle_ticket() 함수로 별도 처리
                    if park_id in [19004, 19600]:
                        return handle_ticket(driver, park_id, ticket_name)

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