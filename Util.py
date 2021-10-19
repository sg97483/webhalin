# -*- coding: utf-8 -*-
import time
import datetime

from selenium.common.exceptions import NoSuchElementException

import Colors


def all_trim(temp_str):
    return ''.join(str(temp_str).split())


def sleep(second):
    time.sleep(second)


def get_week_or_weekend():
    now = datetime.datetime.now()

    if now.weekday() < 5:
        week_or_weekend = 0
    else:
        week_or_weekend = 1

    # 공휴일 일 경우
    # week_or_weekend = 1

    return week_or_weekend


def click_element_id(element_id, driver):
    element = driver.find_element_by_id(element_id)
    driver.execute_script("arguments[0].click();", element)


def click_element_xpath(element_xpath, driver):
    element = driver.find_element_by_xpath(element_xpath)
    driver.execute_script("arguments[0].click();", element)


def click_element_selector(element_selector, driver):
    element = driver.find_element_by_css_selector(element_selector)
    driver.execute_script("arguments[0].click();", element)


def input_element_id(element_id, driver, search_id):
    element = driver.find_element_by_id(element_id)
    driver.execute_script("arguments[0].click();", element)
    element.send_keys(search_id)


def close_modal(driver):
    try:
        driver.find_element_by_css_selector(
            "#modal-window > div > div > div.modal-buttons > a").click()
        sleep(2)
    except NoSuchElementException:
        print(Colors.RED + "모달(팝업)을 닫을 수 없습니다." + Colors.ENDC)


def close_popup(driver):
    try:
        sleep(3)
        popups = driver.window_handles
        print(popups)
        for popup in popups:
            if popup != popups[0]:
                driver.switch_to_window(popup)
                driver.close()

        driver.switch_to_window(driver.window_handles[0])

    except NoSuchElementException:
        print(Colors.RED + "모달(팝업)을 닫을 수 없습니다." + Colors.ENDC)

