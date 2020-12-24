# -*- coding: utf-8 -*-
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def get():
    chrome_driver = 'C:/Users/wisemobile5/Desktop/chromedriver_win32/chromedriver.exe'
    # chrome_driver = webdriver.Chrome(ChromeDriverManager().install())
    return webdriver.Chrome(chrome_driver)