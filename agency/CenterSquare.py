import Util
import Colors
from park import ParkUtil, ParkType, Parks
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome('chromedriver')
driver.implicitly_wait(5)


def web_har_in(target, driver):
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]

    trim_car_num = Util.all_trim(ori_car_num)
    search_id = trim_car_num[-4:]

    print("parkId = " + str(park_id) + ", " + "searchId = " + search_id)
    print("차량번호 = " + ori_car_num)
    print(Colors.BLUE + ticket_name + Colors.ENDC)

    login_url = ParkUtil.get_park_url(park_id)
    driver.implicitly_wait(3)
    driver.get(login_url)

    driver.find_element_by_xpath('// *[ @ id = "t_userid-inputEl"]').clear()

    driver.find_element_by_xpath('// *[ @ id = "t_userid-inputEl"]').send_keys('ppark')

    driver.find_element_by_xpath('// *[ @ id = "t_pwd-inputEl"]').send_keys('1234')
    driver.find_element_by_xpath('//*[@id="btn_login-btnEl"]').send_keys(Keys.ENTER)

    driver.find_element_by_xpath('//*[@id="btn_ParkM-btnEl"]').send_keys(Keys.ENTER)
    time.sleep(3)

    frame = driver.find_element_by_xpath('//*[@id="Input_ParkMAdmin_IFrame"]')
    driver.switch_to.frame(frame)

    driver.find_element_by_xpath('//*[@id="f_carno-inputEl"]').send_keys(search_id)
    driver.find_element_by_xpath('//*[@id="btn_search-btnEl"]').send_keys(Keys.ENTER)

    try:
        dd1 = driver.find_element_by_xpath('//*[@id="gridview-1012"]/table/tbody/tr[2]/td[2]/div').text
    except:
        driver.switch_to.default_content()
        driver.find_element_by_xpath('// *[ @ id = "btn_logout-btnEl"]').click()
        time.sleep(1)
        driver.find_element_by_xpath('// *[ @ id = "button-1006-btnEl"]').click()
        time.sleep(1)

        print(Colors.BLUE + "검색값 없음"+ Colors.ENDC)
        return False

    print(Colors.BLUE + dd1 + Colors.ENDC)

    if ori_car_num == dd1 :
        print(Colors.GREEN + "차량번호 같음" + Colors.ENDC)
        driver.find_element_by_xpath('//*[@id="gridview-1012"]/table/tbody/tr[2]/td[2]/div').click()
    else:
        print(Colors.GREEN + "차량번호 다름" + Colors.ENDC)
        dd2 = driver.find_element_by_xpath('//*[@id="gridview-1012"]/table/tbody/tr[3]/td[2]/div').text
        if ori_car_num == dd2:
            driver.find_element_by_xpath('//*[@id="gridview-1012"]/table/tbody/tr[3]/td[2]/div').click()
        else:
            print(Colors.GREEN + "두번째 차량번호 다름" + Colors.ENDC)
            dd3 = driver.find_element_by_xpath('//*[@id="gridview-1012"]/table/tbody/tr[4]/td[2]/div').text
            if ori_car_num == dd3:
                driver.find_element_by_xpath('//*[@id="gridview-1012"]/table/tbody/tr[4]/td[2]/div').click()
            else:
                driver.switch_to.default_content()
                driver.find_element_by_xpath('// *[ @ id = "btn_logout-btnEl"]').click()
                time.sleep(1)
                driver.find_element_by_xpath('// *[ @ id = "button-1006-btnEl"]').click()
                time.sleep(1)

                print(Colors.GREEN + "세번째 차량번호 다름" + Colors.ENDC)
                print(Colors.GREEN + "실패" + Colors.ENDC)
                return False

    driver.find_element_by_xpath('//*[@id="c_tiket-inputEl"]').click()

    if ticket_name == '3시간권':
        try:
            driver.find_element_by_xpath('//*[@id="boundlist-1021-listEl"]/ul/li[1]').click()
            print("3시간권 : 1021처리")
        except:
            driver.find_element_by_xpath('//*[@id="boundlist-1019-listEl"]/ul/li[1]').click()
            print("3시간권 : 1019처리")

    elif ticket_name == '12시간권':
        try:
            driver.find_element_by_xpath('//*[@id="boundlist-1021-listEl"]/ul/li[2]').click()
            print("12시간권 : 1021처리")
        except:
            driver.find_element_by_xpath('//*[@id="boundlist-1019-listEl"]/ul/li[2]').click()
            print("12시간권 : 1019처리")

    elif ticket_name == '심야권':
        try:
            driver.find_element_by_xpath('//*[@id="boundlist-1021-listEl"]/ul/li[3]').click()
            print("심야권 : 1021처리")
        except:
            driver.find_element_by_xpath('//*[@id="boundlist-1019-listEl"]/ul/li[3]').click()
            print("심야권 : 1019처리")

    elif ticket_name == '24시간권':
        try:
            driver.find_element_by_xpath('//*[@id="boundlist-1021-listEl"]/ul/li[4]').click()
            print("24시간권 : 1021처리")
        except:
            driver.find_element_by_xpath('//*[@id="boundlist-1019-listEl"]/ul/li[4]').click()
            print("24시간권 : 1019처리")


    if ticket_name == '48시간권':

        repeat_count = 2

    elif ticket_name == '72시간권':

        repeat_count = 3

    else:

        repeat_count = 0

    if repeat_count > 0:

        try:

            for i in range(repeat_count):
                print(f"24시간권 {i + 1}번째 적용 중...")

                WebDriverWait(driver, 5).until(

                    EC.element_to_be_clickable((By.XPATH, '//*[@id="boundlist-1019-listEl"]/ul/li[4]'))

                ).click()

                print(f"24시간권 {i + 1}번째 적용 완료!")

                driver.find_element(By.ID, "btn_save-btnEl").click()

                WebDriverWait(driver, 5).until(

                    EC.presence_of_element_located((By.ID, "c_tiket-inputEl"))

                )

                driver.find_element(By.ID, "c_tiket-inputEl").click()

                time.sleep(1)

            print(f"✅ {ticket_name}: 24시간권 {repeat_count}번 적용 완료!")

            return True


        except Exception as e:

            print(f"⚠️ {ticket_name} 처리 중 오류 발생: {e}")

            return False

    driver.find_element_by_xpath('// *[ @ id = "btn_save-btnEl"]').click()
    time.sleep(1)
    driver.switch_to.default_content()
    driver.find_element_by_xpath('// *[ @ id = "btn_logout-btnEl"]').click()
    time.sleep(1)
    driver.find_element_by_xpath('// *[ @ id = "button-1006-btnEl"]').click()
    time.sleep(1)



    return True
