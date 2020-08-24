# -*- coding: utf-8 -*-
import re

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import Util
import ParkType
import Colors
import ParkUtil
import WebInfo

Parks = ParkType.Parks

mapIdToWebInfo = {
    # (하이파킹) 웨스턴853오피스텔
    18999: ["id", "pw", "//*[@id='blurExample']/div/div/form/input[2]",
            "//*[@id='discount']/div[1]/input[1]", "",
            "",
            "javascript:insertDiscount();",
            "javascript:insertDiscount();"],
    # 드림타워 평일 심야권
    18930: ["user_id", "passwd", "//*[@id='login_div']/table/tbody/tr/td",
            "_search_Str", "/html/body/table[2]/tbody/tr[1]/td/form/table/tbody/tr[9]/td/table[2]/tbody/tr/td[5]/input",
            "",
            "javascript:show_notice3('13시간할인','780','N')",
            "javascript:show_notice3('13시간할인','780','N')"],
    # 드림타워 주말권
    19120: ["user_id", "passwd", "//*[@id='login_div']/table/tbody/tr/td",
            "_search_Str", "/html/body/table[2]/tbody/tr[1]/td/form/table/tbody/tr[9]/td/table[2]/tbody/tr/td[5]/input",
            "",
            "javascript:show_notice3('주말종일권','8000','')",
            "javascript:show_notice3('주말종일권','8000','')"],
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
            if park_id == Parks.WESTERN_853:
                if ParkUtil.check_first_conn(park_id):
                    driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
                    driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])

                    driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()

                driver.implicitly_wait(3)

                driver.find_element_by_xpath(web_info[WebInfo.inputSearch]).send_keys(search_id)
                driver.implicitly_wait(3)

                try:
                    park_search_css = "#discount > div.mb-3.inline > ul > li.list-group > a"

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
                            try:
                                driver.find_element_by_css_selector('#discount > div.mb-3.inline > ul > li.list-group > a:nth-child(1)').click()
                            except NoSuchElementException:
                                print("웨스턴853 여러 개 차량번호 클릭 실패")

                            harin_script = get_har_in_script(park_id, ticket_name)
                            driver.execute_script(harin_script)
                            return True
                        else:
                            print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)
                            return False

                except NoSuchElementException:
                    print(Colors.GREEN + "해당 엘리멘트가 존재하지 않습니다." + Colors.ENDC)
                    return False

            elif park_id == Parks.DREAM_TOWER_NIGHT or park_id == Parks.DREAM_TOWER_HOLIDAY:
                # Login
                driver.find_element_by_name('frm').click()
                driver.implicitly_wait(3)
                driver.find_element_by_name(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
                driver.find_element_by_name(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])
                driver.execute_script('javascript:checkLogin();')
                driver.implicitly_wait(3)
                # Search
                driver.find_element_by_name(web_info[WebInfo.inputSearch]).send_keys(search_id)
                driver.find_element_by_name(web_info[WebInfo.inputSearch]).send_keys(Keys.ENTER)
                driver.implicitly_wait(3)

                try:
                    park_search_css = "body > table:nth-child(5) > tbody > tr:nth-child(2) > td:nth-child(2)"

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
                            driver.implicitly_wait(3)
                            harin_script = get_har_in_script(park_id, ticket_name)
                            driver.execute_script(harin_script)
                            driver.implicitly_wait(3)
                            ok_button = 'body > form > table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > td > input'
                            driver.find_element_by_css_selector(ok_button).click()
                            return True
                        else:
                            print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)

                except NoSuchElementException:
                    print(Colors.GREEN + "해당 엘리멘트가 존재하지 않습니다." + Colors.ENDC)

                return False

        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
