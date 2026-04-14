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
    주차권 선택 → 할인 확인 → 로그아웃까지 모두 수행.
    성공하면 True, 실패하면 로그아웃 후 False.
    """
    try:
        # 할인권 라디오 버튼 클릭
        driver.find_element(By.XPATH, radio_xpath).click()
        driver.implicitly_wait(3)

        # 확인 버튼 클릭
        driver.find_element(By.XPATH, confirm_button_xpath).click()
        
        # ---------------------------------------------------------------
        # 💡 [예외 처리] "입차당 할인 한도 적용 불가" 팝업 감지
        # ---------------------------------------------------------------
        try:
            Util.sleep(1)  # 팝업이 렌더링될 시간을 잠시 대기
            
            # 팝업 내 텍스트 확인
            limit_msg_elements = driver.find_elements(By.XPATH, "//div[@role='alertdialog']//p[contains(text(), '입차당 할인 한도 적용 불가')]")
            
            if len(limit_msg_elements) > 0:
                print(Colors.YELLOW + "⚠️ [입차당 할인 한도 적용 불가] 팝업이 감지되었습니다." + Colors.ENDC)
                
                # 팝업 내 '확인' 버튼 찾기
                confirm_btns = driver.find_elements(By.XPATH, "//div[@role='alertdialog']//span[@data-i18n-key='confirm']")
                
                if len(confirm_btns) > 0:
                    confirm_btns[0].click() # 부모 button이 아니라 span을 클릭해도 이벤트 버블링으로 동작 예상되나, 안전하게 클릭
                    print("⚠️ 팝업 '확인' 버튼 클릭 완료.")
                else:
                    # span을 못 찾은 경우 팝업 내 button 태그 검색
                    btns = driver.find_elements(By.XPATH, "//div[@role='alertdialog']//button")
                    if len(btns) > 0:
                        btns[0].click()
                        print("⚠️ 팝업 '확인(대체)' 버튼 클릭 완료.")
                
                Util.sleep(1)
                
                # 팝업 닫은 후 로그아웃 시도
                try:
                    driver.find_element(By.XPATH, side_nav_xpath).click()
                    print("🚪 한도 초과 팝업 처리 후 로그아웃 완료.")
                except Exception as out_ex:
                    print(f"⚠️ 로그아웃 중 예외: {out_ex}")
                
                # 실패 처리(False) 반환
                return False
                
        except Exception as p_ex:
            # 팝업 체크 중 에러가 나더라도 메인 로직은 계속 진행 (로그만 출력)
            print(f"DEBUG: 팝업 체크 중 예외 발생(무시됨): {p_ex}")
        # ---------------------------------------------------------------

        driver.implicitly_wait(3)

        print(Colors.BLUE + "✅ 할인권 클릭 및 확인 완료" + Colors.ENDC)

        # ✅ 성공 후에도 반드시 로그아웃
        try:
            driver.find_element(By.XPATH, side_nav_xpath).click()
            print("✅ 할인 성공 후 로그아웃 완료.")
        except Exception as logout_ex:
            print(f"⚠️ 성공 후 로그아웃 중 예외 발생: {logout_ex}")

        return True

    except Exception as ex:
        print(f"❌ 할인 처리 중 예외 발생: {ex}")

        # 🚪 실패했더라도 로그아웃 시도
        try:
            driver.find_element(By.XPATH, side_nav_xpath).click()
            print("🚪 실패 후 로그아웃 완료.")
        except Exception as logout_ex:
            print(f"⚠️ 실패 후 로그아웃 중 또 다른 예외 발생: {logout_ex}")

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


def handle_multiple_cars(driver, ori_car_num, park_id, ticket_name):
    """
    다중 차량이 조회된 경우 각 차량의 '할인 열기' 버튼을 클릭하여 처리
    """
    try:
        driver.implicitly_wait(3)
        
        # 모든 차량 번호와 할인 열기 버튼을 찾기
        car_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'text-xl') and contains(@class, 'font-semibold')]")
        discount_buttons = driver.find_elements(By.XPATH, "//span[@data-i18n-key='할인 열기']")
        
        print(Colors.BLUE + f"조회된 차량 수: {len(car_elements)}" + Colors.ENDC)
        
        if len(car_elements) == 0:
            print(Colors.RED + "차량 정보를 찾을 수 없습니다." + Colors.ENDC)
            return False
            
        # 각 차량에 대해 처리
        for i, car_element in enumerate(car_elements):
            try:
                displayed_car_num = Util.all_trim(car_element.text)
                print(Colors.BLUE + f"처리 중인 차량: {displayed_car_num}" + Colors.ENDC)
                
                # DB에서 온 번호와 화면 번호의 뒤 7자리를 비교
                if displayed_car_num[-7:] == ori_car_num[-7:]:
                    print(Colors.GREEN + f"✅ 일치하는 차량 발견: {displayed_car_num}" + Colors.ENDC)
                    
                    # 해당 차량의 할인 열기 버튼 클릭
                    if i < len(discount_buttons):
                        discount_buttons[i].click()
                        print(Colors.GREEN + f"✅ 할인 열기 버튼 클릭 완료: {displayed_car_num}" + Colors.ENDC)
                        
                        # 할인 열기 버튼 클릭 후 UI 반영될 때까지 대기
                        Util.sleep(2)
                        
                        # 다중 차량에서 할인 열기 성공 (이후 기존 로직이 이어서 처리)
                        return True
                    else:
                        print(Colors.RED + f"❌ 할인 열기 버튼을 찾을 수 없습니다: {displayed_car_num}" + Colors.ENDC)
                        return False
                else:
                    print(Colors.YELLOW + f"⚠️ 차량번호 불일치: {displayed_car_num} (DB: {ori_car_num})" + Colors.ENDC)
                    
            except Exception as e:
                print(Colors.RED + f"❌ 차량 처리 중 오류: {e}" + Colors.ENDC)
                continue
                
        print(Colors.RED + "❌ 일치하는 차량을 찾을 수 없습니다." + Colors.ENDC)
        return False
        
    except Exception as e:
        print(Colors.RED + f"❌ 다중 차량 처리 중 오류: {e}" + Colors.ENDC)
        return False


def process_discount_for_park(driver, park_id, ticket_name):
    """
    주차장별 할인 처리 로직
    """
    try:
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
            if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='discountItemsDataRadio_fe7e280c050549bf8b01b33df2cc777a']",
                    btn_confirm_xpath
                )
            elif ticket_name == "휴일 당일권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='discountItemsDataRadio_d5b38ccaac154bbe88d36da38c5d46e6']",
                    btn_confirm_xpath
                )
            elif ticket_name == "평일 5시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='discountItemsDataRadio_3b286b02af694a60a2929d474406c78b']",
                    btn_confirm_xpath
                )
            elif ticket_name == "평일 3시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='discountItemsDataRadio_8bed1a623fd463783468f7ee7300fab']",
                    btn_confirm_xpath
                )
            elif ticket_name == "평일 2시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='discountItemsDataRadio_5135ad5bbf044ac5b45b45dfee050306']",
                    btn_confirm_xpath
                )
            elif ticket_name == "평일 1시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='discountItemsDataRadio_7afd0ad4f4c94478b155763727e97098']",
                    btn_confirm_xpath
                )
            else:
                return handle_invalid_ticket(driver)

        elif park_id == 19056:
            if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='discountItemsDataRadio_70b125d06c80438ea71eb0e16ac97453']",
                    btn_confirm_xpath
                )
            elif ticket_name == "휴일 심야 7시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='discountItemsDataRadio_68ff475cf23c4e9092452c62fcd3002c']",
                    btn_confirm_xpath
                )
            elif ticket_name == "평일 심야 7시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='discountItemsDataRadio_68ff475cf23c4e9092452c62fcd3002c']",
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
            elif ticket_name == "평일 2시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='discountItemsDataRadio_c28c84c63d0244d886155b7b07264012']",
                    btn_confirm_xpath
                )
            elif ticket_name == "평일 1시간권":
                return select_discount_and_confirm(
                    driver,
                    "//*[@id='discountItemsDataRadio_2c8624af79234f5db66d32071a97e009']",
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
        
        # 다른 주차장들도 여기에 추가...
        else:
            print(Colors.RED + f"지원하지 않는 주차장 ID: {park_id}" + Colors.ENDC)
            return False
            
    except Exception as e:
        print(Colors.RED + f"할인 처리 중 오류: {e}" + Colors.ENDC)
        return False


def check_discount_open_button(driver):
    """
    '할인 열기' 버튼이 존재하는지 확인
    """
    try:
        driver.implicitly_wait(3)
        discount_open_buttons = driver.find_elements(By.XPATH, "//span[@data-i18n-key='할인 열기']")
        return len(discount_open_buttons) > 0
    except Exception as e:
        print(f"할인 열기 버튼 확인 중 오류: {e}")
        return False



# 기존 코드에서 중복된 부분을 이 함수로 대체
def web_har_in(target, driver):

    # ======================================================================
    # 💡 여기에 변수를 추가해주세요.
    # ======================================================================
    car_num_xpath = "//span[contains(@class, 'text-xl') and contains(@class, 'font-semibold')]"
    # ======================================================================

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

                # ======================================================================
                # 💡 여기부터 새로운 검증 코드 추가
                # ======================================================================
                try:
                    # 1. 화면에 표시된 차량 번호 요소가 나타날 때까지 최대 5초 대기
                    wait = WebDriverWait(driver, 5)
                    car_num_element = wait.until(EC.visibility_of_element_located((By.XPATH, car_num_xpath)))

                    # 2. 요소에서 실제 차량 번호 텍스트를 가져오기 (예: '04마3127')
                    displayed_car_num = Util.all_trim(car_num_element.text)

                    # 3. DB에서 온 번호(ori_car_num)와 화면 번호의 뒤 7자리를 비교
                    if displayed_car_num[-7:] == ori_car_num[-7:]:
                        # ✅ 번호가 일치하면 정상 진행
                        print(Colors.GREEN + f"✅ 차량번호 일치 확인: {displayed_car_num}" + Colors.ENDC)
                    else:
                        # ❌ 번호가 다르면 로그 남기고 실패 처리 후 로그아웃
                        print(
                            Colors.RED + f"❌ 차량번호 불일치. [DB: {ori_car_num}] != [화면: {displayed_car_num}]" + Colors.ENDC)
                        driver.find_element(By.XPATH, side_nav_xpath).click()  # 로그아웃
                        return False

                except (NoSuchElementException, TimeoutException):
                    # 검색 결과가 없거나, 차량 번호 요소를 찾지 못한 경우
                    print(Colors.RED + f"❌ 차량 검색 결과가 없거나 요소를 찾을 수 없습니다. (검색어: {search_id})" + Colors.ENDC)
                    # 현재 페이지에 로그아웃 버튼이 없을 수 있으므로 예외처리하며 로그아웃 시도
                    try:
                        driver.find_element(By.XPATH, side_nav_xpath).click()  # 로그아웃
                    except:
                        pass  # 로그아웃 버튼이 없어도 그냥 넘어감
                    return False
                # ======================================================================
                # 💡 검증 코드 끝
                # ======================================================================


                # '할인 열기' 버튼 있는지 확인
                if check_discount_open_button(driver):
                    print(Colors.BLUE + "다중 차량이 조회되었습니다. 다중 차량 처리 로직을 실행합니다." + Colors.ENDC)
                    # 다중 차량 처리 로직 실행
                    if handle_multiple_cars(driver, ori_car_num, park_id, ticket_name):
                        print(Colors.BLUE + "다중 차량 '할인 열기' 클릭 완료. 기본 처리 로직을 이어갑니다." + Colors.ENDC)
                        pass  # 성공 시 아래의 park_id별 할인권 선택 로직으로 자연스럽게 넘어감
                    else:
                        # 다중 차량 처리 실패 시 로그아웃 후 종료
                        try:
                            driver.find_element(By.XPATH, side_nav_xpath).click()
                            print(Colors.BLUE + "다중 차량 처리 실패로 인한 로그아웃 완료." + Colors.ENDC)
                        except Exception as ex:
                            print(f"로그아웃 중 예외 발생: {ex}")
                        return False

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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fe7e280c050549bf8b01b33df2cc777a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d5b38ccaac154bbe88d36da38c5d46e6']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 5시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3b286b02af694a60a2929d474406c78b']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8be1d1a623fd463783468f7ee7300fab']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5135ad5bbf044ac5b45b45dfee050306']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7afd0ad4f4c94478b155763727e97098']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19056:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c28c84c63d0244d886155b7b07264012']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2c8624af79234f5db66d32071a97e009']",
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
                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                            "//*[@id='discountItemsDataRadio_f504637c9f3040aa8d3aa891a2715349']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4a97c72e852e4512aed19f50037fc331']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_97f4380e9e974004a81185e09f361b12']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19195:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_44399cdcbf0f4441aab566bae1d011aa']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_115896801df44a2cb1ff2c1c94b69d1f']",
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
                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_86adcd7405ed408eadbeb63d93de304a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0d5e0190a8754e1184d8490cce69ede5']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2cfd293970394d01a8d9702ea846de65']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19410:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_966ce3f79c11434b87d309424dfad8bc']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_074920a0444b4dadb6808ce47f602011']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_759fe7eb5778410a86613c5a89d1b4dc']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5f1421c404084c46a9b637e1d9677cee']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 5시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0a5c7d594401410682e5f07d8527cfd9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_02d2716131394ef99ef3b49d34286b32']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7bb11a6a4cac40e4b572903f8e131e90']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_43a849f5ea774c149beb2303a217a777']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name in ["평일 11시간권(월~수)", "평일 11시간권(목-금)", "평일 11시간권"]:
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
                    elif ticket_name == "평일 야간권":
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d2b3901310474031bbc95bbda8c86574']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_26ff22b537b9435f92e55fbce59272cc']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5f745696e17f48beb39b1173d8a0f5ef']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bd1a796f039849dc9430c98c9eb70aaa']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19736:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6def1e0b873846c0a83e767fd74f9995']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8d9d902931214ad0863b20bd5d43176f']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8c88f066e3e54e4f9db7df7d9fb6ddff']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_96ed5fc143e34c74aad7b3a2bf7d9090']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name == "휴일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9e7b07953d2d4aff9172b693f541b051']",
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
                    if ticket_name in ["평일 3시간권", "휴일 3시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f2dcdaf4f4884fadbbf6cbed9cf671c5']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f5a09aa3a9bf44bf8aa6dfadb8d69a0e']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_56ebbfff25f0468b9c6e4173993c4371']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 1시간권", "휴일 1시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b8d902d38e3d482d855fd931f32843d2']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_317ffbdb0a9c42a1a6bca64e5213fdfb']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 저녁권", "휴일 저녁권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9a4f50e44fdd4d0c88f42ba7671c0c5a']",
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
                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0c6a13b59e444d53b7d6b9727277fc81']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29123:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_adef32f33701476893e91c9d37ab07df']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_46aa2690f3a4483481ce1b035d42f568']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7a42edfb53944001903fc500dcfbe1ed']",
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
                    if ticket_name in ["평일 12시간권(수,목,금)", "휴일 12시간권", "평일 12시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f8dae01ae4734d9da9b6f30e5037c51f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["심야권(일~목)", "심야권(금,토)", "평일 야간권(일~목)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b9cfba1087584364ac319b562102d058']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7f4ff534c47945459bf4f6808dd07321']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a10e37f6e7e147ddb8b7728097244e71']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_af12d4c076d24fdea820508c910eae22']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a881103a80d54614be96732f971bb277']",
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

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4e279fdc4a5d442d9d26b2f8f9f3a260']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_051ec274f22a4ff0ac56bac6ec9f941e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "추석특가 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_af51456e506441e5af2306f5b3296501']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_52c14814da124f42a328b6c3f112a5d1']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19171:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c6b465dbbb9d431bb8659025e52851d2']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 야간권", "휴일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_330b95139d0a4c14a1c2e1a85fa90b32']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_13a6a9669a624231868dd571b4a3f6cb']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_148a3c392fab4c119d6508f642edd340']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a261280901f74312a15e5284b9e1f534']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 16360:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_17ae285ede5a48b3b08d7d978c697100']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6a32d0f4dcb44425b347487e046112e2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "추석특가 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_99f2860a674641bdb71917dbc3e85b48']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "야간8시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bca160232b82478ab4ec7712a2df4112']",
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
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ac0ceff7eac54fcdbc0d4162e1c446f7']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7f0e706a75bf4869bb7a9bb4dd23be4e']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9dd1a279b9814007aa09406a8be1560a']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19087:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if  ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name in ["평일 심야권", "휴일 야간권"]:
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

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1af1440727d843d7a9de059b98b3593c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_61c1fc576d6f4da38133e1db419095c6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_702f274a24e0444085559cd0d8736bf8']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_93575b4b9ff64f578e458b2d863c8bae']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_66c9e8671be54beea0195a0071b60f26']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "주말1일권":
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

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "추석특가 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bc8080ffa075449ab6e84e0152b5ab6a']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_906d8473867a47a19591faeeff129e50']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4022c2976a0144e797191d5a946dee64']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6fd1b49216d448c7998dcb16de405ae8']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_05ee060b94104543a0355f149bed5850']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 12시간권","평일 12시간권(월~수)", "평일 12시간권(목,금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_00bdf2d4491a4398b77cc6575e8528ea']",
                            btn_confirm_xpath
                        )


                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a56bd119b1384fcea99a780051a0a39b']",
                            btn_confirm_xpath
                        )


                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_316fbff1cbcc4168a8241f60ea041a92']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0f7a05944ece4c6688ad7e7af172d050']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name == "평일 3시간권(수~금)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6c021defbc784d339f1dd0444fcd98f6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권(수~금)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_389101a9cd5d48e59e712ecb22aca802']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권(수~금)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fa20d02350684190959f3c1dca68fab0']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권(수~금)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_939fedca1e2149bc9145b73700bd00a2']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "추석특가 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5e2536fd9be7431db486f7ccf4aab7b3']",
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

                    elif ticket_name in ["평일 24시간권", "휴일 24시간권"]:
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

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cec4a0535bb544098d5c5d0cc546d59d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7ea86a5e289947d988d85275f4a89733']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d03492f3e76040bdbb6c7b3f0703f22a']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_12f83b69d8c94c049168bcc1a078e119']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 3시간권", "휴일 3시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_17fc1fa8c61e454babd17fda649fa51f']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fa86ec6632fa4ab68647d1552132cd47']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 3시간권", "휴일 3시간권"]:
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
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_95d168afe479498cbdcc058e9160ca23']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 24시간권(월)", "평일 24시간권(화)", "평일 24시간권(수)", "평일 24시간권(목)", "평일 24시간권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b44235086cb44e6f9151f53ab5ffef9f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b68c315032c3494baf9e460f66f6d55b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c4eee6e6a2a04bcfa344e2074d3dc64c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_10aaa0b5c3fc4fd185817168ecd9df32']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_67b93bf40b744a9b91a8d5b144928871']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d40872b8f9394408b95fef2ba9768346']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8e5f5772afdf4fc4817337bd1399ea12']",
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

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19914:
                    if ticket_name == "평일 당일권":
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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


                elif park_id == 19503:
                    if ticket_name == "평일 12시간권(기계식)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f45725102ab04cb78ff7888c8cf68b4c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권(자주식)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b9f87d1ed9c24ff19215d103fb4a9b37']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 9시간권(기계식)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4a5b0a8089ac4151bd9ef8b1c25da4c6']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19241:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bd3487c993b4422e92eb04d44765ce77']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c6b49f6c1aa646bb8d8d7bcd9339d122']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2a5a72cf658c48d6ad6d22fb83545ea6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1112572f82b849ecae7a92dd9fe313b1']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7a8e137287674f0f8a8b5de984711843']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 12시간권(토)", "휴일 12시간권(일)"]:
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
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_da2d498e4d8340b4b474a267e42ce04d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5468a011614f4c38bc2bacb03181f85d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ab5e55eebd8f46a89b893d63740d282a']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0e63aa72d1d7456d9c9856350c716422']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_76865bbe4db64d0ea8c3f8e69ea9cbc1']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_982b5eea171942a98fee24d34d2b002e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 10시간권":
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

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_803fe179044b4cb78d068365fe867d8b']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_09666257e3394bac9640409482cf1757']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2d157d00bb054353be094b671471d63b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_50b4f0cd69ba49f3a3a4bbdc6136f7ad']",
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

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
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
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_42944cd268d3410c83e9e641e22b5054']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_74b69bc572d949a48fee277f1d5c1e7f']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_630fa46b6ad24296ab15a596750c4a88']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19614:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3ba2ee7fad8f401b8759bf4ab983424a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_74b69bc572d949a48fee277f1d5c1e7f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 12시간권(월,화)", "평일 12시간권(수~금)", "평일 12시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_78cd981b00f149caa968aa397ed3da87']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_554f0629172549e09c79fa2f38c70472']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a4eff894f9a549a393ce1858bcfa5a09']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_69934331d9c54221b13604046b723995']",
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

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                            "//*[@id='discountItemsDataRadio_83485acf9fd64c2b87055d9fabe73ac8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_aec721a080eb424f8ecc0a19f2d28680']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_330c366c0edd4a418e0b5ff1cd8b965a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e60cbba400264b85812e884863f157de']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7ff783d174964168a6af67e977472b8a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_14e426c9ce6b45c08b993c9ed4be04df']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19925:
                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_90b077e907794c6fa4de67f0f23662a0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_526cc2a67fde40d9b35ec8cbbfe294dd']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4ac55ffb011d4e488ba903bf0a3b8f5c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 5시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3e76ca9d4bc04da191fc50966cbbef61']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name == "휴일 3시간권":
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_848211901017491cbee0da6f867c6473']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cf07b752349246448528b1002d1e3d16']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_05fb44d49c2e424e8be8e9251bbba74f']",
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

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5e4924c5b9964ed3a724b7d13b6ea79c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b7b7a8b921d04c9ba1097b970603e349']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3be54af32e92446e9153fc29874f9c4e']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "휴일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a95126f117404394b999259d6447c8aa']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bead14a020634ba1bcdb10fa4fb4d227']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4b7b0a9d4529418ab2c85c46f3ac71f6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c428bcbea3704cf6ba4b99ac41f8c9a0']",
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d4c93184281e4816ae0cf26c66874eaf']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0d8fc56ad17d47b7801cdb29a3f54940']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8324beb73d504292ac70b9ec847ea309']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ce0c21ea73514663874a066dd9cb16f9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f4a9dabc9fbc4ecab4a9a8545a7840ab']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a584211ac8cc4da79d0aed26081fc1e9']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 11917:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name in ["평일 야간권", "휴일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_104d9d57a69a4698be3086f4d6d75a47']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19491:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_577409ad1e044925b7e3a38f732fc5af']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
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
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7f7f09a886784d2c830c0bc02bbbcffe']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "주말 당일권":
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

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name == "평일 5시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2fa7cdecb49e47fa9e31220f98eb7372']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a68306b2e45444128337618725ecbf68']",
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
                    if ticket_name in ["평일 12시간권(월)", "평일 12시간권(화)", "평일 12시간권(수)", "평일 12시간권(목)", "평일 12시간권(금)"]:
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
                    elif ticket_name == "평일 오후 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bd7359a26def409d8772f759f7739499']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e0946d0469f34b58ab9a44a9bb81e120']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c6d274f8fbd94dc7a669472fd36c74d1']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_91ed18ed532149aa86ef326dc1d56d67']",
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
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1e51f2c9ba0a4ca88f83d30aafe47968']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_48bae29a4369404cb64e64f652dbec49']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2a412b409dd0454aaf673d85f4c5c3fd']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 45044:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c725c186d0b547cb823d880885e5a53d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_754c6deae28b4a3ebcf715072014c6b2']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_46ae1fc13c994d6283eea2548f4d81f7']",
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
                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cba9c81e96364369866a96925135a194']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_144d95693c20477cb227ffb818dd15cf']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6569e83614aa4f229b8e9fae33829b70']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f63fed33d2804adba1414fe1f502363f']",
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

                elif park_id == 29194:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7f66e450817f46638dca16a57f12c1db']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cef95359c2074afa8624451f8d0be916']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19926:
                    if ticket_name == "휴일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c8cd67c81a764b04819830a95900bb1a']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8b5ce5e4215640db816ddb910c8af9bf']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19916:
                    if ticket_name in ["평일당일권(기계식)","평일당일권(월, 기계식)", "평일당일권(화, 기계식)", "평일당일권(수, 기계식)", "평일당일권(목, 기계식)", "평일당일권(금, 기계식)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_55e6c521ec7647558808586e6cad17cb']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f0ed20a005294c198da0ad028acdd27f']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f8ab3eb552c54ea98a87e58477ed02e1']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0cc3776502d94ecf91f498a7eb512047']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29227:
                    if ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2a829be2435e4f049f72614f5ecc8b73']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 오후 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c71359d6cc9446b2b18d29de977adafb']",
                            btn_confirm_xpath
                        )
                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fbbad8ba35d042468a7e45129ce10b31']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29145:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5edd07868bd44e5399c1f8ff6eb4921d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "2일연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b509dbcf981141b489127ef28a7131dc']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "3일연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fa5e4f3b652d48cc93a05a6e7397f555']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "4일연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_90a2a57a4aa2417e8604d4ff43af1623']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29130:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
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

                elif park_id == 19214:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)","휴일 당일권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_38d97e4213284ede9678745c43acc6c9']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29224:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_66d01d09af0f4b31b71d1bad37ce827e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bf0b2306372946209324997ed5f6b411']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2771b96db7a9458b8c22c8150cbb43f3']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_da925a84d747446981c24a017fe530aa']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 12903:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_11fd2bea1da84eb283ce8955688d1603']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_127a6ae581184797898257a25c111030']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5e7d03723a17463ab8f09d301045e170']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 35529:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6cd3a6b60fe7481caeffdad2644f4e6d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_050215df1ca44cc78ac69f07f2ff202b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_644b9f48bf4f4fb988c2a52994fda2d8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dcae5612ca1c443abffe8a4c385ef09a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ea3ac2e8adc243559bfb14ebc51f12c5']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19618:
                    if ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_950399a0d7f24c3897aadde23ccc4b52']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2f14a992fac540c1a1130096385decae']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19846:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c8dc53fc13d44676b1b74d9a074e052c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8a020a8474fe4cabb6d572ffe90d7463']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_208276e779214a1ea9e8d24a1867860d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 시간권(3시간)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_eb6c0e624ad745af9f666f7b5a2fb7ca']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b0798a2952914d47a6603cb849016434']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19142:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_726c3ea3c69847bb90c3118a7ef62e5f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 12시간권(월~목)", "평일 12시간권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7415ecbfb25642bea04d194de8d1876d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "주말 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2feb4bb5a97b415889f36376d4839e83']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 야간권(월~목)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_de442b35f220484c8bbae9c4e17b62ad']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "야간권(금,일)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e59d13575a6c42399981b9e76a527939']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_74b4de75fb274736858b9e6fd4034bfe']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29221:

                    if ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_db30572765b24feab9638b84f8d6fda2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_02a0dd74f2f644ca9844dc8915b35f1e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bb1d24f5a5f44aed9cb0f1365ce7cdc5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4480e471d7164f2bbac5df2061c64da2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_82e7f2956a3540c5a719f10a57379718']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b443d96fc2214cb2963e72f86b0648b7']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 12750:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c640356f41de4d8dab45358210865577']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["심야권(일~목 전용)", "심야권(금,토 전용)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9bf0851c9a1041d6b93303228a154199']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8c713117835b452db97b394c568c1d26']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b4bec7731a0c43af82d94b4e9d2c6c8e']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3e7d4c335588411eb8f6fa3e8906c44f']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4964476714b44b398da195860e3af5a3']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_818dcf866474409c9a7d235fb6deb215']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19153:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_99689c13251f48759895dc87c7e2a907']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b0568e07579d4a518af991cf613a767c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3fc5873b79304bdfb803f84b7ceb4795']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f02e21b08cc64f88872df277c0cdf20a']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19835:
                    if ticket_name in ["평일 당일권(월, 자주식)", "평일 당일권(화, 자주식)", "평일 당일권(수, 자주식)", "평일 당일권(목, 자주식)", "평일 당일권(금, 자주식)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_08add998bd244aa88a8948df3df2c785']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 당일권(월, 기계식)", "평일 당일권(화, 기계식)", "평일 당일권(수, 기계식)", "평일 당일권(목, 기계식)", "평일 당일권(금, 기계식)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_08add998bd244aa88a8948df3df2c785']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권(자주식)", "휴일 심야권(자주식)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c5fddc6d293e41e9b4aa933f2200d7db']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권(자주식)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0b244cfc7fa549e1876ab96fef29330e']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권(자주식)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9e0e2d7b1d8042b093ea765192e17149']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권(자주식)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a2997dece2fb4f289e949b1532b5439c']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "휴일 당일권(자주식)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_88db939100cf48ea9b6546e5143d56ab']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19857:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cfedf48b2ca841698f6b4cdfa9470c8e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(일)", "휴일 당일권(토)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dbd76b8ec8024bd8b401330d577a1ef6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_029d437c9b1741738810b16269d9dbf7']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ef1a168b25be46b6a29740597c44d6f7']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e5fc1b5b29b541bc9597d4d421e16133']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19851:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b52f741f53ec46ca968459c80b1fda79']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_52f590baa69048a287adfb8e2c705267']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a93d592e17d845c3bf710d71249c89e4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_62385790d38247acb87287da01d18ff7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_de422e2221034ce98c6b75400e9af7b1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b4b16777896640f598109ce117427440']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29259:

                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0691664a2ebc4a9faa8467a88d176197']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dd143c0e50824456bb1c7b031cf1abaa']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "야간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0d7f9b7f988344c396db9de3fe03273d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e200c788d0d8498198e23939ac180691']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19520:

                    if ticket_name == "주말1일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_642fe68e6d7b49f7885d63817e4a2f0d']",
                            btn_confirm_xpath
                        )
                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_120f038c27a64cf1b6de33db6edde33a']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29147:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f53f51a7b5af4d3594d9a2e35f67fc9b']",
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19224:
                    if ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_40494991a8a640ea817c09520b1f11b2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b2d58bb6f68646c494ad55a27246709d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_485f79192e294a00bee8da991901a387']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29246:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fe153334fc1748d5bab67c5681a61534']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9f32a21e73394ce79f062bbcf506a699']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a6c3388396a04ddc9806c3077bcca863']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 16170:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1617920b3b9c4384886ad9b2b7610ce0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8dc982afed0742e997569835113c92c1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f7eb7e30e0c14432ad388fd42be408f6']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19948:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5a5fd30986024f7a930d8febdbf47feb']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1287959daec64ede8df25f5becb63330']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e5b66f536c0e42d5bf0d3fd804f5f350']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19203:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a6a6ad2284234d3ba308cc5b6141b888']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cac23d7e044e4c25ae607d4647c1eecc']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_46c0df4ad84c41d0b0176700a24d0e97']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fe4ee277912f4063a0091305bd8f95b4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "주말 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e3866b6626b748d991372fae842915fa']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 야간 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_02a176524fce404d8be77d3698ad0e0f']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29274:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a48b0c27199c4d42802ad58a496b03d9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ac27b2c213e1412c956d6a5cccddf7e5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_151adedd4e25494b99bac8b2e4c7f2b2']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19504:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6d5103ae00674b0ab8cdb2d5e00a5dd6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1a0a4cc7402243bdaa21ccd2033fc0a8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8e70e5df94824ffa970a80bbda14b472']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_30bbc1a5c5364520b90a88bfcacb3cee']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1cf1806daab340d484bb08af694c7ee1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 야간권(일~목)", "야간권(금,토)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5288f300394943c9a945438181ddac27']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 29101:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cbf1710a7259451da5fd31d64da94cb5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_06734a41625449c1b6887c561f77b053']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c2d8f99cc42845d4b81cd59aca5aa52c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2936bf5ad9004df7ab6e19001d1454b7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_83d2a344490b44d18a145c332eb9c246']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 12074:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_791ebcc7361c4b54b0c3470aec110e5a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 4시간권", "휴일 4시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5235dfd1d4ed4d029810aa191213b93c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ac5314727b8145e2a176d9d50c63ba08']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19230:

                    if ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cbe9d04716594418879b5d1212c04694']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c997c32ae6984144b719f62d66951e41']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29271:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fc1b1ec2b1d64ffe8299f81239ffe344']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6fa3d4dcdac4460490a619279df3437b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cb02c9c4ff4c4fed80449cf4ab7eaa0e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4a6439e368c946f197ee933cfcd2bbeb']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29270:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ecae952d1bd74adb8df8eb908df1c521']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_00a89616f21f48c7b25429dfeb5948f6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_991bb79dfe41494095d0a41d0fe4bba5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ab2f504bb5204689a40a8614364c3448']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19633:

                    if ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3a2576735a434667ad3cc5fce9748c74']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f1fe98be50254c6fb6198e8ebf974283']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6c3b9b901b894088b7c9d11d2d4b3477']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29179:

                    if ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f9fd0925186c4b76907c7335e908e633']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "2일연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_65fa5ab7a21645e983cf3f0760ea4421']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "3일연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_25e2b1397a0248be972db65ae3b0d064']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29280:

                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ae10a638c9f3467aaf575f71d17a2ba8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 10시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c4cbc67be7d14380a56507b90371cf4e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b85003375a3f446d867afdfb35453da1']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29237:
                    if ticket_name in ["평일 3시간권", "평일 3시간권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7a86d23e719a47999bdb4d11378e14b1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권(월-목)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0f15717500d34a39839efe54a4b8d15f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "심야권(금~일)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_19a61e30f40c4e968ce0e02046bd82db']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오전 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2feb1bb076014a3f80a3c6c474277961']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 3시간권(토)", "휴일 3시간권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_85ae2abffd2f4a4ea3ec07005f9c352b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 10시간권(월-목)", "평일 10시간권(금)", "평일 10시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bfa5c4fb9f1d48edbe6322af81ab3a59']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19272:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3a4830af71e74df792f3c233f4cc557b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1a16f062b15c47d98b11db9eaa5d36d4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_781f744e16a24bf19990cbea64b591e5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6b5152d616184e2c955228aa8ac0204e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_63faccf71cb54cf8a48fb7aa2e9f0f3d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c1c7ffb1236542aeafca166d3f2a9984']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0a815fc5dd754645a03d6e59a3ee4b8c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "2일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1da7f3e5bd294a0db65a2105a90f974d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "3일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2f60def1c83c40e3a673ad4e45fa26da']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "4일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7e9d6a7db01b4339b5b7dcb85f596376']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "5일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a2053fe6415940e3a95465ad6d3675b7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "6일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7b4e80a388a340cf8549365ebcb82bdc']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "7일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4271f09df29e44adbdabc1ad2bc09a8d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "8일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b39265022b894c0b8512774ba964cb11']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5d42ca9abb4b46b28d8e9af1b026e2a3']",
                            btn_confirm_xpath
                        )


                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29187:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0556a075a77e4207a43bc5cf9fcf4613']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_257880fa290f467a8f61501b15899b5f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_29b4612d5f364568aa2df1e4bfbeba61']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_acb637bd9a3a4b50ad1e9976bbf1e9f7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_aa2cf46a0e7c4907b5e670cff155e03a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c9ce0d03a11242359f05649c24b65a36']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29142:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_384dae692c9942b6bf07b5b79ae50338']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_71172e9c8fdc4118b5d75700fd206c40']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 3시간권(토~일)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3a2dcb31f9f040b2b57f8598f39d6722']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1d52e267718e480da816a614874f5792']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권(금)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5cf4cc1aacff4a9a99193621a6e96ec3']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_38b558fc03be49239b701a56c59e89d1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e2b081bddcd34a279d34c5c800b62424']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19420:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0c1b812dc032492393abfcc18f4557d0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_bdcfc6c4cbe3492187afc30201970bd9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 심야권", "평일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4f27ad6262844e52a361d86ab8f9282b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9eb8c67a9a59474292708ea46e319cb2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_814dd5fa668944c385214a2e0bc9b690']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a8d1f1a0c6064e409cefe2b37c9c96c5']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 18958:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5a0d97e6395948f7916d5772d648d5a5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_39ae2cfe74ac4589b72a9e00f3b150b5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "추석특가 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_32fa753480aa482ba07bb44d73f83065']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 12시간권(월~화)", "평일 12시간권(수~목)", "평일 12시간권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_432bd48bf490489bb26d05abe943485e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9dbae9af93de40348acf7eab784e85e9']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19441:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5a0d97e6395948f7916d5772d648d5a5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_39ae2cfe74ac4589b72a9e00f3b150b5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "추석특가 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_32fa753480aa482ba07bb44d73f83065']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 12시간권", "평일 12시간권(수~목)", "평일 12시간권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_432bd48bf490489bb26d05abe943485e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9dbae9af93de40348acf7eab784e85e9']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 18989:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8d220a04639b43659d1f395687053bf5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "주말1일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_867130a83f93464290deac43fc5f26a8']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19441:
                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9c376a3249cb4c559437916756221f42']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_00d1c2bcc8974d329056bd26bf6882e6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5c1255fa682c47289a18e81e335f6215']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3a78912a9d0a49d2a240492af3a0534d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fb0c262a3ca044fca147181ac3b9ba20']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29250:
                    if ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cf12ada61c2545f897321eb3058cc613']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4e8d6782f61849e0b205ab57e9e81be3']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "2일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b5f5fa5af36c413d871f9ba6e5ddf604']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "3일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3355273f5316439a84a5f7ef2d58c7a8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "4일 연박권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b001fb3a16f245ef9b8391f33cfcc134']",
                            btn_confirm_xpath
                        )


                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19225:

                    if ticket_name == "평일오후권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_69f544e4a9214b8c9cf18672b26d44ca']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 심야권", "평일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7f602a294fe3482295470823e25ebf72']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1447ab2006f2486a86f74966df396f0c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2decc6e1433a4f38958687766d42e643']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_234824341f3e4a2c8dcc360e3fd1a484']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_99717435ed434bf186ec1f5b91259334']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19944:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dd2e5eb4d846470ba97de5d3204e92d7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 심야권", "평일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_39f69e1e17054dc584cfa595e7d136df']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dd4ffa1a4a514f87b94cac8f049b2a23']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6f9e6be350a242ab9f2975d94f76a874']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cbec6575f83740cdb5fa65e4761fd6f8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_904301fade514a148378f19be4887575']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29344:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d546a46b29694c289bc9fd139d7d79c6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_21c2cf8d925a4ba1abe00d1d05b5d22e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f5f6b9e3d034411486d23dbe46e674d7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 야간권", "휴일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6e9fe40acb944b5dbd08296062d847cb']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19879:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_da13d337796f44bc8f0f726ae637bdce']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0a10f7787af848faa4147c0dbcffa6f4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ca76b2a9fd3043f49db52334aad3c836']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1d1fe6ea05d146eaba6fd93499ee5bcd']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_747e2ee9b0604a5782c337ee84f0eabe']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_2f5ab8f1a66f4342bc83c5e300447467']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19561:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9c376a3249cb4c559437916756221f42']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 3시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_00d1c2bcc8974d329056bd26bf6882e6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5c1255fa682c47289a18e81e335f6215']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)","휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fb0c262a3ca044fca147181ac3b9ba20']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 6시간권(토)","휴일 6시간권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3a78912a9d0a49d2a240492af3a0534d']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29345:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ea3a93da95df4892a877eb15fad31ad9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)","휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_86aab55337b7446c9b829ee742c97029']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 10시간권(월)","평일 10시간권(화)","평일 10시간권(수)","평일 10시간권(목)","평일 10시간권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6f9abae2094e4bb1be9716b11a8859f9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6cd826fa29a74b1981c316bddde61bbf']",
                            btn_confirm_xpath
                        )
                    
                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b78f953bd1774fac85f533af7db627a3']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3e16b48c04574354aa9735b33cdd2c5d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 심야권(일)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e14f77247e5c4cafb79e522ba0c40242']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29289:

                    if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fa0b01f3bd924cb38125c6f41bb41fdd']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_967d96ec7bf8451192bf4694ea415bed']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_12d6c0f99437448c98565ccc2430d8c4']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19888:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4c031656bc8747babf784a8b1ad5951f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a4a177bdf0f2447c91d615ff3fde8fcb']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_810dd7ab71f14d0d8f8ba0462876757c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_254314f69bc6410d9fbdc0d25b62e2ef']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fc23291cdbf14bfcb0793a2e3b4566c8']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 15142:

                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6952d922ac8641a88754000230392e4a']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29320:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a2727af1635b41ad84fc8cfcad93b2ec']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3acdc40f8108442db5bb923e72b26608']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29193:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_cdfbf8a3e4cb4117aaf4f0e9911b11f9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4a03af9ac5224e68bc1a6c804cd08201']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_51417490b6f243edb63669cf059820b4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_565abb9d0d0547b3868d124924af29c6']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29393:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0d73c1fd2d404a6d8b456d62b124420c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c18c798072a04ced807bff1178587171']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ea4893c80e6a4aef8050aab0030539ba']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f1cd17c1e13e4b30a3876e59d509bea5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 심야권":
                       return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f39538be55354232b306498d1d766edc']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 18979:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_acc950dc488e4b43bc2257a14cd82aa3']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_46ccf657d61e4a04a879335d85d4c59e']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4e0bf4a2d7e542c88d1802878867915d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1015ab26dedb4952b5720389aa45a4b0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_64d1c6b02aed4fad8cc07fad97dc41ca']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19911:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e56184eacf0a451a84490b7ffa3a5611']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_983b12f3cac54983a823edf96616ea8a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4e03b443fcea492eb0da6c7bababea52']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dcd7e0533df74a2b9e022f8086dfce2e']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19467:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_aea6c893852648e89caa3f8d600b9b0b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7a0c38a400654f7a8e08d350ad1753f9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f504728348554b888d26b0c701248481']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29477:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3d48faf1c84849dba535d07a30c2e862']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6780afd94d594c3fa4de8e8d3fad4e2c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fdadf9d145104075bd311bd395844464']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19267:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_931bce8b5bd94e2e9ad374a6c328953c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a978dc29ab7f4e81b76b7f9b45b43229']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fc2491835d8e45bfbf5b81b7aa29f299']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ac93e750c09344e8aad771fb9a84e377']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3cbac489abc3405ca5a14f4b3cf4268f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_38daec98112b4b639ff03acc8807922f']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29177:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_14e1176ffe654bb5b7a85f4779877cde']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_481f0e66584d4328b7b5eb84018db184']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f6fe698e643243eebf4bed60291b492a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 야간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8477c5f0601a4064bfae2b9a1bea84b6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_1b4b397f856140caa9de715214132896']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 18999:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9c93453fdc5b4fde85890b134e6e2255']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_057d71e4ee974702a87ef39c7202bf44']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d35092b510c849b39fe998cef844eb53']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c6b6546ac49649f09931c704d8a5c45b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4327bf5e7be5410f980c506820bd4df5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9b879089e42545bbb1d2902fa1b89e65']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0871743f2820471b92989c42fcfa31dc']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19185:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9f87f8b3730548c290894c965f68580d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_137aeedb0be74fdcae38e6653f5fce4a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_137aeedb0be74fdcae38e6653f5fce4a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "오후 4시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0861ceb2b2b64856b8571eb438a13575']",
                            btn_confirm_xpath
                        )


                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19325:
                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f8ce7442397f4a5e8eee397054bf884f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 12시간권(월)", "평일 12시간권(화~금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_81ca874a54b942608271865c6dbf2b34']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_af3c14dc21e64bbc912cde856ca03c49']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권(일~목)", "심야권(금,토)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_114a9b92c6bf43fd9347457044347a4a']",
                            btn_confirm_xpath
                        )


                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19919:
                    if ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b8171d537f1f437694bda920b023049a']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e0285d6b480c470f8a3e8b2b0e9f87fc']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dd1ea2429f6744fdb65604e0533d1fed']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권(지하 6층 전용)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fa2db1e1ebeb4551999250b583ada774']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "야간권(지하 6층 전용,금~토)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a41226e3d35e40788ade1c49803bfdae']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "야간권(지하 6층 전용,일~목)":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a41226e3d35e40788ade1c49803bfdae']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19323:

                    if ticket_name in ["평일 24시간권", "휴일 24시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a152fb62ff2b4f66982588f1072532be']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 12시간권", "휴일 12시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_31fd28088ce7492787ad35f9c26f9eea']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 48시간권", "휴일 48시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5c5d24eb6e4c4d68b0ab60b017819a26']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 60시간권", "휴일 60시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3f9154a6511c4d0587cd45c0075162fc']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_50dbf0ac4d0f4c9aa71f4f1d3d96c9ee']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f4ac21b6926245418f635d467e329a99']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_178e32d0bd614c9789e72c9c945dba87']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29457:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c2e7ee25136644b18e485b972313a9a9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_87181ee7f20141658d5772c7037f068a']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19022:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3ee51056ee0143ee8704cecc40be6de3']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_00457c93086a405b8c9b9873d31db518']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_38443a4a95484d77839fc2cba2cba3c5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6950b977c94c46039242845807b52cd8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_fdd910b3699948808b7687b113ee08fd']",
                            btn_confirm_xpath
                        )
                    
                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_38443a4a95484d77839fc2cba2cba3c5']",
                            btn_confirm_xpath
                        )
                    
                    elif ticket_name == "심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0a32c6482c064449a6e849fa5e71ba46']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29493:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_04e60cb5260f421b9265d3fbe230d916']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d4e04acd6e754140ab67525b0da90ddc']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_def7e3afc1334533963a188b74dcdae3']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e69077994985413eae0add8271cfcd9d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d24104c96a5a4ea2a04f054c5c424861']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 16434:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0ca06c92630149bd8a3de032b588cb37']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_26fb02818d4b438680bc3251bf7778ce']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_dac675fffda24a87bf289f57276d9cdc']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d2e8e2d3b6fd41f2be22c3a296c3ffb1']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3351146aa2014c39bac0ce37315b70ac']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_71f87e56a0784feb8e788ff251dc245f']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29269:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a7fb5a271265408c8cd845a39793ee6d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["평일 6시간권(월-목)", "평일 6시간권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d5d57506ed584a3aa2c36d8a46518917']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)

                elif park_id == 19591:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_55a3aa9578f04562b65a14c4461a3f79']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d1aadebee2114fa48b297655276a618f']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29480:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_60d4d697f69044fb872fd3ae554b7072']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8662e1459a944bfda428c68faea12616']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b9dd736c02bc4f48a0fadcb30aa2f6a7']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_d1aadebee2114fa48b297655276a618f']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29395:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_71b86b973e7045b49647e658d5d6ffb4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오전권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e11b073c355847959d16d3a1b5d58db9']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a6d3cd611b6f48449620aff6a55e98b0']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 20864:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_05adaf30c284469aad694315e99b571c']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0479e6832be54b6ba22736bc02f2c5d6']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후 6시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9936600f398148e7997fa352ec4ede74']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_91dbccdc6a0c4f938084e51b07f025a2']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "2일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_6382a1269ea64af89e96b0182cf80fa8']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "3일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b53fb9a7b1c54747895b70b365eb866f']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "4일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_758df8b796104ab99dfd6edbf1997ba2']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29192:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ee7ff26a5aa44df4a4b96f67227831ce']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7c2db4954dc24f9bb29f16a390fa3c82']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 야간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a1a42d2bd4b74ed79016fa12d358cb2d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5a3b988fbd6d4c11a91a0dfa8d3188f4']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7c2db4954dc24f9bb29f16a390fa3c82']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 야간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a1a42d2bd4b74ed79016fa12d358cb2d']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29388:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_436c522be401464aa657e8d9b1fd6628']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b2b0a5b2e1b246d9a8ab4e7812665c9b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(토)", "휴일 당일권(일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_5e1ee87b7cd04c39b8aa8130c1c186e7']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 29484:

                    if ticket_name in ["평일 당일권(기계식, 월)", "평일 당일권(기계식, 화)", "평일 당일권(기계식, 수)", "평일 당일권(기계식, 목)", "평일 당일권(기계식, 금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8ae3dbf7460a4308b811e935a4d44c6d']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(자주식, 토)", "휴일 당일권(자주식, 일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8ae3dbf7460a4308b811e935a4d44c6d']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19740:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_ab59bd7bac674e0493f17f57091ed38b']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_b3d121a62e104b709553257147f25fc5']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_4998b6beaec648459519af1cdafbdadd']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f8bf7b5661ba40a49c2e36eb793ef000']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_3709bd78737c4c17b7e7fe09c203f0cd']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 2시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_63c24962c28f48148a7344fdf41c70e0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 1시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_e8cdc1ae82c640d183195d1e65eb132e']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 21787:

                    if ticket_name in ["평일 야간권", "휴일 야간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_89c9b4e281e6423091e4fcb2cc695bff']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 당일권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_9532be78b4ea4a97abf745a66003231b']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19860:

                    if ticket_name in [
                        "평일 당일권(월, 지하 2층 전용)",
                        "평일 당일권(화, 지하 2층 전용)",
                        "평일 당일권(수, 지하 2층 전용)",
                        "평일 당일권(목, 지하 2층 전용)",
                        "평일 당일권(금, 지하 2층 전용)"
                    ]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c7426c51aa2a4ad9be677a9e16982832']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 오후권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_0559d0ef478f4579ae357501982461b0']",
                            btn_confirm_xpath
                        )

                    elif ticket_name in ["휴일 당일권(지하 2층 전용,토)", "휴일 당일권(지하 2층 전용,일)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_a1ebb0f9042047af8417027792d36d73']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19624:

                    if ticket_name == "주말심야권(지하 7층전용)":
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


                elif park_id == 19600:

                    if ticket_name == "평일 5시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8212307d40df414ca06822f841b66756']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_aad9b019afa34f28aacaa66dc427d118']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 3시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_38efd15337be4a4aba7ab50dcd91fcfe']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "휴일 12시간권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_434c72e2495a40c399528947955f6208']",
                            btn_confirm_xpath
                        )

                    elif ticket_name == "평일 심야권":
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_c1720255eed748c597fd9de6c5e9caf9']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19490:

                    if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_8fea89d3864f4279b63493d518c31483']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)



                elif park_id == 19181:

                    if ticket_name in ["평일 당일권(자주식,월)", "평일 당일권(자주식,화)", "평일 당일권(자주식,수)", "평일 당일권(자주식,목)", "평일 당일권(자주식,금)"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_f00260b72c8747d08a0b50084db40ec5']",
                            btn_confirm_xpath
                        )

                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19558:
                    if ticket_name in ["휴일 당일권(토)", "휴일 당일권(일,공휴일)", "평일 10시간권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_7c2daff56df043fe9b8e9810d2201d85']",
                            btn_confirm_xpath
                        )


                    else:
                        return handle_invalid_ticket(driver)


                elif park_id == 19231:
                    if ticket_name in ["평일 심야권", "휴일 심야권"]:
                        return select_discount_and_confirm(
                            driver,
                            "//*[@id='discountItemsDataRadio_51f51cc7415a412393f704bf6cb83b76']",
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

