# -*- coding: utf-8 -*-
import re
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import Util
from park import ParkType, Parks, ParkUtil
import Colors
import requests
import json

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

    if str(ticket_name).endswith('1일권'):
        driver.get(nice_url)
        time.sleep(3)
        try:
            # wait for the alert to show up
            WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                           'Timed out waiting for PA creation ' +
                                           'confirmation popup to appear.')
            # if it does
            driver.switch_to.alert.accept()
            time.sleep(3)
        except TimeoutException:
            print("no alert")
        try:
            driver.find_element_by_id("login_id").send_keys("admin")
            driver.find_element_by_id("login_pw").send_keys("!@park0413")
            driver.find_element_by_xpath("""//*[@id="login_fs"]/input[3]""").click()
            driver.implicitly_wait(3)
        except Exception as ex:
            print(Colors.RED + str(ex) + Colors.ENDC)

        driver.get(nice_url)

        driver.find_element_by_name('stx').send_keys(search_id)
        driver.find_element_by_xpath('//*[@id="fsearch"]/input').click()
        # try:
        #     searched_car_number = driver.find_element_by_xpath('/html/body/table[1]/tbody/tr[2]/td[1]/font/b').text
        # except NoSuchElementException as ex:
        #     print("차량이 검색되지 않음\n" + ex)

        time.sleep(2)
        count = len(driver.find_elements_by_xpath("/html/body/table[1]/tbody/tr"))

        for index in range(2, count+1):
            sale_table = driver.find_element_by_xpath("/html/body/table[1]/tbody/tr[" + str(index) + "]")
            searched_car_number = driver.find_element_by_xpath("/html/body/table[1]/tbody/tr[" + str(index) + "]/td[1]").text
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
                for sale_index in range(1, sale_count+1):
                    sale_text = driver.find_element_by_xpath("/html/body/table[1]/tbody/tr[" + str(index) + "]/td[11]/b["+str(sale_index)+"]")
                    print(sale_text.text)
                    if (sale_text.text == '입차일 당일'):
                        sale_text.click()
                        try:
                            driver.find_element_by_css_selector(
                                "#modal-window > div > div > div.modal-buttons > a").click()
                        except Exception as ex:
                            print(Colors.RED + str(ex) + Colors.ENDC)
                        return True
                    else:
                        continue

            else:
                print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)
                continue


            # for trs in sale_table.find_elements_by_tag_name("tr"):
            #     print(trs)
            #     # 테이블 헤더 제외
            #     if index==0:
            #         index = index+1
            #         continue
            #
            #     # 검색 결과 <tr>
            #     elif index > 0:
            #         tds = trs.find_element_by_tag_name("td")
            #         searched_car_number = tds.text
            #         print("나누기전 : " + searched_car_number)
            #         td_car_num_1 = re.sub('<.+?>', '', searched_car_number, 0, re.I | re.S)
            #         td_car_num_2 = td_car_num_1.strip()
            #         td_car_num_3 = td_car_num_2.split('\n')
            #
            #         global td_car_num
            #         if len(td_car_num_3[0].split(' ')) > 1:
            #             td_car_num = td_car_num_3[0].split(' ')[0][-7:]
            #         else:
            #             td_car_num = td_car_num_3[0][-7:]
            #
            #         print("검색된 차량번호 : " + td_car_num + " == " + "기존 차량번호 : " + ori_car_num + " / " + ori_car_num[-7:])
            #
            #         if ori_car_num[-7:] == td_car_num or ori_car_num == td_car_num:
            #             print("차량 번호 같음")
            #             for sale_b in tds[10].find_elements_by_tag_name('b'):
            #                 if(sale_b.text == '입차일 당일'):
            #                     driver.find_element_by_css_selector(sale_b).click()
            #                     try:
            #                         driver.find_element_by_css_selector(
            #                             "#modal-window > div > div > div.modal-buttons > a").click()
            #                     except Exception as ex:
            #                         print(Colors.RED + str(ex) + Colors.ENDC)
            #                     return True
            #
            #         else:
            #             print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)
            #             index = index + 1
            #             continue

            return False
        return False


    else:
        print("나이스 - (평일/주말)1일권이 아님")
        return False

# sale_table = temp_table.find_all('b')

# for list in sale_table:
#     print(list.text)
#     if (list.text == '입차일 당일'):
#         list.click()
#         try:
#             driver.find_element_by_css_selector("#modal-window > div > div > div.modal-buttons > a").click()
#         except Exception as ex:
#             print(Colors.RED + str(ex) + Colors.ENDC)
#         return True
