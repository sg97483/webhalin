# -*- coding: utf-8 -*-
import Util
import ParkType
import Colors
import ParkUtil
import WebInfo

mapIdToWebInfo = {
    # 마곡 GMG주차타워
    19071: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('10', '1', '', '어플평일당일권(웹할인)', '1', '0');",
            "javascript:applyDiscount('09', '1', '', '어플주말당일권(웹할인)', '1', '0');"],
    # (하이파킹) 순화빌딩 주차장
    16173: ["name", "pwd", "//*[@id='login']/table/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "/html/body/table[2]/tbody/tr[2]",
            "body > table:nth-child(4) > tbody > tr:nth-child(4) > td:nth-child(1) > p:nth-child(3) > input[type=button]",
            "body > table:nth-child(4) > tbody > tr:nth-child(4) > td:nth-child(1) > p:nth-child(3) > input[type=button]"],
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
            # todo 현재 URL을 가지고와서 비교 후 자동로그인
            # print(driver.current_url)
            # 재접속이 아닐 때, 그러니까 처음 접속할 때
            if ParkUtil.first_access(park_id, driver.current_url):

                driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
                driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])

                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()

                # discount_url = login_url + ParkUtil.get_park_discount_url(park_type)
                # driver.get(discount_url)

                driver.implicitly_wait(3)

                driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
                Util.sleep(3)

                driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()

                Util.sleep(1)

                if ParkUtil.check_search(
                        "#search_form > table > tbody > tr > td:nth-child(2) > table:nth-child(3) > tbody > "
                        "tr:nth-child(2)",
                        driver):
                    if ParkUtil.check_same_car_num(park_id, ori_car_num, driver):
                        driver.find_element_by_id(web_info[WebInfo.btnItem]).click()
                        harin_script = get_har_in_script(park_id, ticket_name)
                        driver.execute_script(harin_script)
                        return True

                return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
