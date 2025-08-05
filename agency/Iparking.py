# -*- coding: utf-8 -*-
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

import Util
import Colors
from park import ParkUtil, ParkType, Parks
import WebInfo
import re
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

mapIdToWebInfo = {

    # KT 구로지밸리
   19425: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],

    # 서초 꽃마을
    19433: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    # 예전빌딩
    19448: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],

    #동양프라자
    19459: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    #다산법조메디컬타워
    19461: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    #화광빌딩
    19462: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],

    # 이마트TR송림점
    19476: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
     # 이마트풍산점
     19508: ["id", "password", "//*[@id='login']",
             "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
             "#carList > tr",
             "2"
             ],
    # 하이파킹 성수무신사캠퍼스N1
    19921: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    # 하이파킹 종로5가역하이뷰더광장
    29220: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
    # 하이파킹 SK-C타워(구, 충무로15빌딩)
    29175: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],

    # 신한은행 광교 주차장
    19945: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],

    # 카카오 T 이마트구로점
    19579: ["id", "password", "//*[@id='login']",
            "carNumber", "//*[@id='container']/section[2]/div[2]/div/button",
            "#carList > tr",
            "2"
            ],
}

i_parking_hi_parking = [
    #Parks.YEOUIDO_NH_CAPITAL
]


def get_har_in_script(park_id, ticket_name):
    # todo 요일 구분이 필요없는 현장
    if Util.get_week_or_weekend() == 0:
        return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]
    else:
        return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]

def handle_popup_ok(driver):
    """
    로그인 전 '다시 보지 않기' 팝업 닫기
    """
    try:
        popup_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "popupOk")))
        popup_button.click()
        print(Colors.YELLOW + "[팝업] 다시 보지 않기 클릭 완료." + Colors.ENDC)
        Util.sleep(1)
    except TimeoutException:
        print(Colors.YELLOW + "[팝업] 다시 보지 않기 없음." + Colors.ENDC)



def handle_after_login_popup(driver):
    """
    로그인 후 '다시 보지 않기' 팝업 처리 (체크 후 닫기)
    """
    try:
        # [확실한 대기] 체크박스가 보이고 클릭 가능할 때까지 대기
        checkbox = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "chkRemove2"))
        )
        if not checkbox.is_selected():
            checkbox.click()
            print(Colors.YELLOW + "[팝업] 다시 보지 않기 체크 완료." + Colors.ENDC)
        else:
            print(Colors.YELLOW + "[팝업] 이미 체크됨." + Colors.ENDC)

        # [확실한 대기] 닫기 버튼 보이고 클릭 가능할 때까지 대기
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "gohome"))
        )
        close_button.click()
        print(Colors.YELLOW + "[팝업] 닫기 완료." + Colors.ENDC)
        Util.sleep(1)

    except TimeoutException:
        print(Colors.YELLOW + "[팝업] 로그인 후 팝업 없음." + Colors.ENDC)
    except Exception as ex:
        print(Colors.RED + f"[팝업] 처리 중 예외 발생: {ex}" + Colors.ENDC)


def close_info_and_tutorial(driver):
    """
    튜토리얼과 인포 레이어 닫기
    """
    try:
        # 튜토리얼 레이어가 보이면 닫기
        tutorial_layer = driver.find_element(By.ID, "tutorial")
        if tutorial_layer.is_displayed():
            print(Colors.YELLOW + "[팝업] 튜토리얼 레이어 감지, 닫기 시도." + Colors.ENDC)
            close_button = tutorial_layer.find_element(By.ID, "start")
            close_button.click()
            Util.sleep(1)
        else:
            print(Colors.YELLOW + "[팝업] 튜토리얼 레이어 없음." + Colors.ENDC)
    except Exception as ex:
        print(Colors.YELLOW + f"[팝업] 튜토리얼 닫기 예외: {ex}" + Colors.ENDC)

    try:
        # 인포 레이어가 보이면 닫기
        info_layer = driver.find_element(By.ID, "information")
        if info_layer.is_displayed():
            print(Colors.YELLOW + "[팝업] 인포 레이어 감지, 닫기 시도." + Colors.ENDC)
            checkbox = info_layer.find_element(By.ID, "chkRemove2")
            if not checkbox.is_selected():
                checkbox.click()
                print(Colors.YELLOW + "[팝업] 인포 레이어 다시 보지 않기 체크 완료." + Colors.ENDC)
            close_button = info_layer.find_element(By.ID, "gohome")
            close_button.click()
            Util.sleep(1)
        else:
            print(Colors.YELLOW + "[팝업] 인포 레이어 없음." + Colors.ENDC)
    except Exception as ex:
        print(Colors.YELLOW + f"[팝업] 인포 레이어 닫기 예외: {ex}" + Colors.ENDC)



def close_info_and_tutorial(driver):
    """
    튜토리얼과 인포 레이어 강제 닫기 (순서 보장, 강제 스크립트 포함)
    """

    # 1. 튜토리얼 레이어 닫기
    try:
        tutorial_layer = driver.find_element(By.ID, "tutorial")
        if tutorial_layer.is_displayed():
            print(Colors.YELLOW + "[팝업] 튜토리얼 레이어 감지, 닫기 시도." + Colors.ENDC)
            close_button = tutorial_layer.find_element(By.ID, "start")
            driver.execute_script("arguments[0].click();", close_button)  # 강제 클릭
            Util.sleep(1)
        else:
            print(Colors.YELLOW + "[팝업] 튜토리얼 레이어 없음." + Colors.ENDC)
    except Exception as ex:
        print(Colors.YELLOW + f"[팝업] 튜토리얼 닫기 예외: {ex}" + Colors.ENDC)

    # 2. 인포 레이어 닫기
    try:
        info_layer = driver.find_element(By.ID, "information")
        if info_layer.is_displayed():
            print(Colors.YELLOW + "[팝업] 인포 레이어 감지, 닫기 시도." + Colors.ENDC)
            checkbox = info_layer.find_element(By.ID, "chkRemove2")
            if not checkbox.is_selected():
                driver.execute_script("arguments[0].click();", checkbox)  # 강제 클릭
                print(Colors.YELLOW + "[팝업] 인포 다시 보지 않기 체크 완료." + Colors.ENDC)
            close_button = info_layer.find_element(By.ID, "gohome")
            driver.execute_script("arguments[0].click();", close_button)  # 강제 클릭
            Util.sleep(1)
        else:
            print(Colors.YELLOW + "[팝업] 인포 레이어 없음." + Colors.ENDC)
    except Exception as ex:
        print(Colors.YELLOW + f"[팝업] 인포 레이어 닫기 예외: {ex}" + Colors.ENDC)

    # 3. 슬라이더(li 태그) 가림
    try:
        slider_list = driver.find_elements(By.CSS_SELECTOR, "li.img-screen")
        for li in slider_list:
            driver.execute_script("arguments[0].style.display='none';", li)  # 강제 숨김
        print(Colors.YELLOW + "[팝업] 슬라이더 레이어 숨김 완료." + Colors.ENDC)
    except Exception as ex:
        print(Colors.YELLOW + f"[팝업] 슬라이더 숨기기 예외: {ex}" + Colors.ENDC)


def handle_discount(driver, park_id, ticket_name):
    """
    19945 (신한은행 광교) 전용 할인 처리 - 클릭 후 등록 성공까지 검증하는 버전
    """
    if park_id == 19945:
        print(Colors.YELLOW + "[19945] 신한은행 광교 할인 처리 시작" + Colors.ENDC)

        try:
            product_list = driver.find_elements(By.CSS_SELECTOR, "#productList > tr")
            found = False

            normalized_ticket_name = ticket_name.replace(" ", "")  # 공백 제거

            for row in product_list:
                try:
                    label = row.find_element(By.TAG_NAME, "td").text.strip()
                    apply_button = row.find_element(By.CSS_SELECTOR, "button.btn-apply")

                    if not apply_button.is_enabled():
                        print(Colors.YELLOW + f"⚠️ 비활성화 버튼: {label}" + Colors.ENDC)
                        continue

                    # (1) 할인권 매칭
                    if normalized_ticket_name == "주말당일권" and "휴일 당일권" in label:
                        driver.execute_script("arguments[0].click();", apply_button)
                        found = True
                        break
                    elif normalized_ticket_name == "주말3시간권" and "휴일 3시간권" in label:
                        driver.execute_script("arguments[0].click();", apply_button)
                        found = True
                        break
                    elif normalized_ticket_name == "토일연박권" and "토,일 연박권" in label:
                        driver.execute_script("arguments[0].click();", apply_button)
                        found = True
                        break

                except Exception as ex:
                    print(Colors.RED + f"❌ 할인 버튼 클릭 중 오류: {ex}" + Colors.ENDC)

            if not found:
                print(Colors.YELLOW + f"⚠️ '{ticket_name}'에 해당하는 할인권 버튼을 찾지 못했습니다." + Colors.ENDC)
                return False

            # (2) 클릭 후 등록 성공 여부 검증
            Util.sleep(2)  # 클릭 후 반영 대기

            try:
                apply_list = driver.find_elements(By.CSS_SELECTOR, "#applyList > tr")
                registered = False

                for row in apply_list:
                    text = row.text
                    if normalized_ticket_name == "주말당일권" and "휴일 당일권" in text:
                        registered = True
                        break
                    elif normalized_ticket_name == "주말3시간권" and "휴일 3시간권" in text:
                        registered = True
                        break
                    elif normalized_ticket_name == "토일연박권" and "토,일 연박권" in text:
                        registered = True
                        break

                if registered:
                    print(Colors.BLUE + "✅ 할인권 등록 완료 확인됨." + Colors.ENDC)
                    return True
                else:
                    print(Colors.RED + "❌ 할인 클릭은 했지만 등록 완료되지 않음." + Colors.ENDC)
                    return False

            except Exception as ex:
                print(Colors.RED + f"❌ 할인 등록 확인 중 오류: {ex}" + Colors.ENDC)
                return False

        except Exception as e:
            print(Colors.RED + f"❌ 할인 처리 중 전체 오류 발생: {e}" + Colors.ENDC)
            return False

    return None  # park_id가 19945가 아니면 처리하지 않음


def web_har_in(target, driver):
    pid, park_id, ori_car_num, ticket_name, *_ = target  # 4개 받고 나머지는 무시
    park_id = int(Util.all_trim(park_id))
    ori_car_num = Util.all_trim(ori_car_num)
    trim_car_num = Util.all_trim(ori_car_num)
    search_id = trim_car_num[-4:]
    print(f"parkId = {park_id}, searchId = {search_id}")
    print(Colors.BLUE + ticket_name + Colors.ENDC)

    # 웹할인 불가능한 주차장 체크
    if not ParkUtil.is_park_in(park_id):
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False

    # 자동화 정보 없는 주차장 체크
    if park_id not in mapIdToWebInfo:
        print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
        return False

    login_url = ParkUtil.get_park_url(park_id)
    driver.get(login_url)
    Util.sleep(2)
    driver.implicitly_wait(3)

    # [✅ 추가] Skip 버튼 처리
    try:
        skip_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, "skip"))
        )
        skip_button.click()
        print(Colors.YELLOW + "[팝업] Skip 클릭 완료." + Colors.ENDC)
        Util.sleep(1)
    except TimeoutException:
        print(Colors.YELLOW + "[팝업] Skip 버튼 없음." + Colors.ENDC)

    # 로그인 전 팝업 처리
    handle_popup_ok(driver)

    # 로그인 수행
    web_info = mapIdToWebInfo[park_id]
    web_har_in_info = ParkUtil.get_park_lot_option(park_id)

    if ParkUtil.first_access(park_id, driver.current_url):
        driver.find_element(By.ID, web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
        driver.find_element(By.ID, web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])
        driver.find_element(By.XPATH, web_info[WebInfo.btnLogin]).click()
        Util.sleep(2)

        # 로그인 후 팝업 처리
        handle_after_login_popup(driver)

        close_info_and_tutorial(driver)  # 추가된 부분 (팝업 닫기)


    # 차량 검색
    driver.find_element(By.ID, web_info[WebInfo.inputSearch]).send_keys(search_id)
    Util.sleep(3)
    driver.find_element(By.XPATH, web_info[WebInfo.btnSearch]).click()
    Util.sleep(1)


    # 검색 결과 확인
    tr_text = driver.find_element(By.CSS_SELECTOR, "#notChooseCar > p:nth-child(1)").text
    if tr_text.strip().endswith("에 대한 검색 결과가 없습니다."):
        print(Colors.YELLOW + "검색 결과 없음." + Colors.ENDC)
        return False

    # 차량 검색 후 리스트에서 차량번호 가져오기
    try:
        car_rows = driver.find_elements(By.CSS_SELECTOR, "#carList > tr")

        found = False  # 차량을 찾았는지 여부 확인

        for row in car_rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) > 1:
                detected_car_num = columns[1].text.strip()  # 차량번호 추출

                print(f"[디버그] 검색된 차량번호: {detected_car_num}")  # 로그 확인

                if detected_car_num == ori_car_num:  # 검색한 차량번호와 일치하는지 확인
                    print(Colors.BLUE + f"✅ 차량번호 일치: {detected_car_num}" + Colors.ENDC)

                    # 해당 차량의 라디오 버튼 선택
                    radio_button = row.find_element(By.NAME, "radioGroup")
                    driver.execute_script("arguments[0].click();", radio_button)  # 강제 클릭
                    print(Colors.BLUE + "✅ 차량 선택 완료." + Colors.ENDC)

                    # 차량 선택 버튼 활성화 후 클릭
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "next"))
                    )
                    driver.execute_script("arguments[0].click();", next_button)  # 강제 클릭
                    print(Colors.BLUE + "✅ 차량 선택 버튼 클릭 완료." + Colors.ENDC)

                    found = True  # 차량을 찾았음을 표시
                    break  # 차량을 찾았으면 루프 종료

        if not found:
            print(Colors.RED + "❌ 차량번호가 검색된 리스트에 없음." + Colors.ENDC)
            return False

    except TimeoutException:
        print(Colors.RED + "❌ 차량 선택 또는 버튼 클릭 실패!" + Colors.ENDC)
        return False
    except Exception as ex:
        print(Colors.RED + f"❌ 차량 선택 중 오류 발생: {ex}" + Colors.ENDC)
        return False

    # 할인 처리
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "next"))).click()
        Util.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # ✅ 분당 예외 처리
        if park_id == 19446:
            print(Colors.YELLOW + "분당" + Colors.ENDC)
            driver.find_element(By.XPATH, "//*[@id='productList']/tr[3]/td[3]/button").click()

        # ✅ 하이파킹 종로5가역하이뷰더광장 예외 처리
        elif park_id == 29220:
            product_list = driver.find_elements(By.CSS_SELECTOR, "#productList > tr")
            found = False

            for row in product_list:
                try:
                    label = row.find_element(By.TAG_NAME, "td").text.strip()
                    apply_button = row.find_element(By.CSS_SELECTOR, "button.btn-apply")

                    if ticket_name in ["평일 당일권(기계식)", "휴일 당일권(기계식)"] and "기계식종일권(공유서비스)" in label:
                        driver.execute_script("arguments[0].click();", apply_button)
                        print(Colors.BLUE + "✅ 기계식종일권(공유서비스) 할인 적용 완료." + Colors.ENDC)
                        found = True
                        break

                    elif ticket_name == "평일 3시간권(기계식)" and "기계식3시간권공유서비스" in label:
                        driver.execute_script("arguments[0].click();", apply_button)
                        print(Colors.BLUE + "✅ 기계식3시간권공유서비스 할인 적용 완료." + Colors.ENDC)
                        found = True
                        break

                except Exception as ex:
                    print(Colors.RED + f"❌ 할인 버튼 처리 중 오류: {ex}" + Colors.ENDC)

            if not found:
                print(Colors.YELLOW + f"⚠️ '{ticket_name}'에 해당하는 할인권을 찾지 못했습니다." + Colors.ENDC)
                return False

        elif park_id == 29175:
            print(Colors.YELLOW + "하이파킹 SK-C타워 할인 처리" + Colors.ENDC)
            product_list = driver.find_elements(By.CSS_SELECTOR, "#productList > tr")
            found = False

            normalized_ticket_name = ticket_name.replace(" ", "")  # 공백 제거

            for row in product_list:
                try:
                    label = row.find_element(By.TAG_NAME, "td").text.strip()
                    apply_button = row.find_element(By.CSS_SELECTOR, "button.btn-apply")

                    if normalized_ticket_name in ["평일당일권", "휴일당일권"] and ("종일권" in label or "주말권" in label):
                        driver.execute_script("arguments[0].click();", apply_button)
                        print(Colors.BLUE + "✅ 종일권 할인 적용 완료." + Colors.ENDC)
                        found = True
                        break

                    elif normalized_ticket_name == "평일6시간권" and "평일6시간권(공유서비스)" in label:
                        driver.execute_script("arguments[0].click();", apply_button)
                        print(Colors.BLUE + "✅ 평일6시간권(공유서비스) 할인 적용 완료." + Colors.ENDC)
                        found = True
                        break

                except Exception as ex:
                    print(Colors.RED + f"❌ 할인 버튼 처리 중 오류: {ex}" + Colors.ENDC)

            if not found:
                print(Colors.YELLOW + f"⚠️ '{ticket_name}'에 해당하는 할인권을 찾지 못했습니다." + Colors.ENDC)
                return False


        elif park_id == 19945:
            result = handle_discount(driver, park_id, ticket_name)
            return result if result is not None else False



        # ✅ 성수무신사 N1 예외 처리 (24시간 무료)
        elif park_id == 19921:
            if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)", "휴일 당일권"]:
                print(Colors.YELLOW + "성수무신사 N1 - 24시간 무료권 처리" + Colors.ENDC)
                product_list = driver.find_elements(By.CSS_SELECTOR, "#productList > tr")
                found = False
                for row in product_list:
                    try:
                        cell_text = row.find_element(By.TAG_NAME, "td").text.strip()
                        if "24시간무료" in cell_text:
                            apply_button = row.find_element(By.CSS_SELECTOR, "button.btn-apply")
                            if apply_button.is_enabled():
                                driver.execute_script("arguments[0].click();", apply_button)
                                print(Colors.BLUE + "✅ 24시간무료 할인 적용 완료." + Colors.ENDC)
                                found = True
                                break
                    except Exception as ex:
                        print(Colors.RED + f"❌ 할인 버튼 찾기 중 오류: {ex}" + Colors.ENDC)

                if not found:
                    print(Colors.YELLOW + "⚠️ 24시간무료 할인권을 찾지 못했습니다." + Colors.ENDC)
            else:
                print(Colors.RED + f"❌ 성수무신사 N1 - 허용되지 않은 티켓({ticket_name})으로 할인 불가!" + Colors.ENDC)
                return False  # ✅ 티켓 조건이 맞지 않으면 중단

        # ✅ 카카오 T 이마트구로점 예외 처리 (일일권(24시간) 적용)
        elif park_id == 19579:
            if ticket_name in ['평일1일권', '주말1일권']:
                print(Colors.YELLOW + "카카오 T 이마트구로점 - 일일권(24시간) 할인권 처리" + Colors.ENDC)
                product_list = driver.find_elements(By.CSS_SELECTOR, "#productList > tr")
                found = False
                for row in product_list:
                    try:
                        cell_text = row.find_element(By.TAG_NAME, "td").text.strip()
                        if "일일권(24시간)" in cell_text:
                            apply_button = row.find_element(By.CSS_SELECTOR, "button.btn-apply")
                            if apply_button.is_enabled():
                                driver.execute_script("arguments[0].click();", apply_button)
                                print(Colors.BLUE + "✅ 일일권(24시간) 할인 적용 완료." + Colors.ENDC)
                                found = True
                                break
                    except Exception as ex:
                        print(Colors.RED + f"❌ 할인 버튼 찾기 중 오류: {ex}" + Colors.ENDC)

                if not found:
                    print(Colors.YELLOW + "⚠️ 일일권(24시간) 할인권을 찾지 못했습니다." + Colors.ENDC)
                    return False  # 할인권이 없으면 중단
            else:
                print(Colors.RED + f"❌ 카카오 T 이마트구로점 - 허용되지 않은 티켓({ticket_name})으로 할인 불가!" + Colors.ENDC)
                return False


        # ✅ KT 구로지밸리 예외 처리 (24시간 적용)
        elif park_id == 19425 and ticket_name in ['평일1일권', '주말1일권']:
            print(Colors.YELLOW + "KT 구로지밸리 - 24시간 할인권 처리" + Colors.ENDC)
            product_list = driver.find_elements(By.CSS_SELECTOR, "#productList > tr")
            found = False

            for row in product_list:
                try:
                    cell_text = row.find_element(By.TAG_NAME, "td").text.strip()
                    if "24시간" in cell_text:  # "24시간" 포함된 행 찾기
                        apply_button = row.find_element(By.CSS_SELECTOR, "button.btn-apply")
                        if apply_button.is_enabled():
                            driver.execute_script("arguments[0].click();", apply_button)
                            print(Colors.BLUE + "✅ 24시간 할인 적용 완료." + Colors.ENDC)
                            found = True
                            break
                except Exception as ex:
                    print(Colors.RED + f"❌ 할인 버튼 찾기 중 오류: {ex}" + Colors.ENDC)

            if not found:
                print(Colors.YELLOW + "⚠️ 24시간 할인권을 찾지 못했습니다." + Colors.ENDC)
                return False  # ✅ 할인 실패 시 중단


        # 기본 할인 적용 (기존 코드)
        else:
            try:
                discount_button = driver.find_element(By.CSS_SELECTOR, "#productList > tr > td:nth-child(3) > button")
                driver.execute_script("arguments[0].click();", discount_button)
            except Exception as ex:
                print(Colors.RED + f"❌ 기본 할인 버튼 클릭 중 오류 발생: {ex}" + Colors.ENDC)
                return False  # ✅ 할인 버튼 클릭 실패 시 중단

        Util.sleep(2)
        driver.find_element(By.ID, "popupOk").click()
        print(Colors.BLUE + "할인 완료" + Colors.ENDC)
        return True

    except Exception as ex:
        print("[할인 처리 중 에러]", ex)
        return False
