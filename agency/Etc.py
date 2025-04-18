# -*- coding: utf-8 -*-
import datetime
import re

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import Util
import Colors
from park import ParkUtil, ParkType, Parks
import WebInfo

mapIdToWebInfo = {
    # (하이파킹) 웨스턴853오피스텔
    18999: ["""//*[@id='sc-login-form']/div/div[1]/div/input""", """//*[@id='sc-login-form']/div/div[2]/div/input""", """//*[@id="sc-login-form"]/div/div[3]/a""",
            """//*[@id="sc-page-content"]/div/div/div/div[2]/div/div[1]/div/input""", "",
            "",
            "",
            ""],

    #하이파킹 종로플레이스
    19427: ["""//*[@id="sc-login-form"]/div/div[1]/div/input""", """//*[@id="sc-login-form"]/div/div[2]/div/input""", """//*[@id="sc-login-form"]/div/div[3]/a""",
            """//*[@id="sc-page-content"]/div/div/div/div[2]/div/div[1]/div/input""", "",
            "",
            "",
            ""],


}


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

            # 재접속이 아닐 때, 그러니까 처음 접속할 때
            if park_id == Parks.WESTERN_853 or park_id == Parks.HUMAX_VILLAGE or park_id==19427:
                if ParkUtil.check_first_conn(park_id):
                    driver.find_element_by_xpath(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
                    driver.find_element_by_xpath(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])
                    driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()
                #로그인완료
                driver.implicitly_wait(3)

                #차번호입력
                driver.find_element_by_xpath(web_info[WebInfo.inputSearch]).send_keys(search_id)
                driver.implicitly_wait(3)
                Util.sleep(2)
                try:
                    tr_text = driver.find_element_by_css_selector("#sc-page-content > div > div > div > div.uk-card-body > div > div.uk-width-1-1.uk-grid-margin.uk-first-column > div > table > tbody > tr:nth-child(1) > td:nth-child(1) > span").text
                    text = re.sub('<.+?>', '', tr_text, 0, re.I | re.S)
                    trim_text = text.strip()
                    # print(trim_text)
                    if trim_text.startswith("검색") or trim_text.startswith("입차") or trim_text.startswith("차량"):
                        print(Colors.YELLOW + "미입차" + Colors.ENDC)
                        return False
                    else:
                        td_car_num_0 = driver.find_element_by_css_selector("#sc-page-content > div > div.uk-width-1-3\@l.uk-first-column > div > div.uk-card-body > div > div.uk-width-1-1.uk-grid-margin.uk-first-column > div > table > tbody > tr:nth-child(1) > td:nth-child(1) > span").text
                        td_car_num_1 = re.sub('<.+?>', '', td_car_num_0, 0, re.I | re.S)
                        td_car_num_2 = td_car_num_1.strip()
                        td_car_num_3 = td_car_num_2.split('\n')
                        td_car_num = td_car_num_3[0][-7:]

                        print("검색된 차량번호 : " + td_car_num + " == " + "기존 차량번호 : " + ori_car_num + " / " + ori_car_num[-7:])
                        search_date_text = driver.find_element_by_xpath("""//*[@id="sc-page-content"]/div/div[1]/div/div[2]/div/div[2]/div/table/tbody/tr[1]/td[2]""").text
                        now = datetime.datetime.now()

                        nowDate = now.strftime('%m%d')
                        search_date = search_date_text[5:7]+search_date_text[8:10]

                        if ori_car_num[-7:] == td_car_num:
                            # 웹할인 페이지 리스트의 입차날짜와 현재날짜 비교
                            if nowDate == search_date:
                                driver.implicitly_wait(2)
                                Util.sleep(1)
                                try:
                                    driver.find_element_by_css_selector('#scrollbar > div > table > tbody > tr > td:nth-child(1)').click()
                                    driver.find_element_by_xpath('//*[@id="sc-page-content"]/div/div[2]/div/div[2]/div/div[1]/div[2]/div/div/div/div[1]').click()
                                except NoSuchElementException:
                                    print("웨스턴853/휴맥스빌리지/공덕푸르지오시티 여러 개 차량번호 클릭 실패")
                                    return False
                                return True
                            else:
                                print(Colors.MARGENTA + "입차날짜가 틀립니다." + Colors.ENDC)
                                return False
                        else:
                            print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)
                            return False

                except NoSuchElementException:
                    print(Colors.GREEN + "해당 엘리멘트가 존재하지 않습니다." + Colors.ENDC)
                    return False


            elif park_id == park_id == 19170:
                if ParkUtil.check_first_conn(park_id):
                    driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
                    driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])

                    driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()

                driver.implicitly_wait(2)
                driver.find_element_by_id("ContentPlaceHolder1_btnParking").click()
                driver.implicitly_wait(2)

                if(park_id == 19170):
                    driver.find_element_by_id("ContentPlaceHolder1_Repeater1_btnParkCd_0").click()
                driver.implicitly_wait(2)

                driver.find_element_by_id("txtInCardNo").click()
                driver.execute_script("document.getElementById('txtInCardNo').innerHTML = '" + search_id + "';")
                driver.implicitly_wait(2)
                driver.find_element_by_xpath("//*[@id='form1']/div[5]/div[1]/div/div[2]/div[2]/button").click()
                driver.implicitly_wait(2)

                try:
                    park_search_css = "#form1 > div.wrap > div > div > div.car-select-list-wrap > ul > li > label > div.car-number"

                    tr_text = driver.find_element_by_css_selector(park_search_css).text
                    text = re.sub('<.+?>', '', tr_text, 0, re.I | re.S)
                    trim_text = text.strip()
                    # print(trim_text)
                    if trim_text.startswith("검색") or trim_text.startswith("입차") or trim_text.startswith("차량"):
                        print(Colors.YELLOW + "미입차" + Colors.ENDC)
                        return False
                    else:
                        td_car_num_0 = driver.find_element_by_css_selector(park_search_css).text
                        td_car_num_1 = re.sub('<.+?>', '', td_car_num_0, 0, re.I | re.S)
                        td_car_num_2 = td_car_num_1.strip()
                        td_car_num_3 = td_car_num_2.split('\n')
                        td_car_num = td_car_num_3[0][-7:]

                        print("검색된 차량번호 : " + td_car_num + " == " + "기존 차량번호 : " + ori_car_num + " / " + ori_car_num[-7:])

                        if ori_car_num[-7:] == td_car_num:
                            driver.find_element_by_css_selector(park_search_css).click()
                            driver.implicitly_wait(2)
                            driver.execute_script("javascript:next()")
                            driver.implicitly_wait(2)
                            try:
                                driver.find_element_by_xpath("//*[@id='form1']/div[17]/div/div/div[2]/div[1]/button").click()
                                driver.implicitly_wait(2)
                                driver.execute_script(web_info[6])
                                Util.sleep(2)
                            except:
                                print("할인권 적용 안됨")
                                return False


                            driver.implicitly_wait(2)
                            driver.execute_script('javascript:validate();')
                            driver.implicitly_wait(2)
                            driver.execute_script('javascript:confirm();')
                            driver.implicitly_wait(2)
                            driver.execute_script("javascript:goLink('Ticket_CheckPoint.aspx', true);")
                            driver.implicitly_wait(2)
                            Util.sleep(2)
                            return True
                        else:
                            print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)
                            return False

                except NoSuchElementException:
                    print(Colors.GREEN + "해당 엘리멘트가 존재하지 않습니다." + Colors.ENDC)
                    return False

        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False