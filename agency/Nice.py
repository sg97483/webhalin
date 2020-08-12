# -*- coding: utf-8 -*-

import Util
import ParkType
import Colors

Parks = ParkType.Parks


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

    parkingpark_url = "http://cafe.wisemobile.kr/manager"
    nice_url = "http://cafe.wisemobile.kr/manager/adm/wz_booking_admin/parkingpark_nice_web_harin.php"

    driver.get(parkingpark_url)

    try:
        driver.find_element_by_id("ol_id").send_keys("admin")
        driver.find_element_by_id("ol_pw").send_keys("@park0413")
        driver.find_element_by_id("ol_submit").click()
    except Exception as ex:
        print(Colors.RED + str(ex) + Colors.ENDC)

    driver.get(nice_url)
    driver.find_element_by_name('stx').send_keys(search_id)
    driver.find_element_by_xpath('//*[@id="fsearch"]/input').click()
    searched_car_number = driver.find_element_by_xpath('/html/body/table[1]/tbody/tr[2]/td[1]/font/b').text
    print(searched_car_number)

    if ori_car_num[-7:] == searched_car_number[-7:]:
        if ticket_name == '평일1일권':
            driver.find_element_by_css_selector(
                'body > table:nth-child(11) > tbody > tr:nth-child(2) > td:nth-child(11) > b:nth-child(3) > a > font').click()
        else:
            driver.find_element_by_css_selector(
                'body > table:nth-child(11) > tbody > tr:nth-child(2) > td:nth-child(11) > b:nth-child(1) > a > font').click()

        try:
            driver.find_element_by_css_selector("#modal-window > div > div > div.modal-buttons > a").click()
        except Exception as ex:
            print(Colors.RED + str(ex) + Colors.ENDC)

        return True

    else:
        print(Colors.MARGENTA + "차량번호가 틀립니다." + Colors.ENDC)
        return False
