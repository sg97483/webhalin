# -*- coding: utf-8 -*-
from selenium.webdriver import ActionChains
from selenium.webdriver.common import alert
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import Util
import Colors
from park import ParkUtil, ParkType
import WebInfo
import pymysql
from agency.park_mappings import PARK_DISCOUNT_MAPPINGS


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
side_nav_xpath = "//a[@data-ui='sideNavButtonLogout']"
#side_nav_xpath = "//*[@id='side-nav']/div/div/div[3]/div[3]/div/a"
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
        park_str = str(park_id)
        if park_str in PARK_DISCOUNT_MAPPINGS:
            mapping = PARK_DISCOUNT_MAPPINGS[park_str]
            if ticket_name in mapping:
                return select_discount_and_confirm(
                    driver,
                    mapping[ticket_name],
                    btn_confirm_xpath
                )
            else:
                return handle_invalid_ticket(driver)
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

            print(Colors.BLUE + f"DEBUG: current_url = {driver.current_url}" + Colors.ENDC)
            first_access_result = ParkUtil.first_access(park_id, driver.current_url)
            print(Colors.BLUE + f"DEBUG: first_access_result = {first_access_result}" + Colors.ENDC)
            
            if not first_access_result:
                try:
                    driver.implicitly_wait(1)
                    if len(driver.find_elements(By.ID, "username")) > 0:
                        print(Colors.BLUE + "DEBUG: 화면에 username 필드가 감지되어 로그인 과정을 강제 활성화합니다." + Colors.ENDC)
                        first_access_result = True
                except:
                    pass
                driver.implicitly_wait(3)

            if first_access_result:
                try:
                    wait = WebDriverWait(driver, 10)
                    
                    # ID 입력 필드 대기 및 입력
                    print("DEBUG: username 필드 대기 중...")
                    username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
                    print("DEBUG: username 필드 찾음, 입력 중...")
                    username_field.send_keys(web_har_in_info[WebInfo.webHarInId])
                    
                    # PW 입력 필드 대기 및 입력
                    print("DEBUG: password 필드 대기 중...")
                    password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
                    print("DEBUG: password 필드 찾음, 입력 중...")
                    password_field.send_keys(web_har_in_info[WebInfo.webHarInPw])
                    
                    # 로그인 버튼 클릭
                    print("DEBUG: 로그인 버튼 대기 중...")
                    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, web_info[WebInfo.btnLogin])))
                    print("DEBUG: 로그인 버튼 클릭 중...")
                    login_btn.click()
                    
                    driver.implicitly_wait(3)
                    
                    # 차량번호 입력 필드 대기 및 입력
                    print("DEBUG: 차량번호 입력 필드 대기 중...")
                    search_field = wait.until(EC.presence_of_element_located((By.ID, web_info[WebInfo.inputSearch])))
                    print("DEBUG: 차량번호 입력 필드 찾음, 입력 중...")
                    search_field.send_keys(search_id)
                    Util.sleep(3)
                    
                    # 검색 버튼 클릭
                    print("DEBUG: 검색 버튼 대기 중...")
                    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, web_info[WebInfo.btnSearch])))
                    print("DEBUG: 검색 버튼 클릭 중...")
                    search_btn.click()
                    
                    Util.sleep(3)
                    print("DEBUG: 로그인 및 차량 검색 완료")
                except UnexpectedAlertPresentException as alert_ex:
                    alert_text = alert_ex.alert_text if hasattr(alert_ex, 'alert_text') and alert_ex.alert_text else str(alert_ex)
                    print(Colors.RED + f"❌ 로그인 중 알림창 감지 (ID/PW 불일치 등): {alert_text}" + Colors.ENDC)
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()
                    except:
                        pass
                    return False
                except Exception as login_ex:
                    print(Colors.RED + f"❌ 로그인 또는 검색 과정 중 오류 발생: {login_ex}" + Colors.ENDC)
                    return False

                # ======================================================================
                # 💡 여기부터 새로운 검증 코드 추가
                # ======================================================================
                try:
                    # 1. 화면에 표시된 차량 번호 요소가 나타날 때까지 최대 5초 대기
                    wait = WebDriverWait(driver, 5)
                    wait.until(EC.visibility_of_element_located((By.XPATH, car_num_xpath)))
                    car_num_elements = driver.find_elements(By.XPATH, car_num_xpath)

                    is_matched = False
                    for element in car_num_elements:
                        displayed_car_num = Util.all_trim(element.text)
                        if displayed_car_num[-7:] == ori_car_num[-7:]:
                            is_matched = True
                            print(Colors.GREEN + f"✅ 차량번호 일치 확인: {displayed_car_num}" + Colors.ENDC)
                            break

                    if not is_matched:
                        # ❌ 일치하는 번호가 없으면 로그 남기고 실패 처리 후 로그아웃
                        displayed_nums = [Util.all_trim(el.text) for el in car_num_elements]
                        print(Colors.RED + f"❌ 차량번호 불일치. [DB: {ori_car_num}] != [화면: {', '.join(displayed_nums)}]" + Colors.ENDC)
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

                park_str = str(park_id)
                if park_str in PARK_DISCOUNT_MAPPINGS:
                    mapping = PARK_DISCOUNT_MAPPINGS[park_str]
                    if ticket_name in mapping:
                        return select_discount_and_confirm(
                            driver,
                            mapping[ticket_name],
                            btn_confirm_xpath
                        )
                    else:
                        return handle_invalid_ticket(driver)
                else:
                    try:
                        driver.implicitly_wait(3)
                        try:
                            driver.find_element("xpath", side_nav_xpath).click()
                        except:
                            driver.find_element_by_xpath(side_nav_xpath).click()
                            
                        print(Colors.BLUE + "지원하지 않는 주차장 ID: " + str(park_id) + Colors.ENDC)
                        return False
                    except Exception as ex:
                        print(f"Error during process: {ex}")
                        return False

    return False
