# -*- coding: utf-8 -*-
import Util
import ParkType
import Colors
import ParkUtil
import WebInfo

mapIdToWebInfo = {
    # GRANG_SEOUL 그랑서울
    12872: ["j_username", "j_password", "/html/body/div[2]/div/div/form/button[1]/i",
            "car_no", "//*[@id='frm']/div/button"
            ]
}


def click_har_in_script(ticke_name, driver):
    if ticke_name == "4시간권":
        driver.find_element_by_xpath("//*[@id='discount_click_name' and @value='4시간쿠폰']").click()
        return True
    elif ticke_name == "저녁권" or ticke_name == "6시간권":
        driver.find_element_by_xpath("//*[@id='discount_click_name' and @value='4시간쿠폰']").click()
        driver.find_element_by_xpath("//*[@id='discount_click_name' and @value='2시간쿠폰']").click()
        return True
    elif ticke_name.startswith("12시간"):
        driver.find_element_by_xpath("//*[@id='discount_click_name' and @value='4시간쿠폰']").click()
        driver.find_element_by_xpath("//*[@id='discount_click_name' and @value='4시간쿠폰']").click()
        driver.find_element_by_xpath("//*[@id='discount_click_name' and @value='4시간쿠폰']").click()
        return True
    else:
        print("유효하지 않는 주차권 입니다.")
        return False


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
                driver.find_element_by_name(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
                driver.find_element_by_name(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])

                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()

                # discount_url = login_url + ParkUtil.get_park_discount_url(park_type)
                # driver.get(discount_url)

                driver.implicitly_wait(3)

            driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
            Util.sleep(3)

            driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()

            Util.sleep(1)

            if ParkUtil.check_search(park_id, driver):
                if ParkUtil.check_same_car_num(park_id, ori_car_num, driver):
                    driver.find_element_by_css_selector("#carList > table > tbody > tr > td:nth-child(2) > a").click()
                    # 할인권 기입 후 등록 체크
                    #
                    # driver.find_element_by_id(web_info[WebInfo.btnItem]).click()
                    if click_har_in_script(ticket_name, driver):
                        driver.find_element_by_id("insertSubmit").click()
                        return True

            return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
