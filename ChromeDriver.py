# -*- coding: utf-8 -*-
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager


def get():

    # 크롬드라이버 경로
    # 에러 뜬다면 해당 컴퓨터 크롬버전과 안맞음(현재 89.~)
    # 크롬설정가서 업데이트 눌러서 버전확인
    chrome_driver = './chromedriver.exe'
    # chrome_driver = webdriver.Chrome(ChromeDriverManager().install())
    return webdriver.Chrome(chrome_driver)