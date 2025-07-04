# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoAlertPresentException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import Util
import Colors
from park import ParkUtil, ParkType, Parks
import WebInfo

mapIdToWebInfo = {

    # KDB생명(연박권 따로빼기)
    45655: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9549');",  # 1일권
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9549');",  #
            "javascript:fnDisCount('75:전액무료(웹) / 잔여수량 9956');",  # 전액 무료
            "",
            "javascript:fnDisCount('79:전액무료(웹) / 잔여수량 9956');","javascript:fnDisCount('80:전액무료(웹) / 잔여수량 9956');"],

    # 카카오 T 강동홈플러스
    19243: ["login_id", "login_pw",
            "//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9549');",  # 1일권
            "javascript:fnDisCount('75:24시간유료(웹) / 잔여수량 9549');",  #
            "javascript:fnDisCount('75:전액무료(웹) / 잔여수량 9956');",  # 전액 무료
            "",
            "javascript:fnDisCount('79:전액무료(웹) / 잔여수량 9956');","javascript:fnDisCount('80:전액무료(웹) / 잔여수량 9956');"],

    # 중앙로공영주차장
    19237: ["login_id", "login_pw", "//*[@id='bodyCSS']/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",
            "javascript:fnDisCount('56:전액무료(웹)', '1');", # 평일1일권
            "javascript:fnDisCount('56:전액무료(웹)', '1');", # 주말1일권
            "javascript:fnDisCount('56:전액무료(웹)', '1');", # 심야권
            ],

    #한국경제신문
    19450: ["login_id", "login_pw",
            "//*[@id='third']/div/div/div/div[5]/div/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('54:24시간 유료(웹) / 잔여수량 999978');",  # 1일권
            "javascript:fnDisCount('54:24시간 유료(웹) / 잔여수량 999978');",
            "javascript:fnDisCount('54:24시간 유료(웹) / 잔여수량 999978');",
            ""],

    #판교아이스퀘어C1
    19493: ["login_id", "login_pw",
            #"//*[@id='bodyCSS']/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/form/center/button[1]",
            "//*[@id='third']/div/div/div/div[5]/div/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",  # 1일권
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",
            ""],
    # 판교아이스퀘어C2
    19494: ["login_id", "login_pw",
            "//*[@id='third']/div/div/div/div[5]/div/input",
            "searchCarNo", "//*[@id='btnSearch']",
            "",  # 차량번호 클릭
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",  # 1일권
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",
            "javascript:fnDisCount('55:24시간무료(웹) / 잔여수량 9999', '1');",
            ""],

}

def get_har_in_script(park_id, ticket_name):

    if park_id == 45655: #KDB 연박
        if str(ticket_name).endswith("평일1일권"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]
        elif str(ticket_name).endswith("연박권(2일)"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn4]
        elif str(ticket_name).endswith("연박권(3일)"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn5]
        elif str(ticket_name).endswith("주말1일권"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]
        elif str(ticket_name).endswith("평일심야권"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn3]

    else:
        if str(ticket_name).endswith("심야권"):
            return mapIdToWebInfo[park_id][WebInfo.night]
        elif str(ticket_name).endswith("주말3시간권"):
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn3]
        elif Util.get_week_or_weekend() == 0:
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]  #평일
        else:
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]  #주말


def log_out_web(driver):
    Util.sleep(1)

    element = driver.find_element_by_xpath("//a[contains(@href, 'doLogout')]")
    driver.execute_script("arguments[0].click();",element)
    print(Colors.BLUE + "로그아웃" + Colors.ENDC)

    driver.implicitly_wait(3)
    Util.sleep(3)


import re

def click_matching_car_number(driver, ori_car_num, search_id=None):
    try:
        car_rows = driver.find_elements(By.CSS_SELECTOR, "#divAjaxCarList > tbody > tr")
        print(f"DEBUG: 검색된 차량 개수 = {len(car_rows)}")

        for row in car_rows:
            try:
                font_tag = row.find_element(By.CSS_SELECTOR, "a font")
                car_number = font_tag.text.strip()
                print(f"DEBUG: 검색된 차량번호 = {car_number}")

                # 특수문자 제거
                clean_car_number = re.sub(r'[^가-힣0-9]', '', car_number)
                clean_ori_number = re.sub(r'[^가-힣0-9]', '', ori_car_num)

                # ✅ 차량번호 끝 6자리가 아니라 전체 자리에서 '87조5953' 같은 조합 포함되면 선택
                if clean_ori_number[-6:] in clean_car_number:
                    print(Colors.BLUE + f"✅ 클릭 대상 차량번호 발견: {car_number}" + Colors.ENDC)
                    car_link = row.find_element(By.TAG_NAME, "a")
                    onclick_script = car_link.get_attribute("onclick")
                    if onclick_script:
                        driver.execute_script(onclick_script)
                        print(Colors.BLUE + "🚗 차량 선택 스크립트 실행 완료!" + Colors.ENDC)
                        return True
            except Exception as e:
                print(f"DEBUG: 차량번호 파싱 오류 - {e}")

        print(Colors.RED + "❌ 일치하는 차량번호를 찾을 수 없음." + Colors.ENDC)
        return False
    except Exception as e:
        print(Colors.RED + f"❌ 차량번호 선택 중 예외 발생: {e}" + Colors.ENDC)
        return False


def apply_discount_button(driver):
    """
    🎟 "24시간무료(웹)" 할인 버튼을 찾아 클릭
    """
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "#divAjaxFreeDiscount button")

        for button in buttons:
            if "24시간무료(웹)" in button.text:
                print(Colors.BLUE + "✅ 24시간무료(웹) 할인 버튼 클릭!" + Colors.ENDC)
                driver.execute_script("arguments[0].click();", button)
                return True

        print(Colors.RED + "❌ '24시간무료(웹)' 할인 버튼을 찾을 수 없음!" + Colors.ENDC)
        return False

    except Exception as e:
        print(Colors.RED + f"❌ 할인 버튼 클릭 중 오류 발생: {e}" + Colors.ENDC)
        return False


def web_har_in(target, driver):
    import re

    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]
    park_type = ParkType.get_park_type(park_id)

    trim_car_num = Util.all_trim(ori_car_num)
    search_id = trim_car_num[-4:]

    print("parkId = " + str(park_id) + ", " + "searchId = " + search_id)
    print(Colors.BLUE + ticket_name + Colors.ENDC)

    if str(ticket_name).endswith("연박권"):
        print("GS 연박권")
        return False

    if ParkUtil.is_park_in(park_id):
        if park_id in mapIdToWebInfo:
            login_url = ParkUtil.get_park_url(park_id)
            driver.implicitly_wait(3)
            driver.get(login_url)

            web_info = mapIdToWebInfo[park_id]
            web_har_in_info = ParkUtil.get_park_lot_option(park_id)

            # 로그인
            driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
            driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])
            driver.implicitly_wait(3)
            driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()
            driver.implicitly_wait(3)

            # 차량번호 검색
            driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
            Util.sleep(3)

            try:
                driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()
            except NoSuchElementException:
                log_out_web(driver)
                return False

            Util.sleep(3)

            if ParkUtil.check_search(park_id, driver):
                # ✅ 차량번호 클릭 처리 (전체 번호 매칭)
                car_rows = driver.find_elements(By.CSS_SELECTOR, "#divAjaxCarList > tbody > tr")
                matched = False
                for row in car_rows:
                    try:
                        font_tag = row.find_element(By.CSS_SELECTOR, "a font")
                        car_number = font_tag.text.strip()
                        print(f"DEBUG: 검색된 차량번호 = {car_number}")

                        clean_car_number = re.sub(r'[^가-힣0-9]', '', car_number)
                        clean_ori_number = re.sub(r'[^가-힣0-9]', '', ori_car_num)

                        if clean_ori_number[-6:] in clean_car_number:
                            print(Colors.BLUE + f"✅ 클릭 대상 차량번호 발견: {car_number}" + Colors.ENDC)
                            car_link = row.find_element(By.TAG_NAME, "a")
                            onclick_script = car_link.get_attribute("onclick")
                            if onclick_script:
                                driver.execute_script(onclick_script)
                                print(Colors.BLUE + "🚗 차량 선택 스크립트 실행 완료!" + Colors.ENDC)
                                matched = True
                                break
                    except Exception as e:
                        print(f"DEBUG: 차량번호 파싱 오류 - {e}")

                if not matched:
                    print("❌ 차량 클릭 실패, 로그아웃 후 종료")
                    log_out_web(driver)
                    return False

                Util.sleep(3)

                # ✅ 할인권 적용
                if park_id == 19243 and ticket_name in ["평일1일권", "주말1일권"]:
                    try:
                        discount_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//*[@id='divAjaxFreeDiscount']/input"))
                        )
                        discount_button.click()
                        print(Colors.BLUE + "✅ 24시간무료(웹) 할인 적용 완료 (강동홈플러스)." + Colors.ENDC)
                    except TimeoutException:
                        print(Colors.RED + "❌ 24시간무료(웹) 버튼을 찾을 수 없음 (강동홈플러스)." + Colors.ENDC)
                        log_out_web(driver)
                        return False

                # ✅ 할인권 적용
                if park_id in [19493, 19494]:
                    try:
                        discount_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, "//button[contains(text(), '24시간무료(웹)')]")
                            )
                        )
                        discount_button.click()
                        print(Colors.BLUE + "✅ 24시간무료(웹) 할인 적용 완료." + Colors.ENDC)
                    except TimeoutException:
                        print(Colors.RED + "❌ 24시간무료(웹) 버튼을 찾을 수 없음." + Colors.ENDC)
                        log_out_web(driver)
                        return False
                else:
                    harin_script = get_har_in_script(park_id, ticket_name)
                    driver.execute_script(harin_script)

                Util.sleep(1)
                try:
                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                    driver.switch_to.alert.accept()
                    print("✅ 할인 적용 완료")
                except TimeoutException:
                    print("⚠️ 할인 적용 알림 없음")

                log_out_web(driver)
                Util.sleep(3)
                return True

            else:
                print("❌ 차량 검색 결과 없음 또는 실패")
                log_out_web(driver)
                return False

        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False


