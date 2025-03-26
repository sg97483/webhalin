# -*- coding: utf-8 -*-
from selenium.webdriver import ActionChains
from selenium.webdriver.common import alert
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


import Util
import Colors
from park import ParkUtil, ParkType
import WebInfo

mapIdToWebInfo = {
    # 센터스퀘어등촌
    19426: ["t_userid", "t_pwd", "//*[@id='btn_login-btnInnerEl']",
            "f_carno", "//*[@id='btnFind']","95"
            ]

}


def click_har_in_script(ticke_name, driver):

    if ticke_name == "평일 당일권":
        driver.find_element_by_xpath("//*[@id='tbData_dckey']/tbody/tr[1]/td/button").click()
        return True
    elif ticke_name == "심야권":
        driver.find_element_by_xpath("/html/body/table[2]/tbody/tr[5]/td[1]/p[2]/input").click()
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

                print(Colors.BLUE + "센터스퀘어 진입" + Colors.ENDC)

                driver.implicitly_wait(3)

                driver.find_element_by_name(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
                driver.find_element_by_name(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])

                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()

                driver.implicitly_wait(3)

                driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
                Util.sleep(3)

                #driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()

                #Util.sleep(3)

                driver.find_element_by_xpath("//*[@id='tbData']/tbody/tr/td[1]/div").click()

                driver.implicitly_wait(3)

                print(Colors.BLUE + "개발테스트4" + Colors.ENDC)

                if (ticket_name == "평일 당일권"):
                    #Util.sleep(3)

                    driver.implicitly_wait(10)

                    element = driver.find_element_by_xpath("//button[@name='btnDckey' and @value='95']")
                    driver.execute_script("arguments[0].click();", element)

                    driver.implicitly_wait(5)

                    alert = Alert(driver)
                    alert.accept()

                    driver.implicitly_wait(2)

                    return True

                elif (ticket_name == "평일 오후6시간권"):

                    driver.implicitly_wait(10)

                    element = driver.find_element_by_xpath("//button[@name='btnDckey' and @value='75']")
                    driver.execute_script("arguments[0].click();", element)

                    driver.implicitly_wait(5)

                    alert = Alert(driver)
                    alert.accept()

                    driver.implicitly_wait(2)

                    return True

                elif (ticket_name == "오전 3시간권"):

                    driver.implicitly_wait(10)

                    element = driver.find_element_by_xpath("//button[@name='btnDckey' and @value='30']")
                    driver.execute_script("arguments[0].click();", element)

                    driver.implicitly_wait(5)

                    alert = Alert(driver)
                    alert.accept()

                    driver.implicitly_wait(2)

                    return True


                elif (ticket_name == "휴일 당일권"):

                    driver.implicitly_wait(10)

                    element = driver.find_element_by_xpath("//button[@name='btnDckey' and @value='86']")
                    driver.execute_script("arguments[0].click();", element)

                    driver.implicitly_wait(5)

                    alert = Alert(driver)
                    alert.accept()

                    driver.implicitly_wait(2)

                    return True


           # return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다.!" + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다.!" + Colors.ENDC)
        return False
