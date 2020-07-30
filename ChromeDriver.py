# -*- coding: utf-8 -*-
from selenium import webdriver


def get():
    chrome_driver = '/Users/user/PycharmProjects/parkingpark-macro/parkingpark-macro/venv2/driver/chromedriver'
    return webdriver.Chrome(chrome_driver)