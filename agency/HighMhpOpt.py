# -*- coding: utf-8 -*-
from selenium.webdriver import ActionChains
from selenium.webdriver.common import alert
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import Util
import Colors
from park import ParkUtil, ParkType
import WebInfo
import pymysql


# DB 연결 정보
DB_CONFIG = {
    'host': '49.236.134.172',
    'port': 3306,
    'user': 'root',
    'password': '#orange8398@@',
    'db': 'parkingpark',
    'charset': 'utf8'
}

# 동일한 정보로 통합된 mapIdToWebInfo
DEFAULT_WEB_INFO = ["username", "password", "/html/body/mhp-console/div/div[2]/div/div/main/div/form/button",
                    "discountPlateNumberForm", "/html/body/mhp-console/div/div[2]/div/div/main/div[2]/div[1]/div[1]/form/button/div"]


def get_park_ids_by_urls(target_urls):
    """
    DB에서 특정 URL 리스트와 매칭된 park_id를 가져옵니다.
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        curs = conn.cursor()
        # SQL 쿼리 실행
        format_strings = ','.join(['%s'] * len(target_urls))
        sql = f"SELECT parkId FROM T_PARKING_WEB WHERE url IN ({format_strings})"
        curs.execute(sql, target_urls)
        rows = curs.fetchall()
        return [row[0] for row in rows]  # park_id 리스트로 반환
    except Exception as e:
        print(f"DB 쿼리 실패: {e}")
        return []
    finally:
        if conn:
            conn.close()

# 대상 URL 리스트
TARGET_URLS = [
    "https://console.humax-parcs.com/login",
    "https://console.humax-parcs.com/",
    "https://console.humax-parcs.com"
]

# DB에서 park_id 동적 조회
dynamic_park_ids = get_park_ids_by_urls(TARGET_URLS)


# mapIdToWebInfo 동적 생성
mapIdToWebInfo = {
    park_id: DEFAULT_WEB_INFO
    for park_id in dynamic_park_ids
}

# 확인용 출력
#print(f"Dynamic park IDs: {dynamic_park_ids}")

# 공통으로 사용할 xpath들
#btn_login_xpath = "//*[@id='app']/div/div[2]/div/div/main/div/form/button"
btn_login_xpath = "/html/body/mhp-console/div/div[2]/div/div/main/div/form/button"
btn_search_xpath = "/html/body/mhp-console/div/div[2]/div/div/main/div[2]/div[1]/div[1]/form/button/div"
side_nav_xpath = "//*[@id='side-nav']/div/div/div[3]/div[3]/div/a"
#side_nav_xpath = "//*[contains(@id, 'side-nav')]/div/div/div[3]/div[3]/div/a"
btn_confirm_xpath = "/html/body/mhp-console/div/div[2]/div/div/main/div[2]/div[1]/div[2]/div/div/div/div[2]/div[1]/div/div/div[2]/button[2]"

def click_har_in_script(ticket_name, driver):
    ticket_xpaths = {
        "평일 당일권": "//*[@id='tbData_dckey']/tbody/tr[1]/td/button",
        "심야권": "/html/body/table[2]/tbody/tr[5]/td[1]/p[2]/input"
    }

    if ticket_name in ticket_xpaths:
        driver.find_element_by_xpath(ticket_xpaths[ticket_name]).click()
        return True
    else:
        print("유효하지 않는 주차권 입니다.")
        return False


def click_radio_button(driver, radio_xpath):
    """
    라디오 버튼을 클릭하는 공통 함수.
    """
    try:
        driver.find_element_by_xpath(radio_xpath).click()
        driver.implicitly_wait(5)
    except Exception as ex:
        print(f"라디오 버튼 클릭 실패: {ex}")
        return False
    return True

def click_and_logout(driver):
    """
    버튼 클릭 후 로그아웃을 수행하는 공통 함수.
    """
    try:
        driver.find_element_by_xpath("/html/body/mhp-console/div/div[2]/div/div/main/div[2]/div[1]/div[2]/div/div/div/div[2]/div[1]/div/div/div[2]/button[2]").click()
        driver.implicitly_wait(5)
        print(Colors.BLUE + "개발테스트4" + Colors.ENDC)
        driver.find_element_by_xpath(side_nav_xpath).click()
        return True
    except Exception as ex:
        print(f"버튼 클릭 또는 로그아웃 실패: {ex}")
        driver.implicitly_wait(3)
        driver.find_element_by_xpath(side_nav_xpath).click()
        return False

def select_discount_and_confirm(driver, radio_xpath, confirm_button_xpath):
    """
    주차권 선택 및 확인 버튼 클릭, 로그아웃까지 처리하는 함수.
    """
    try:
        driver.find_element_by_xpath(radio_xpath).click()
        driver.implicitly_wait(5)
        driver.find_element_by_xpath(confirm_button_xpath).click()
        driver.implicitly_wait(5)

        print(Colors.BLUE + "개발테스트4" + Colors.ENDC)
        driver.find_element_by_xpath(side_nav_xpath).click()

        return True
    except Exception as ex:
        print(f"Error during selection: {ex}")
        driver.implicitly_wait(3)
        driver.find_element_by_xpath(side_nav_xpath).click()
        return False



def handle_invalid_ticket(driver):
    """
    유효하지 않은 ticket_name을 처리하는 공통 함수.
    """
    try:
        driver.implicitly_wait(3)
        driver.find_element_by_xpath(side_nav_xpath).click()
        print(Colors.BLUE + "유효하지않은 ticket_name입니다. " + Colors.ENDC)
    except Exception as ex:
        print(f"Error during process: {ex}")
    return False


def check_discount_open_button(driver):
    """
    '할인 열기' 버튼이 존재하는지 확인하고 존재하면 로그아웃 후 False 반환
    """
    try:
        driver.implicitly_wait(3)
        discount_open_buttons = driver.find_elements(By.XPATH, "//span[@data-i18n-key='할인 열기']")
        if len(discount_open_buttons) > 0:
            print(Colors.RED + "'할인 열기' 버튼이 존재합니다. 다중 차량으로 처리 불가." + Colors.ENDC)
            # 🚨 '할인 열기' 존재하면 로그아웃 시도 후 False
            try:
                driver.find_element(By.XPATH, side_nav_xpath).click()
                print(Colors.BLUE + "다중 차량 감지로 인한 로그아웃 완료." + Colors.ENDC)
            except Exception as ex:
                print(f"로그아웃 중 예외 발생: {ex}")
            return False  # 실패 처리
        return True  # 없으면 계속 진행
    except Exception as e:
        print(f"할인 열기 버튼 확인 중 오류: {e}")
        return False



# 기존 코드에서 중복된 부분을 이 함수로 대체
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

    # ParkUtil.is_park_in 확인
    is_park_in = ParkUtil.is_park_in(park_id)
    print(f"ParkUtil.is_park_in(park_id) = {is_park_in}")  # 확인을 위한 출력

    if is_park_in:
        # mapIdToWebInfo에 park_id가 있는지 확인
        if park_id in mapIdToWebInfo:
            print(f"park_id {park_id} is in mapIdToWebInfo")  # 확인을 위한 출력
            login_url = ParkUtil.get_park_url(park_id)
            driver.implicitly_wait(3)
            driver.get(login_url)

            web_info = mapIdToWebInfo[park_id]
            web_har_in_info = ParkUtil.get_park_lot_option(park_id)

            if ParkUtil.first_access(park_id, driver.current_url):

                driver.find_element_by_id("username").send_keys(web_har_in_info[WebInfo.webHarInId])
                driver.find_element_by_id("password").send_keys(web_har_in_info[WebInfo.webHarInPw])

                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()

                driver.implicitly_wait(3)

                driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
                Util.sleep(3)

                driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()

                Util.sleep(3)

                # '할인 열기' 버튼 있는지 확인
                if not check_discount_open_button(driver):
                    return False  # 실패 처리 후 다음 작업으로 넘어갈 수 있도록 False 반환


                if park_id == 19598:
                    if ticket_name == "평일 시간권(12시간)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_30236773c2ae46efb4e4699da822810d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 시간권(12시간)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d3f6972a85ef4017a98216c51562c93e']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3085ac10d8e64b72917103b47d08b5e7']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19834:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d5b38ccaac154bbe88d36da38c5d46e6']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fe7e280c050549bf8b01b33df2cc777a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 5시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fe7e280c050549bf8b01b33df2cc777a']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19056:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_70b125d06c80438ea71eb0e16ac97453']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 심야 7시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5c62ff0333f64ed0ac8147a928c35bfb']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 심야 7시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5c62ff0333f64ed0ac8147a928c35bfb']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_772aa62d7233445cb11a4307aecc077c']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_772aa62d7233445cb11a4307aecc077c']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19414:
                    if ticket_name == "평일 11시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2a4dc029f46c4f6db129d0414e8f239e']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c987154216e04efeb3fb9489ee26eec0']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_05b8a7fddc7a4cd8bbc182de742a0d4d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["휴일 당일권(일)", "휴일 당일권(토)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7ae6d01495844d348abb36445126085c']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_61ecaa9116a24920a35ad410ab823ee6']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19195:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_44399cdcbf0f4441aab566bae1d011aa']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_44399cdcbf0f4441aab566bae1d011aa']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6652d51c020a4563b76bcaa5ce01b01c']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 12054:
                    if ticket_name == "평일 오후6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5489f4553a4f4c69abd078ea1f2e72da']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_35dafb9435d94216973fc24d626e821a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "주말 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e23451e340164b2ba0982c525b04ba23']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19211:
                    if ticket_name == "3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_69e8be12391f4a9988016a1fa8971d76']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "10시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_35dafb9435d94216973fc24d626e821a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_35dafb9435d94216973fc24d626e821a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "야간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_35dafb9435d94216973fc24d626e821a']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19073:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c517f093f7904b98b9bd49bc43fce7ee']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8f79af7737f14382ae057062fabc041c']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ae1605ad57094ca8b6173edf786bf9fb']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19410:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cd47c75107254ed29bd5d1d9f16484bc']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fec924e21fb641f0bc20dc4281431eaa']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "토일연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_481c82744dba489aabd0d31e269a91e9']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19592:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_775427bfd6b445f5a3801db71fd39738']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일오전 8시간권", "평일오후 8시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f3e72d2f86554340bb94ad64e78af95d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_078b1d25225e42b4b12a4188423e1418']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19452:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5f1421c404084c46a9b637e1d9677cee']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_02d2716131394ef99ef3b49d34286b32']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_aba2400bcf8d42859eb8ffed62fd910c']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 야간권", "휴일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_94c7ebf310ec4e3db849580b5d58210b']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19429:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_042528b5d3ab49649ee9b5b778066f04']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f87161751ab64b42ad1387d95d5245ab']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9cabdfa1061c400aa088cf7fd190da0c']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1e0fac6fed864c049ee4d7a1c0590bd6']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19875:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ec711ce63a60456599c80dfb8f7af841']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f4db56c5d2734f5eaf555c131bed28cb']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19419:
                    if ticket_name == "평일 오후 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6bf0111e4b5f49188e0d9639e0759f09']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 11시간권(월~수)", "평일 11시간권(목~금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d274867d89f8434a813af8b8ef119312']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9244eedee2274e17a71ba53d15201e51']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8e28c051bfa3465db2833fafc777a20e']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19212:
                    if ticket_name == "평일12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_03d19ee79c624f299b97f7f3f81bb73f']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dcd5369ee2904969abbbd56d03bb2801']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7dbcf403357d43808c73c27f77790c9d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3be01e8c96ee4eb3b834cdc50b0f438d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "야간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_08b3dedba16b4c09a418f28cb5e77161']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 18980:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_97b159cf96ce4f5cb3542102267fe03b']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_47c727230a264c5d8aff232b64541b87']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19736:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_74fb60bc858a4f11bb7ef1037dd7f99e']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e83acc5934e145db8fb5fc5f985c7ce2']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_20818da333e840aa82c87c5cce864540']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19884:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_300ea3bbf5a34f958f0775540914bbc8']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_87112a42195f4b2bb74d361c9df526e5']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e1b16345f40241838a4c3d9030e31a8f']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_67e8b342613e4b0eb9cd1853dd92a661']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19431:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ae05ad12967e45f3a69f4a580911f302']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a9b2cdf840084ca196ba248c569f4b22']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4fb88bc8c4ea4361bb97c82f4b136395']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 야간권", "휴일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bdfc71f814d44f1e993a0d4f82e8ccbf']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19848:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_de30dac95e0c4674b03ca3b00b862efe']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 주간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_795857aa964f44abb5d9260d3beff310']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19623:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4f99601465fe4e73b7c3d191314bb99f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 3시간권", "휴일 3시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b252935970d94a3681b7087a37e58125']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 저녁권", "휴일 저녁권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a415541c9e194719ac52b936daae08f9']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_487ab36674624eec932f928fc6ab66dc']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19218:
                    if ticket_name == "평일12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9188b122a3c84f6aa03b12d3196d03e2']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b1cf03cb2ff441e492a9ab47d871f139']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_444a4d65186e49bfb20eabea3bdb6b62']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c3f7534bec864520840dcc2a281f647c']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19140:
                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_56ebbfff25f0468b9c6e4173993c4371']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_304b0e27e797440aa566c76c5a3d1e84']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_56ebbfff25f0468b9c6e4173993c4371']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_23e7f199652040b484a54e50c01bcecf']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 18981:
                    if ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fc923f6259cf4c2e9ba885bcf71e8cc9']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cbd0bc1080544b8fb2288269e8c55106']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0c6a13b59e444d53b7d6b9727277fc81']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29123:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c4fdaec4a55b4f52a1a18df6a8d967ac']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2일권(월~목)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a77aaaf5c693456ba99448671dc29f3a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3일권(월~수)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1435e4c2a01841e2b43239946c625c66']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 16175:
                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dff6c473af654c879e5f66684c95a8dc']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9743cbe2680b4b2781df83d1e249b5c1']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4c306f9033784f7093beb145b74eeee0']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2d02a9a6397844b5b6fa913f5b74d8e7']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ef6df63fba3340ffb7b7bc7caac03322']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19737:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1d1ddfdb18bf45d29056b4847b2443a2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_326de4917c6a4be1abd9578a361092d0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "주말 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_414b912547e04037a6fc3aa1a743198f']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19953:
                    if ticket_name in ["평일 12시간권(수,목,금)", "휴일12시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f8dae01ae4734d9da9b6f30e5037c51f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["심야권(일~목)", "심야권(금,토)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b9cfba1087584364ac319b562102d058']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19083:
                    if ticket_name == "평일 오후 8시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4b86655c05624c5cbaec7db6398f3888']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7f4ff534c47945459bf4f6808dd07321']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "야간8시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e630107729a748be89d0909fbd7e7d17']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_52c14814da124f42a328b6c3f112a5d1']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19171:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c6b465dbbb9d431bb8659025e52851d2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_13a6a9669a624231868dd571b4a3f6cb']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 16360:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_17ae285ede5a48b3b08d7d978c697100']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e0596e82e573446f8f5724ae098b4ef4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fae0e5a7cfdf494da4f1c7c4395f9f00']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19501:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7c9d536987bf4f59893e82890016ffc2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bd0bf1eba1d84b9592041168c8d3dd1c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c7362fd046344e28a7dc92712f3b56ef']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19854:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a4a8203e4d0849f2b04eab78db8f296a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e05a697b2619479da72df22ec2adf29b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0519b3a27eaf4bd89d3e487bd50433a1']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19084:
                    if ticket_name in ["평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d6d051e84b6b46c7a15f3c6585ffa5d3']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e33c0600b8bb4a24912c20550f062386']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c3c5fe62b1ac46fb94e2d8e125e207a0']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19087:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1ae2a8de4ee3443fa642029664129fe2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_151fd6c18db041c38f2eacc6d42721a5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 야간권", "휴일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9e68b9dbf76c4663a6343ec53f7757ff']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19942:
                    if ticket_name in ["휴일 야간권", "평일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_11de326766544ac7972e0f01a4b817df']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c2eafba65ea64b3daea0239b7f7e3587']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1c57da2209e74374bdaa889725455ecb']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_826d2141c4b7438790cc56733b336f86']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 18972:
                    if (ticket_name == "평일 당일권"):
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0c927f60ff154f27bbf1f7d9bf7a602d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_21ca569fd53a461f820d3a044d46b0d0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bd16b9f935e946fbbc28f39a1d78a973']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19859:
                    if ticket_name in ["평일 3시간권", "휴일 3시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_40219ced8f4945b5b6286a30a7c414fb']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1d65c0d4705245329b97115dd6b0f775']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_570784be302946b1950029e052dbff2d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a6056ea454634ab796b28960b6e18c28']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7421d48e1414476a8f878cb79c0d188c']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19180:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7dfb8b113abe4a7497d8507356508631']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_32f8676da7f34a5f8898b42484d15543']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e4f4e9b0991048c7b1a23bbf2fabc298']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_268f7e25a1c14c4aa0fcb2837f78a7db']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19464:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_75705c0ae7c14149abb48f2b1607ea61']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["토요일권", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_57b038fb162846aa86988fc9568fbc7e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e3608e0187994e8581e3dd1939ea5457']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19226:
                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_712062b2c79f474aa27fe74aa9b2690d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a7de5a984c6e41dbb9de93f6123fa296']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "주말 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_230e041d29bf45bba2caa75770053b72']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "야간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6fbfd81f9bec4ecfb0fe621d478c261c']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 18959:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_98cfa3a5c9ab49c5b2c714c5d3aa8c71']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권(토,일)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1d22c084b03d4343b00d5c793437e1b4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cc0335ea37a34b779e11adf6fbe71658']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bf574ee6f42a45eda06ad8d23a91459e']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19139:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_93575b4b9ff64f578e458b2d863c8bae']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["휴일 당일권(토요일)", "휴일 당일권(일요일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_33d317846d4743739113dc26f5a7cf07']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_861a019e5ecb499b8bf1983418f3a9cb']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 심야권", "평일심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f1458d5278034233981aca9ad4f2ada3']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19626:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_66c9e8671be54beea0195a0071b60f26']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_308a38dd7c3042bca0fe64c0663327a6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_62286f8669b54b8abe6ebfda9040ef14']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 16215:
                    if ticket_name in ["평일 3시간권(월)", "평일 3시간권(화~금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0810b21575294255af7c86cfabe74b51']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a03b0f1d646544aba442bda631eb9004']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_28b2aecadb7346dea9ed154cdb806d3f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 심야권", "평일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ddfab422991a4eceb5ee0a7a9b9bdd57']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 13044:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4bd97cbea0264eae8cca7b4c843cc2a5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4b69579740fa4490b7f99cee578eb86b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1f624a6341bd4aba83359d523486f2fc']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ea27e9b70b8244d8b0b24999976f9b33']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29191:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d540a0db34614cc8a68513db3ef4960c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c4c5c0e9390e4c39abb7f335045345d8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8f696850de5b4cd582027d5b23da62c5']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 16173:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_93b3333cb07540059adc362aa36771e0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 시간권(6시간)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8f408e9eec15413286fb9f21ce484e73']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_49deae21329e4376997e0a5bc0fa736d']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 16184:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_05ee060b94104543a0355f149bed5850']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 12시간권(월~수)", "평일 12시간권(목,금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_00bdf2d4491a4398b77cc6575e8528ea']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9f03cd56dc7b473a80b6b71409b402bb']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 29205:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fa721b08ff4948b7a50abb751ffbd580']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 야간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8c5cc933733642199c59e0dd9b5a6ef4']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3c01c454ed874e229f2c202422735325']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d2aa54e76b174a40a0ec29118966cca5']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 18967:
                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6c021defbc784d339f1dd0444fcd98f6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_389101a9cd5d48e59e712ecb22aca802']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 14588:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9aa9389d11994265bf51b0422a54b575']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19374:
                    if ticket_name in ["평일 당일권(수~금,기계식)", "평일 당일권(월~화,기계식)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_aa2165f2002f4708ac419f76917f4ffc']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오전 8시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6bc40b123e014bf8abc1cf7b4fb8d88c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후 8시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_efa56330bd2b4f22ab14e18a8a5a9bca']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19138:
                    if ticket_name == "평일 96시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0decd9664d384b0d972f9cde09a3a877']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_14feb6038695484e992ad49f58034bb8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 48시간권", "휴일 48시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_37676733df544a6788b0ced8a5d39758']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6f47d315b3714543b7c8007f8d13182a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 72시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cac69a17d6484b5f90c2fa4fb7e5754f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 24시간권", "휴일24시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f283fcb30ece4f2fa1ad02952e445825']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 12시간권", "휴일 12시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f552cb04c0e046978f3edcc039de6fc2']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 29099:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dcb9cc0ecfd54e4ca6d63a00e3661cf7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5aca69e4bb574dbcb20afe2b34b9bfb3']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19516:
                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8a8fb3594d5241888b6d340d40e649a4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e1e8b281afe44a97a41f5399d334535a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5706f17c1cf54fa293db3bbc7e8361bf']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 10시간권", "휴일 10시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d5f17e9c51744ff6ad4a84724c7166ec']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19519:
                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_59fc112deb774232a5f9794979387a8d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_94d415f534874270a74d3526b2803970']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 심야권", "평일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7ba4dfce4fb0490a91447c3b45993f47']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_609b9ed03f2b421e9614104fdd3d3bef']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 14994:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_75a98fa171b64982ae8cad69b4c4a766']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_16d6ac5de20a4596b790d63506f7a778']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_191f5cf9a8bc4dc2abf95a960b98f0d4']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29106:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7990ebda29534c6a90548adf1860cf94']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5c66bbcce07f4278ae28f220a62cd4ab']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ed38fef8afab4cb083aa88cbbc5256f7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fd3ba90599a8424a8af4d5655e726238']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d16e8916f790492aa465f185f926113a']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29130:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dccef85ee6ac4d90bdcb417162f2351c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_37e3cb7c4bc24e3482bfecc54ae9797f']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29125:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ded68d275aea422da051cffb08085905']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a5726267286346e4a0f2c866bfe53fd1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2a49cb1f1c0d4c5fbf7e75342846a55d']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19472:
                    if ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4ceec33065194126aca21a41ebc3879e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_71a84872021f44109e2ec12465b90bc0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 11시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6086fab63f914a35978900a8285dbcd1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_933d3a0220a94755839d2303fdff2a20']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19002:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7535bdb0b7fe4ffc85b522ecd0a14f76']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8636d6ee052a48699494f020c0d0283d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8b5fe493117544489c53b68007524f47']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19929:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_12f83b69d8c94c049168bcc1a078e119']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 3시간권", "휴일 3시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8636d6ee052a48699494f020c0d0283d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                       return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_37197fea616545ea8649df1452bcd5ce']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19929:
                    if ticket_name == "평일 당일권(지하 7층전용)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_44249a1f1a1149618a265569497dee53']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_da9a1b4fe7c042a9b2dd04f2e16c79f4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "주말심야권(지하 7층전용)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6b0f22345c624234a22d161530d67cf8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 12시간권(지하 7층전용)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_340fd85f03d74212b8d2379196058164']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권(지하 7층전용)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_24d6863d70644e9a926bcb5ed41c0e94']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29178:
                    if ticket_name == "평일당일권(자주식)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_32ed4002ba834ca493d3c2d16aec5141']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권(기계식)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5fd9c677cad74b38934cab6320819ee9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권(자주식)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7be9adb070574e1b8041e5b03e959674']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19631:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fa86ec6632fa4ab68647d1552132cd47']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_95d168afe479498cbdcc058e9160ca23']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "주말 1일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dcda4f2fd9df4b82b452e705d32b339a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7ca17cd222d94459a3d9adc7f1a38e5c']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19896:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9c26a426d9864fec8b520b9ac80faf4f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 야간권", "휴일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_880656fce3af442c90a945576827d60f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0e7d3a8c6bf741578fc69f1b42f84b8b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_18de221b6cca4df2af451661d65bfa9d']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29144:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c42ecec063434e199f9e72d4df3015a9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cb84770012be4066847fbb73c78a535b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_927ee9bf842c47a7ad716e3e5cebb256']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19863:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a67c0bc0793b4207bd3a8824e28d22f7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1ad47feea82d4009bca5693794edb2e7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f869cc50a05c458bba2937f1b0f43629']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2bd5642250e94218956fcec3c1e939a9']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 18995:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0ad12ffa4b3a441db71f17cc5104a0fd']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_785a9d90d98e4219963b4593427b37cc']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "2일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f18bf1f56bf441e088928789b4b9d13e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "3일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_57fa937b6b654cd697bcff1428834b9e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "4일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1a3f037752a543acbde4977736fccf44']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "5일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_399ed2221f3b4055a8c13747f98768cd']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "6일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_479c300df9464d4c90b7dead1abc5a06']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "7일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_83297f952dbf48ca95d3a31903b64677']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "8일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b2b651b11a534aa0b47bb142677eff12']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "9일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_da82064dfb85481a98df17a6e6963017']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "10일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_200fc715e0554d328b1d86ed1c5aed8c']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19952:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_58bc8859e93a48aaa26193dcaf2a9c80']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d98d694e8f0b4994b4407134c764c35e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c4eee6e6a2a04bcfa344e2074d3dc64c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["심야권", "평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_10aaa0b5c3fc4fd185817168ecd9df32']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "2일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7ecec1f2337941eebb46ccb45cdc1de1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "3일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8c5a1322abb745fe936fbce22771fdb4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "4일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cf9dbf53c46940e8b158eae0683e6373']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "5일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_342bb3b61ae443f98c4695460fba2181']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b68c315032c3494baf9e460f66f6d55b']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19914:
                    if ticket_name == "평일당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fc854da4b1814b2c97a8c9cc61feddf4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_855739e48f784a18bcf36571b49b7e26']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_11648f9580a94ee19708742fa16bb4fe']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 18969:
                    if ticket_name == "평일 10시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_617303ce0f314f3298df3fc73e0d2034']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8843010759fe40729789b73fc22061d8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_88d9d06b6d3842aba218dcabbd291039']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 22982:
                    if ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d6cbe1861ab146628a6a74b221b03918']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 15437:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_67776a96054f4011a1e8b49f1b3b3f7d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f9338e12ef7b43f9a29e43d94a43a18a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ae06abef0e2b48f9a9c46267f1f1ee56']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19466:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3c8837ff5b01456293fca3571a787ff0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_92dc258f1368409a848c9c7a6e436cf4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0475ad489f92457a89167cbdf46712ec']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19202:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0ba6fb9c72964d83817212ae23fd73c6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_784465e02a514a6792e97ab3db6780f5']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19241:
                    if ticket_name in ["평일 당일권(월)","평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bd3487c993b4422e92eb04d44765ce77']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0639fa425d0a4ad68273b4393c1c9f55']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a63d268fa3ca47438d0eb5340833ff2f']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19143:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7a8e137287674f0f8a8b5de984711843']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f684761f115248dbbc1c674e9486a659']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_810e70b951ba4135ac618c410b356876']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_999151e2f6e14965a13497b66c112565']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 오후6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3ab61625a41f48e0ba1521d0a6b20844']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19122:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화~금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b873f61f02584135a40d281ce43f61a7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4a3837288294475aa9216994a8424131']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b254993957854cbcbea011b9b88522d2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d8cdb93cf7b848dda8dbbaa0f3d1fe69']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1f070e52a0cb4b988fc039e793a87a3e']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 12766:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_982b5eea171942a98fee24d34d2b002e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 10시간권(월~목)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_159759b57b4642b58880e3fcea9127b4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_82de6fdedb514a09807c88434e4e1786']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9f24a9187c7e491d8813308abba8ee99']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 오후 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_abbfa927ef174dada145b9928da3a8e9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d68111d35385475fa0c9c23f4a1695f8']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)




                elif park_id == 19159:

                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e785342f8f8c41e0803ad956c02afde9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_751fb62b69b3421ca6ef1481a67e9bd6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권(월~금)", "휴일 심야권(토~일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ebf251aaae8a453b9579d6d1b5ae3beb']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_83241f5178274b37846760913c18656b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 5시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_99908b21a36c4b1b8ce765e8639e3c6c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_43e3f5f9811c43958e51b35f3daa23ba']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19847:
                    if ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_da72fe394ec5410f81188a5a4dc717e8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6c761947e7244c778dcc0b155e6d6eb7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_803fe179044b4cb78d068365fe867d8b']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19845:
                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_74b69bc572d949a48fee277f1d5c1e7f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 야간권", "휴일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_531fefba2b7845a283e00c1d9addd994']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["주말 당일권(토)", "주말 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c8b0a6e6318b494093c322906c2b9358']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "토일연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f70ce4d242774779b612b2f7ee999622']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19614:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3ba2ee7fad8f401b8759bf4ab983424a']",
                            btn_confirm_xpath
                        )


                    elif ticket_name in ["평일 12시간권(월,화)", "평일 12시간권(수~금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_78cd981b00f149caa968aa397ed3da87']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c81c5bc23f914b90add723692af20072']",
                            btn_confirm_xpath
                        )


                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 29188:
                    if ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_14acd1149f5348da85d928e890034d49']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dac20820e2e64f9db991ebd6b090bc47']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ee03a4e75e5040118b5f7df3306f1f94']",
                            btn_confirm_xpath
                        )


                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19161:
                    if ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_14acd1149f5348da85d928e890034d49']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dac20820e2e64f9db991ebd6b090bc47']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ee03a4e75e5040118b5f7df3306f1f94']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ee03a4e75e5040118b5f7df3306f1f94']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19925:
                    if ticket_name == "평일3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_90b077e907794c6fa4de67f0f23662a0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일5시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3e76ca9d4bc04da191fc50966cbbef61']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_68669f476a744137b45f47658bf4abaf']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 저녁권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f02145f1765d418d9bd8fa993c5a2fcc']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_87b1aecc28f643759a4f225c93b462ea']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ec5c80560578496d878daaab76bdce0e']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 오후 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1a23ebe833d14502ae98c18b2529ebdc']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19881:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b63949b0f0a24f89a2c3bf54697dcfb1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 심야권", "평일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b6bc44edee904d0f8c41cf1c1e5e47e8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d11a6e98b91e41fab7bafb100bbe2e6a']",
                            btn_confirm_xpath
                        )


                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19924:

                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cf0b41b8386346eeb13c9b47a0aad20c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_37e6dc4bd45b47058c355f4b19b2ecaf']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19627:

                    if ticket_name == "평일 주간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cb24128c87ef422eb99383e2090d52cf']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 12997:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0f37a084c6f84269875140ad891345e4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bfdabc3d07bb473790bd5a2f850c6dcd']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 저녁권", "주말 저녁권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_abbdf6cb24dd44d7b9bccdb103df6f3b']",
                            btn_confirm_xpath
                        )


                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 29134:
                    if ticket_name in ["심야권(일~목)", "심야권(금,토)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_eb99712ae3f44aa8bedcf913503beb1d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_992c024ddf004b0688668d13c9e41fda']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_01e00d926e674c9c8a771665be09bae2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f0b0e9ac919f4cc385fbfc25199ef56a']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29137:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_882642f3956545fe91e74eee811b6eb5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후 5시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_eb61d16906f340fdb50fc9a19c2adff3']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6099d9cabe004ef4be809267235e7b9e']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29198:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3a4f16645edb4c2e8e245246e8f65238']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_000a76ff21ce404ab819db01bff4a859']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ef8554d849884006aceda5e207a2e043']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b611a080dd0d499fa7c98447621caf14']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29176:
                    if ticket_name == "평일 당일권(지하4층전용)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d4c93184281e4816ae0cf26c66874eaf']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "주말 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0d8fc56ad17d47b7801cdb29a3f54940']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a584211ac8cc4da79d0aed26081fc1e9']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 11917:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f4a6341cf9824fc1b35a25457f071464']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d4c7f97a3d5742d9a92915a0116539fe']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 11917:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a4b8a6426bb24b72a179ddad68751dfb']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_12ac36cb6a4a4109a48aa6b08fd29f40']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_104d9d57a69a4698be3086f4d6d75a47']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_668454da082e496a8db4a9f5c7164be3']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 29226:
                    if ticket_name == "평일3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_38d6f37c1981484d9c9a793d306ba7c8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_802c71c947b447338c73981f99ea3a8f']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e4b74f288b944a5ebc99fad8e16faefc']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_66a75235248846538f2a48949563947b']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 오후 7시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f33e32cd3b644d78b86df7e14be37ad8']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19874:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a4b8a6426bb24b72a179ddad68751dfb']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_12ac36cb6a4a4109a48aa6b08fd29f40']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_668454da082e496a8db4a9f5c7164be3']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_104d9d57a69a4698be3086f4d6d75a47']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19491:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ef01393155a14a0c915b2326253ecb8b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ac79cfb8063a49389eeda29b0a815a1d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_babcc7e5e33348a191488fac6d3b03d3']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19217:
                    if ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_963b6430aac843eead157a057bf36278']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cc8faf15b23340a4b17ab77892ee0d46']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19601:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e97f864e960646ac9eaad63cd0836661']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 10시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e184c0dee1f4446e9247efb76b50c0e2']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e184c0dee1f4446e9247efb76b50c0e2']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 오후 5시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d049f482cf1f4c84ad5bced5e82f5afc']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f5c2529e5e10445eb22859358cea7b87']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29183:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_db7f14826c8f40499080f048fe81276f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_702e1755207f4342b4ef5f99e6d1868b']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 12532:
                    if ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a11036fe97694fc3a54835bd24079a8a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1f402fe92b6440c4a9589290a3fdbb5a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1546b59e15ed4f5e8188076e08961866']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c8c648d4ffc94ce6bbd675ed720eefd1']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19228:
                    if ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5e977aafb6f045a2a1790ba48e03979f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f3c97769e3724c0494722982466b7ce1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d8d5049ddcd544238ac4976975f2c26c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9f9f4632a5a14612b1737ca6ca388d45']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_577409ad1e044925b7e3a38f732fc5af']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29201:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bce1517ac6704cd1a004356dfa94855a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fd209e15b88a426cbdab90a3e2a1b7c1']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29204:
                    if ticket_name == "평일1일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7f7f09a886784d2c830c0bc02bbbcffe']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "주말1일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_91c271b28069404a8e2ac1edd89e56d1']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_03f0f34a97d8453188a1a489a2767085']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29186:
                    if ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_393e1eb5e2cc48d89bdbc08bff1b01f1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5bf23b8775974bb0beabca18753565b0']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 주간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9686e4275d2b49a1b093a9570b326695']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 주간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ccd28d48040a493c90e4fbb8606e9484']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19838:
                    if ticket_name == "평일 시간권(5시간)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_66ab9085d2194f24aaae2556623d638c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 시간권(10시간)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fad4bdf887b744d0a11c232ad9728825']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ea5fbd0bb35348e4b9a839a08a5fd0bd']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "야간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fb1b2ad80cb142a7aa77044c066020de']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 시간권(3시간)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4916131bc91440c3b698cf19d621da80']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 시간권(5시간)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9eb906b74f6b4be6b300d9607ce57de6']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_066bb070255145b8a220a4d55a0792bc']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 18957:
                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3c4472ba09c3481ea70bce3a0512b695']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cf7c640b3813470190a84a07393c82ab']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e888ee6f60a64854aa2c5dc6580034d9']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["휴일 야간권", "평일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f4c66f34e38c402ba8e7954f5030d65b']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19227:
                    if ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_baa5c6ff54924969b000055b17fd7dca']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_81eb1987750544ca909f6a2e4a352a18']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2e40954790ec4ae6860c5090647c1d8c']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 14776:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_da3a90d90f8c4883a3efe1fa41f940da']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 오후 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6cef8a600677439db08b705ad166fb3c']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 오후 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bd7359a26def409d8772f759f7739499']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29243:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2f3af9bb9c5643edb6906853d02717cc']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_92355eabdd6e48088e94860be8f5433d']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29247:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_38e2b9ec24d44375a19d726a1c35f850']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 45044:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c5a80afaba214e5f8a21d4d19c243b10']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_614886caf7da4e85b9de07366cb3291d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 오후권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b3bdfeac27344eebafa7d665b256bae9']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_37426dfd36bb4ba8b2069d240eefe059']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_377a30f49e9440a6870158a129664581']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19599:
                    if ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_561c994fed684188b8e292102e61112a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6277c2a88a9444ba914e337bf429b0de']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 오후권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_338d1f68794f406fa28d71fa9bc627bb']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 야간권", "휴일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_19dc5567f69443e18fe22ce816ccc37b']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19204:
                    if ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_660df8f3d67d482fba28956fda398f5a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_29408152c7b14457841f63b44dc8cce7']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 10시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fb5386b3a0d041629aa682576068542b']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19557:
                    if ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2ab15c0dc55c4a2d8a13248409dbcaab']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 오후 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d3e5495dfd0a419d91c526b65deee544']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_01fa9a5d41754a41b5fe25025650e933']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29143:
                    if ticket_name == "평일3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ff2e31917bd441e2b0d8cad4ca4cdf3b']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dc2e205d627843b894ac90d1350d1d7c']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1466adf34765486ba5b6195c9a9f704b']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["휴일 심야권(토)", "휴일 심야권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f5a7820eb5c94d89adb4f986b686334e']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19809:
                    if ticket_name in ["평일 3시간권(월,화,수,목)", "평일 3시간권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_144d95693c20477cb227ffb818dd15cf']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cba9c81e96364369866a96925135a194']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29200:
                    if ticket_name in ["평일 야간 2시간권", "휴일 야간 2시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9c9d28df5a4b4265857e305f7695d253']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 5시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2feb7e5c4b4546309e16f3cdd0134d3c']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29209:
                    if ticket_name in ["평일 야간권", "휴일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9c9d28df5a4b4265857e305f7695d253']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2feb7e5c4b4546309e16f3cdd0134d3c']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29223:
                    if ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b3e0b01c6f914383ada2c2bbd9096c41']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6cfbe8c63d6d4a5397b50ca372fa6395']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d3deba983e16417b8252a9588136832f']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                else:
                    try:
                        driver.implicitly_wait(3)
                        driver.find_element_by_xpath(side_nav_xpath).click()

                        print(Colors.BLUE + "제휴주차장없음" + Colors.ENDC)
                        return False
                    except Exception as ex:
                        print(f"Error during process: {ex}")
                        return False

    return False

