# -*- coding: utf-8 -*-
import datetime
import re

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.alert import Alert

import Util
import Colors
from park import ParkUtil, ParkType, Parks
import WebInfo

mapIdToWebInfo = {
    # 마곡 GMG주차타워
    19071: ["name", "pwd", "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "",
            "javascript:onclickDiscount('20200407090327-00361', '00009', '당일 무료', '56너0427', '매수차감', form1.remark.value);",
            "javascript:onclickDiscount('20200407090327-00361', '00009', '당일 무료', '56너0427', '매수차감', form1.remark.value);"],
    # (하이파킹) 순화빌딩 주차장
    # 16173: ["name", "pwd", "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",
    #         "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
    #         "",
    #         "javascript:onclickDiscount('1440', '20210927105212-00468', '00019', '앱서비스', '0000000000', '매수차감', form1.remark.value);",
    #         "javascript:onclickDiscount('1440', '20210927105212-00468', '00019', '앱서비스', '0000000000', '매수차감', form1.remark.value);"],

    # 발산 파크프라자
    19070: ["name", "pwd", "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "",
            "/html/body/table[2]/tbody/tr[4]/td[1]/p[1]/input",
            "/html/body/table[2]/tbody/tr[4]/td[1]/p[1]/input"],

    # 	롯데마트 영종도점(x)
    19497: ["name", "pwd", "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "",
            "javascript:onclickDiscount('1440', '20211118094204-99999', '00015', '24시간할인권', '111테1111', '매수차감', form1.remark.value);",
            "javascript:onclickDiscount('960', '20211118094204-99999', '00016', '야간권', '111테1111', '매수차감', form1.remark.value);"],
    # 	우리빌딩점 (x)
    19503: ["name", "pwd", "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "",
            "javascript:onclickDiscount('20200407090327-00361', '00009', '당일 무료', '56너0427', '매수차감', form1.remark.value);",
            "javascript:onclickDiscount('20200407090327-00361', '00009', '당일 무료', '56너0427', '매수차감', form1.remark.value);"],
    # 타워8(x)
    19504: ["name", "pwd", "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "",
            "javascript:onclickDiscount('20200407090327-00361', '00009', '당일 무료', '56너0427', '매수차감', form1.remark.value);",
            "javascript:onclickDiscount('20200407090327-00361', '00009', '당일 무료', '56너0427', '매수차감', form1.remark.value);"],
    # 소노타워  (x)
    19505: ["name", "pwd", "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "",
            "javascript:onclickDiscount('20200407090327-00361', '00009', '당일 무료', '56너0427', '매수차감', form1.remark.value);",
            "javascript:onclickDiscount('20200407090327-00361', '00009', '당일 무료', '56너0427', '매수차감', form1.remark.value);"],
    # 	롯데마트 고양점(x)
    19499: ["name", "pwd", "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "",
            "javascript:onclickDiscount('20200407090327-00361', '00009', '당일 무료', '56너0427', '매수차감', form1.remark.value);",
            "javascript:onclickDiscount('20200407090327-00361', '00009', '당일 무료', '56너0427', '매수차감', form1.remark.value);"],
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

    if ticket_name == "직접주차":
        print(Colors.BLUE + "직접주차입니다." + Colors.ENDC)
        return False
    #발산 연박 개수대로 수동 넣어주어야함
    if ("연박용" in ticket_name ) and park_id == 19070 :
        print(Colors.BLUE + "발산파크 연박권입니다." + Colors.ENDC)
        return False
    #순화빌딩 9170 LPR 인식 문제
    # if park_id == 16173 and ori_car_num =='11다9170' :
    #     print(Colors.BLUE + "웹할인 확인이 필요한 차량입니다" + Colors.ENDC)
    #     return False

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

            if park_id == 19087:
                try:
                    tr_text = driver.find_element_by_css_selector(
                        "body > table:nth-child(5) > tbody > tr:nth-child(2) > td:nth-child(2) > p:nth-child(2)").text

                    text = re.sub('<.+?>', '', tr_text, 0, re.I | re.S)
                    trim_text = text.strip()
                    split_trim_text = trim_text.split(":")
                    search_day_text = split_trim_text[1].strip()

                    today = datetime.datetime.now()
                    today_text = today.strftime('%Y-%m-%d')

                    if today_text == search_day_text:
                        driver.find_element_by_xpath("/html/body/table[2]/tbody/tr[2]").click()
                    else:
                        print(Colors.BLUE + "금일 날짜에 맞는 데이터가 없습니다." + Colors.ENDC)
                        return False
                except NoSuchElementException as ex:
                    print(Colors.BLUE + "날짜 선택을 건너뜁니다. " + ex.msg + Colors.ENDC)
                try:
                    tr_text = driver.find_element_by_css_selector("body > table:nth-child(5) > tbody > tr:nth-child(3) > td:nth-child(2)").text
                    text = re.sub('<.+?>', '', tr_text, 0, re.I | re.S)
                    trim_text = text.strip()

                    split_trim_text = trim_text.split()
                    trim_text = split_trim_text[3]

                    if ori_car_num[-7:] == trim_text[-7:]:

                        if park_id == 19497:
                            driver.find_element_by_xpath("/html/body/table[2]/tbody/tr[5]/td[1]/p[6]/input").click()
                        else:
                            print(Colors.BLUE + "할인권 버튼을 찾을 수 없습니다." + Colors.ENDC)
                            return False
                    driver.implicitly_wait(3)
                    alert = Alert(driver)
                    alert.accept()
                    driver.implicitly_wait(3)
                    return True

                except NoSuchElementException as ex:
                    print(Colors.RED + "예외 발생 : " + ex.msg + Colors.ENDC)
                    print(Colors.BLUE + "검색결과가 없습니다." + Colors.ENDC)
                    return False
                try:
                    tr_text = driver.find_element_by_css_selector(
                        "body > table:nth-child(5) > tbody > tr:nth-child(2) > td:nth-child(2) > p:nth-child(2)").text

                    text = re.sub('<.+?>', '', tr_text, 0, re.I | re.S)
                    trim_text = text.strip()
                    split_trim_text = trim_text.split(":")
                    search_day_text = split_trim_text[1].strip()

                    today = datetime.datetime.now()
                    today_text = today.strftime('%Y-%m-%d')

                    if today_text == search_day_text:
                        driver.find_element_by_css_selector("body > table:nth-child(5) > tbody > tr:nth-child(2)").click()
                    else:
                        print(Colors.BLUE + "금일 날짜에 맞는 데이터가 없습니다." + Colors.ENDC)
                        return False
                except NoSuchElementException as ex:
                    print(Colors.BLUE + "날짜 선택을 건너뜁니다. " + ex.msg + Colors.ENDC)
            else:
                # 차량 번호 검색 및 비교 시도
                try:
                    tr_text = driver.find_element_by_css_selector(
                        "body > table:nth-child(4) > tbody > tr:nth-child(3) > td:nth-child(2)").text

                    text = re.sub('<.+?>', '', tr_text, 0, re.I | re.S)
                    trim_text = text.strip()
                    split_trim_text = trim_text.split()
                    trim_text = split_trim_text[3]
                    print(Colors.RED + "예외 발생 : " + tr_text)
                    if ori_car_num[-7:] == trim_text[-7:]:
                        # harin_script = get_har_in_script(park_id, ticket_name)
                        # driver.execute_script(harin_script)
                        if park_id == Parks.GMG_TOWER:
                            if ticket_name == '평일1일권' or ticket_name == '주말1일권':
                                driver.find_element_by_id("BTN_당일 무료").click()
                            else:
                                print(Colors.BLUE + "연박권 " + Colors.ENDC)
                                return False
                        elif park_id == 19087 or park_id == 19070:
                            driver.find_element_by_xpath("/html/body/table[2]/tbody/tr[4]/td[1]/p[1]/input").click()

                        else:
                            print(Colors.BLUE + "할인권 버튼을 찾을 수 없습니다." + Colors.ENDC)
                            return False
                        driver.implicitly_wait(3)
                        alert = Alert(driver)
                        alert.accept()
                        driver.implicitly_wait(3)
                        return True

                except NoSuchElementException as ex:
                    print(Colors.RED + "예외 발생 : " + ex.msg + Colors.ENDC)
                    print(Colors.BLUE + "검색결과가 없습니다." + Colors.ENDC)
                    return False

                return False



            if park_id == 19497:
                try:
                    tr_text = driver.find_element_by_css_selector("body > table:nth-child(5) > tbody > tr:nth-child(3) > td:nth-child(2)").text
                    text = re.sub('<.+?>', '', tr_text, 0, re.I | re.S)
                    trim_text = text.strip()

                    split_trim_text = trim_text.split()
                    trim_text = split_trim_text[3]

                    if ori_car_num[-7:] == trim_text[-7:]:

                        if park_id == 19497:
                            driver.find_element_by_xpath("/html/body/table[2]/tbody/tr[5]/td[1]/p[6]/input").click()
                        else:
                            print(Colors.BLUE + "할인권 버튼을 찾을 수 없습니다." + Colors.ENDC)
                            return False
                    driver.implicitly_wait(3)
                    alert = Alert(driver)
                    alert.accept()
                    driver.implicitly_wait(3)
                    return True

                except NoSuchElementException as ex:
                    print(Colors.RED + "예외 발생 : " + ex.msg + Colors.ENDC)
                    print(Colors.BLUE + "검색결과가 없습니다." + Colors.ENDC)
                    return False




        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
