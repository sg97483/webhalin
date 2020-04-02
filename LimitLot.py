# -*- coding: utf-8 -*-
import Colors

main_url = "http://cafe.wisemobile.kr/manager/"
limit_lot_url = "http://cafe.wisemobile.kr/manager/adm/wz_booking_admin/check_parkingLot_count.php"


def do_limit_lot(driver):
    driver.get(main_url)

    try:
        driver.find_element_by_id("ol_id").send_keys("admin")
        driver.find_element_by_id("ol_pw").send_keys("wise0413")
        driver.find_element_by_id("ol_submit").click()
    except Exception as ex:
        print(Colors.RED + str(ex) + Colors.ENDC)

    driver.get(limit_lot_url)