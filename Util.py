# -*- coding: utf-8 -*-
import time
import datetime


def all_trim(temp_str):
    return ''.join(temp_str.split())


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
