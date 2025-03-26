# -*- coding: utf-8 -*-
import re
import time

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import Util
import Colors

value_client_code = '0005'
value_access_token = 'BNQ8gkHyk0Rd52ioTYAGKg=='
headers = {'Content-Type': 'application/json; chearset=utf-8'}

nice_url = "http://cafe.wisemobile.kr/manager/adm/wz_booking_admin/parkingpark_nice_web_harin.php"
url_search_car = 'https://npmu.nicepark.co.kr/api/v0/parkinglots/cars'
url_register_sale = 'https://npmu.nicepark.co.kr/api/v0/parkinglots/cars/discounts'


def web_har_in(target, driver):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]

    trim_car_num = Util.all_trim(ori_car_num)
    search_id = trim_car_num[-4:]

    print("parkId = " + str(park_id) + ", " + "searchId = " + search_id)
    print(Colors.BLUE + ticket_name + Colors.ENDC)

    driver.get(nice_url)
    time.sleep(3)

    # 처음 로그인 팝업 확인
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' + 'confirmation popup to appear.')
        driver.switch_to.alert.accept()
        time.sleep(3)
    except TimeoutException:
        print("no alert")

    # 로그인
    try:
        driver.find_element_by_id("login_id").send_keys("admin")
        driver.find_element_by_id("login_pw").send_keys("@!#park0413")
        driver.find_element_by_xpath("""//*[@id="login_fs"]/input[3]""").click()
        driver.implicitly_wait(3)
    except Exception as ex:
        print(Colors.RED + str(ex) + Colors.ENDC)

    driver.get(nice_url)

    driver.find_element_by_name('stx').send_keys(search_id)
    driver.find_element_by_xpath('//*[@id="fsearch"]/input').click()

    time.sleep(2)
    count = len(driver.find_elements_by_xpath("/html/body/table[1]/tbody/tr"))

    # 차량리스트 검색 for문
    for index in range(2, count + 1):
        sale_table = driver.find_element_by_xpath("/html/body/table[1]/tbody/tr[" + str(index) + "]")
        searched_car_number = driver.find_element_by_xpath(
            "/html/body/table[1]/tbody/tr[" + str(index) + "]/td[1]").text
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
            print("차량 번호 같음")
            print("index = " + str(index))
            sale_count = len(driver.find_elements_by_xpath("/html/body/table[1]/tbody/tr[" + str(index) + "]/td[11]/b"))
            print("sale_count : " + str(sale_count))

            # 할인권리스트 for문
            for sale_index in range(1, sale_count + 1):
                sale_text = driver.find_element_by_xpath(
                    "/html/body/table[1]/tbody/tr[" + str(index) + "]/td[11]/b[" + str(sale_index) + "]")
                print(sale_text.text)

                # 1일권
                if str(ticket_name).endswith('1일권') or str(ticket_name).endswith('당일권'):
                    if sale_text.text == '입차일 당일':
                        sale_text.click()
                        try:
                            driver.find_element_by_css_selector(
                                "#modal-window > div > div > div.modal-buttons > a").click()
                        except Exception as ex:
                            print(Colors.RED + str(ex) + Colors.ENDC)
                        return True
                    else:
                        continue

                # 심야권
                elif str(ticket_name).endswith('심야권') or str(ticket_name).endswith('야간권'):
                    if str(sale_text.text).startswith('17') and str(sale_text.text)[6] == '0':
                        sale_text.click()
                        try:
                            driver.find_element_by_css_selector(
                                "#modal-window > div > div > div.modal-buttons > a").click()
                        except Exception as ex:
                            print(Colors.RED + str(ex) + Colors.ENDC)
                        return True
                    elif str(sale_text.text).startswith('18') and str(sale_text.text)[6] == '0':
                        sale_text.click()
                        try:
                            driver.find_element_by_css_selector(
                                "#modal-window > div > div > div.modal-buttons > a").click()
                        except Exception as ex:
                            print(Colors.RED + str(ex) + Colors.ENDC)
                        return True
                    elif str(sale_text.text).startswith('19') and str(sale_text.text)[6] == '0':
                        sale_text.click()
                        try:
                            driver.find_element_by_css_selector(
                                "#modal-window > div > div > div.modal-buttons > a").click()
                        except Exception as ex:
                            print(Colors.RED + str(ex) + Colors.ENDC)
                        return True
                    elif str(sale_text.text).startswith('20') and str(sale_text.text)[6] == '0':
                        sale_text.click()
                        try:
                            driver.find_element_by_css_selector(
                                "#modal-window > div > div > div.modal-buttons > a").click()
                        except Exception as ex:
                            print(Colors.RED + str(ex) + Colors.ENDC)
                        return True
                    elif (str(sale_text.text).startswith('22') and str(sale_text.text)[6:].startswith(
                            '10')):  # 나이스파크 월피점
                        sale_text.click()
                        try:
                            driver.find_element_by_css_selector(
                                "#modal-window > div > div > div.modal-buttons > a").click()
                        except Exception as ex:
                            print(Colors.RED + str(ex) + Colors.ENDC)
                        return True
                    else:
                        continue

                # 3시간권
                elif str(ticket_name).endswith('3시간권'):
                    if sale_text.text == '3시간':
                        sale_text.click()
                        try:
                            driver.find_element_by_css_selector(
                                "#modal-window > div > div > div.modal-buttons > a").click()
                        except Exception as ex:
                            print(Colors.RED + str(ex) + Colors.ENDC)
                        return True
                    else:
                        continue

                # 부천 시네마존 평일 오후권
                elif park_id == 19296 and str(ticket_name).endswith('오후권'):
                    if str(sale_text.text).startswith('08'):
                        sale_text.click()
                        try:
                            driver.find_element_by_css_selector(
                                "#modal-window > div > div > div.modal-buttons > a").click()
                        except Exception as ex:
                            print(Colors.RED + str(ex) + Colors.ENDC)
                        return True
                else:
                    continue

            print("할인권 적용 실패")
            return False
        else:
            print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)
            continue

        return False
    return False
