# -*- coding: utf-8 -*-
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager


def get():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument("--disable-extensions")
    # options.add_argument("disable-infobars")
    # options.add_argument("window-size=1920x1080")
    options.add_argument("no-sandbox")
    options.add_argument("disable-gpu")
    options.add_argument("--lang=ko_KR")
    options.add_argument('--proxy-server=socks5://127.0.0.1:9150')
    options.add_argument( 'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')

    chrome_driver = 'C:/Users/park/chromedriver/chromedriver.exe'
    # chrome_driver = webdriver.Chrome(ChromeDriverManager().install())
    return webdriver.Chrome(chrome_driver, chrome_options=options)