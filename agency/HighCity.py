# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By

import Util
import Colors
from park import ParkUtil, ParkType, Parks
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
import WebInfo

mapIdToWebInfo = {
    # HighCity 동일타워
    15313: [
        "user_id",  # ID 입력 필드 ID
        "user_pw",  # PW 입력 필드 ID
        "//*[@id='btnLogin']",  # 로그인 버튼 XPath
        "txtCarno",  # 차량번호 입력 필드 ID (← 실제는 이거임)
        "//*[@id='btnFind']",  # 차량 검색 버튼 XPath
        "",  # radio 버튼 없음
        "-",  # weekday 스크립트 사용 안함
        "-",  # weekend 스크립트 사용 안함
        "-",  # night 스크립트 사용 안함
    ],
    # 목동 예술인센터
    19517: [
        "user_id",  # ID 입력 필드 ID
        "user_pw",  # PW 입력 필드 ID
        "//*[@id='btnLogin']",  # 로그인 버튼 XPath
        "txtCarno",  # 차량번호 입력 필드 ID (← 실제는 이거임)
        "//*[@id='btnFind']",  # 차량 검색 버튼 XPath
        "",  # radio 버튼 없음
        "-",  # weekday 스크립트 사용 안함
        "-",  # weekend 스크립트 사용 안함
        "-",  # night 스크립트 사용 안함
    ],
    # 남산스퀘어
    13007: [
        "user_id",  # ID 입력 필드 ID
        "password",  # PW 입력 필드 ID
        "//input[@type='button']",  # 로그인 버튼 XPath
        "license_plate_number",  # 차량번호 입력 필드 ID
        "//input[@type='button']",  # 차량 검색 버튼 XPath
        "chk",  # ✅ 차량 선택용 radio 버튼 ID
        "-",  # 평일1일권 등 스크립트는 분기문으로 처리
        "-",  # 주말권 스크립트
        "-",  # 야간권 스크립트
    ],

    # 트윈시티남산
    16003: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('98', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('98', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('92', '1', '', '파킹박(야간)', '1', '0');"

            ],

    # EG빌딩
    19194: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('20', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('20', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('32', '1', '', 'ppark(야간)', '1', '0') ;",
            ],

    #  코리아나호텔
    19248: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('13', '1', '01|02|03|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('13', '1', '01|02|03|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('31', '1', '', 'ppark(야간)', '999999999', '0');",
            ],
    #  동산마을공영
    19276: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            ],

    #  반포동방음언덕형공영
    19273: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '05|', 'PPark', '1', '0');",
            "javascript:applyDiscount('08', '1', '05|', 'PPark', '1', '0');",
            "javascript:applyDiscount('08', '1', '05|', 'PPark', '1', '0');",
            ],
    # 그랜드센트럴
    19364: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('91', '1', '', 'ppark(야간)', '999999999', '0'); ",
            ],

    # 하이파킹 무궁화공영
    19456: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('91', '1', '', 'ppark(야간)', '999999999', '0'); ",
            ],


    # TURU 을지트윈타워 (할인 버튼을 직접 클릭하므로 스크립트는 불필요)
    19174: [
        "name_form",  # 0: ID 입력 필드
        "pwd_form",  # 1: PW 입력 필드
        "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",  # 2: 로그인 버튼
        "carNumber",  # 3: 차량번호 입력
        "/html/body/table[2]/tbody/tr[5]/td/input",  # 4: 검색 버튼
        ""  # 5: radio 버튼 없음 (할인 버튼은 ticket_name에 따라 별도 처리)
    ],


    # GS타임즈 반포2동공영
    19492: ["user_id", "user_pw", "//*[@id='btnLogin']",
            "txtCarno", "//*[@id='btnFind']",
            "",  # radio 버튼 처리 안함
            "-",  # btnItem 없음
            "-",  # weekday 스크립트 제거
            "-",  # weekend 스크립트 제거
            "-",  # night 스크립트 제거
            ],

    # 하이파킹 충무로흥국빌딩
    16159: ["name", "pwd", "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "",  # radio 버튼 처리 안함
            "-",  # btnItem 없음
            "-",  # weekday 스크립트 제거
            "-",  # weekend 스크립트 제거
            "-",  # night 스크립트 제거
            ],

    # 하이파킹 판교알파리움타워(2동)
    29218: ["name", "pwd", "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "",  # radio 버튼 처리 안함
            "-",  # btnItem 없음
            "-",  # weekday 스크립트 제거
            "-",  # weekend 스크립트 제거
            "-",  # night 스크립트 제거
            ],

    # 하이파킹 판교알파리움타워(1동)
    18996: ["name", "pwd", "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "",  # radio 버튼 처리 안함
            "-",  # btnItem 없음
            "-",  # weekday 스크립트 제거
            "-",  # weekend 스크립트 제거
            "-",  # night 스크립트 제거
            ],


    # 	DWI 마곡595빌딩 주차장
    29248: ["txtID", "txtPassword",
            "//*[@id='lbtnLogin']",
            "ContentPlaceHolder_txtVehicleNo", "//*[@id='ContentPlaceHolder_lbtnSearch']",
            "",  # radio 버튼 처리 안함
            "-",  # btnItem 없음
            "-",  # weekday 스크립트 제거
            "-",  # weekend 스크립트 제거
            "-",  # night 스크립트 제거
            ],

    # 	역삼아르누보시티
    29364: ["//div[@name='login-id']/input", "//div[@name='login-password']/input",
            "//button[contains(@class, 'login-button')]",
            "//*[@id='hho']", "//button[contains(@class, 'button-submit')]",
            "",  # radio 버튼 처리 안함
            "-",  # btnItem 없음
            "-",  # weekday 스크립트 제거
            "-",  # weekend 스크립트 제거
            "-",  # night 스크립트 제거
            ],

    # 	보타니끄논현오피스텔
    29361: ["//div[@name='login-id']/input", "//div[@name='login-password']/input",
            "//button[contains(@class, 'login-button')]",
            "//*[@id='hho']", "//button[contains(@class, 'button-submit')]",
            "",  # radio 버튼 처리 안함
            "-",  # btnItem 없음
            "-",  # weekday 스크립트 제거
            "-",  # weekend 스크립트 제거
            "-",  # night 스크립트 제거
            ],

    # 	서초그랑자이그랑몰
    29362: ["//div[@name='login-id']/input", "//div[@name='login-password']/input",
            "//button[contains(@class, 'login-button')]",
            "//*[@id='hho']", "//button[contains(@class, 'button-submit')]",
            "",  # radio 버튼 처리 안함
            "-",  # btnItem 없음
            "-",  # weekday 스크립트 제거
            "-",  # weekend 스크립트 제거
            "-",  # night 스크립트 제거
            ],

}

def get_har_in_script(park_id, ticket_name):
    # 1. 특정 주차장 + 특정 티켓 분기


    if park_id == 16003:
        if ticket_name in ["평일 당일권", "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)", "휴일 당일권"]:
            return "javascript:applyDiscount('98', '5', '25|29|', '파킹박', '1', '0');"
        elif ticket_name in ["평일 심야권", "휴일 심야권"]:
            return "javascript:applyDiscount('92', '1', '25|29|', '파킹박(야간)', '1', '0');"
        elif ticket_name == "평일 오후 6시간권":
            return "javascript:applyDiscount('93', '1', '', '평일오후6시간권(공유)', '1', '0');"
        elif ticket_name == "휴일 연박권":
            return "javascript:applyDiscount('80', '1', '25|29|', '2일권', '1', '0');"
        else:
            return False  # ❗️트윈시티남산에서 지정된 티켓 외는 실패 처리

    if park_id == 19174:
        t = ticket_name.strip()  # ← 이 줄 추가
        if t in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
            return "BTN_공유서비스 종일"
        elif t in ["휴일 당일권(토)", "휴일 당일권(일)"]:
            return "BTN_공유서비스 주말"
        elif t == "평일 12시간권(화~금)":
            return "BTN_12시간권_O2O"
        elif t in ["평일 심야권", "휴일 심야권"]:
            return "BTN_공유서비스 야간"
        elif t == "평일 3시간권":
            return "BTN_3시간권(공유서비스)"
        elif t == "평일 2시간권":
            return "BTN_2시간권(공유서비스)"
        elif t == "평일 1시간권":
            return "BTN_1시간권(공유서비스)"
        else:
            return False

    if park_id == 19364:
        if ticket_name in [
            "평일 당일권",
            "평일 당일권(월)",
            "평일 당일권(화)",
            "평일 당일권(수)",
            "평일 당일권(목)",
            "평일 당일권(금)"
        ]:
            return "javascript:applyDiscount('07', 'CP0802', '1', '01|20|24|', '평일당일권(공유서비스)', '999999999', '0');"
        elif ticket_name in [
            "휴일 당일권(토,공휴일)",
            "휴일 당일권(일)"
        ]:
            return "javascript:applyDiscount('08', 'CP0802', '1', '01|20|24|', '휴일당일권(공유서비스)', '999999999', '0');"
        elif ticket_name == "휴일 연박권(토,일)":
            return "javascript:applyDiscount('70', 'CP0802', '1', '20|24|', '2일권', '999999999', '0');"
        elif ticket_name == "평일 2시간권":
            return "javascript:applyDiscount('62', 'CP0802', '1', '', '평일2시간권(공유서비스)', '999999999', '0');"
        elif ticket_name == "평일 3시간권":
            return "javascript:applyDiscount('25', 'CP0802', '1', '', '3시간권', '999999999', '0');"
        elif ticket_name in ["평일 심야권", "휴일 심야권"]:
            return "javascript:applyDiscount('90', 'CP0802', '1', '20|', '심야권(공유서비스)', '999999999', '0');"
        else:
            return False


    # 2. 공통 룰
    if ticket_name[-3:] == "심야권" or ticket_name[-3:] == "야간권":
        if park_id in mapIdToWebInfo:
            return mapIdToWebInfo[park_id][WebInfo.night]
        else:
            return False  # ❗️대상 주차장에 정보 없으면 실패

    elif ticket_name == "평일1일권":
        if park_id in mapIdToWebInfo:
            return mapIdToWebInfo[park_id][WebInfo.weekday]
        else:
            return False

    elif ticket_name in ["주말1일권", "토요일권", "일요일권"]:
        if park_id in mapIdToWebInfo:
            return mapIdToWebInfo[park_id][WebInfo.weekend]
        else:
            return False

    # 3. 기타 티켓에 대해서 평일/주말에 따른 분기
    if park_id in mapIdToWebInfo:
        if Util.get_week_or_weekend() == 0:  # 평일
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]
        else:  # 주말
            return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]
    else:
        return False  # ❗️최종적으로도 없으면 실패


def check_discount_alert(driver, park_id=None):
    if park_id in [19364, 16003, 19456, 19194]:
        print("✅ 할인 결과 알림창 없음 → 예외 없이 성공 처리 (예상된 구조)")
        return True

    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()

        print(f"할인 결과 알림창: {alert_text}")

        # ❗️중복 클릭 등으로 인한 취소 의도 경고 감지
        if "취소 하시겠습니까" in alert_text:
            print("⚠️ 이미 할인된 항목을 재클릭하여 취소 확인창이 떴음 → 실패 처리")
            return False

        if "할인 되었습니다" in alert_text or "등록되었습니다" in alert_text:
            return True
        else:
            return False

    except Exception as e:
        print("❌ 할인 처리 후 알림창이 감지되지 않음:", e)
        return False


def is_discount_already_applied(driver, ticket_name):
    """
    19492 전용 - 할인적용내역에 현재 ticket_name에 해당하는 버튼만 있는지 확인
    추가 검사: 버튼 외 등록자/등록시각 정보까지 존재하는지 확인
    """
    expected_text_map = {
        "평일1일권": "24시간(유료)",
        "12시간권": "12시간(유료)",
        "주말1일권": "휴일당일권"
    }

    expected_text = expected_text_map.get(ticket_name)
    if not expected_text:
        print(f"[ERROR] ticket_name 매핑 실패: {ticket_name}")
        return False

    try:
        buttons = driver.find_elements(By.XPATH, "//table[@id='tbData_detail']//button[@name='btnDckey']")
        for btn in buttons:
            applied_text = btn.text.strip()
            if applied_text != expected_text:
                print(f"⚠️ 다른 할인권 이미 적용됨: {applied_text} ≠ {expected_text}")
                return False

            # 🔍 버튼 외 등록자/시간 확인
            try:
                row = btn.find_element(By.XPATH, "../../..")  # <tr>
                regman = row.find_elements(By.TAG_NAME, "td")[2].text.strip()
                regtime = row.find_elements(By.TAG_NAME, "td")[3].text.strip()
                if not regman or not regtime:
                    print("⚠️ 등록자/등록시각 비어있음 → 실제 할인 미적용 상태")
                    return False
            except Exception as e:
                print(f"⚠️ 등록자/시각 확인 실패 → 미적용 간주: {e}")
                return False

        if buttons:
            print(f"✅ 동일한 할인권 이미 적용됨: {expected_text}")
            return True
        else:
            print("ℹ️ 할인적용내역이 비어있음 → 새로 클릭해야 함")
            return False

    except Exception as e:
        print(f"[예외] 할인 적용 내역 확인 중 오류 발생: {e}")
        return False




def web_har_in(target, driver):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]
    park_type = ParkType.get_park_type(park_id)

    print(Colors.BLUE + f"DEBUG: HighCity.web_har_in 시작 - park_id: {park_id}, park_type: {park_type}" + Colors.ENDC)

    trim_car_num = Util.all_trim(ori_car_num)
    search_id = trim_car_num[-4:]

    print("parkId = " + str(park_id) + ", " + "searchId = " + search_id)
    print(Colors.BLUE + ticket_name + Colors.ENDC)

    print(Colors.BLUE + f"DEBUG: ParkUtil.is_park_in({park_id}) = {ParkUtil.is_park_in(park_id)}" + Colors.ENDC)
    print(Colors.BLUE + f"DEBUG: park_id {park_id} in mapIdToWebInfo = {park_id in mapIdToWebInfo}" + Colors.ENDC)
    
    if ParkUtil.is_park_in(park_id):
        if park_id in mapIdToWebInfo:
            login_url = ParkUtil.get_park_url(park_id)
            driver.implicitly_wait(3)
            
            try:
                driver.get(login_url)
            except Exception as url_ex:
                print(Colors.RED + f"❌ URL 접속 실패: {login_url}, 오류: {url_ex}" + Colors.ENDC)
                return False

            web_info = mapIdToWebInfo[park_id]
            web_har_in_info = ParkUtil.get_park_lot_option(park_id)
            
            print(Colors.BLUE + f"DEBUG: web_info 로드 완료: {web_info}" + Colors.ENDC)
            print(Colors.BLUE + f"DEBUG: web_har_in_info 로드 완료: {web_har_in_info}" + Colors.ENDC)

            # 재접속이 아닐 때, 그러니까 처음 접속할 때
            print(Colors.BLUE + f"DEBUG: ParkUtil.first_access({park_id}, {driver.current_url}) 확인 중..." + Colors.ENDC)
            first_access_result = ParkUtil.first_access(park_id, driver.current_url)
            print(Colors.BLUE + f"DEBUG: ParkUtil.first_access 결과: {first_access_result}" + Colors.ENDC)
            
            if first_access_result:
                print(Colors.GREEN + "DEBUG: first_access가 True - 로그인 과정 실행" + Colors.ENDC)
                print(Colors.BLUE + f"DEBUG: 로그인 페이지 접속 - URL: {driver.current_url}" + Colors.ENDC)

                try:
                    # WebDriverWait를 사용하여 요소가 나타날 때까지 최대 10초간 기다립니다.
                    wait = WebDriverWait(driver, 10)

                    # ID 입력 - XPath인지 ID인지 자동 판별
                    id_selector = web_info[WebInfo.inputId]
                    print(Colors.BLUE + f"DEBUG: ID 입력 필드 찾는 중 - {id_selector}" + Colors.ENDC)
                    if id_selector.startswith("//") or id_selector.startswith("/"):
                        # XPath 사용
                        user_id_field = wait.until(EC.presence_of_element_located((By.XPATH, id_selector)))
                    else:
                        # ID 사용
                        user_id_field = wait.until(EC.presence_of_element_located((By.ID, id_selector)))
                    
                    # 29364 주차장은 JavaScript로 입력 (React/Vue 프레임워크 대응)
                    if park_id in [29364, 29361, 29362]:
                        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", 
                                             user_id_field, web_har_in_info[WebInfo.webHarInId])
                    else:
                        user_id_field.send_keys(web_har_in_info[WebInfo.webHarInId])
                    print(Colors.GREEN + "✅ ID 입력 완료" + Colors.ENDC)

                    # PW 입력 - XPath인지 ID인지 자동 판별
                    pw_selector = web_info[WebInfo.inputPw]
                    print(Colors.BLUE + f"DEBUG: PW 입력 필드 찾는 중 - {pw_selector}" + Colors.ENDC)
                    if pw_selector.startswith("//") or pw_selector.startswith("/"):
                        # XPath 사용
                        user_pw_field = wait.until(EC.presence_of_element_located((By.XPATH, pw_selector)))
                    else:
                        # ID 사용
                        user_pw_field = wait.until(EC.presence_of_element_located((By.ID, pw_selector)))
                    
                    # 29364 주차장은 JavaScript로 입력 (React/Vue 프레임워크 대응)
                    if park_id in [29364, 29361, 29362]:
                        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", 
                                             user_pw_field, web_har_in_info[WebInfo.webHarInPw])
                    else:
                        user_pw_field.send_keys(web_har_in_info[WebInfo.webHarInPw])
                    print(Colors.GREEN + "✅ PW 입력 완료" + Colors.ENDC)

                    # 로그인 버튼 클릭
                    print(Colors.BLUE + f"DEBUG: 로그인 버튼 찾는 중 - {web_info[WebInfo.btnLogin]}" + Colors.ENDC)
                    login_button = wait.until(EC.presence_of_element_located((By.XPATH, web_info[WebInfo.btnLogin])))
                    # 29364 주차장은 JavaScript로 클릭 (React/Vue 프레임워크 대응)
                    if park_id in [29364, 29361, 29362]:
                        driver.execute_script("arguments[0].click();", login_button)
                    else:
                        login_button.click()
                    print(Colors.GREEN + "✅ 로그인 버튼 클릭 완료" + Colors.ENDC)

                    # 29364 주차장: 로그인 후 모달 팝업 처리 (다른 기기 로그인 전환 확인)
                    if park_id in [29364, 29361, 29362]:
                        try:
                            Util.sleep(2)  # 모달이 나타날 시간 대기
                            wait_modal = WebDriverWait(driver, 5)
                            
                            # 모달 텍스트 확인 ("다른 기기에 로그인되어 있습니다" 포함)
                            modal_text = wait_modal.until(
                                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '다른 기기에 로그인되어 있습니다')]"))
                            )
                            
                            # 모달이 실제로 보이는지 확인 (부모 modal-container 확인)
                            modal_container = modal_text.find_element(By.XPATH, "./ancestor::div[@class='modal-container']")
                            is_visible = driver.execute_script(
                                "var style = window.getComputedStyle(arguments[0]); return style.display !== 'none' && style.visibility !== 'hidden';",
                                modal_container
                            )
                            
                            if is_visible:
                                print(Colors.BLUE + "DEBUG: 로그인 전환 모달 팝업 감지됨" + Colors.ENDC)
                                
                                # 확인 버튼 찾기 - 여러 방법 시도
                                try:
                                    # 방법 1: modal-container 내부의 확인 버튼 찾기
                                    modal_submit_button = modal_container.find_element(By.XPATH, ".//button[contains(@class, 'modal-submit-button')]")
                                except:
                                    # 방법 2: 전체 페이지에서 확인 버튼 찾기
                                    modal_submit_button = wait_modal.until(
                                        EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'modal-submit-button')]"))
                                    )
                                
                                # 버튼이 보이는지 확인 후 클릭
                                button_visible = driver.execute_script(
                                    "var style = window.getComputedStyle(arguments[0]); return style.display !== 'none' && style.visibility !== 'hidden';",
                                    modal_submit_button
                                )
                                
                                if button_visible:
                                    driver.execute_script("arguments[0].click();", modal_submit_button)
                                    print(Colors.GREEN + "✅ 모달 확인 버튼 클릭 완료" + Colors.ENDC)
                                    Util.sleep(2)  # 모달 닫힐 시간 대기
                                else:
                                    print(Colors.YELLOW + "⚠️ 확인 버튼이 보이지 않음" + Colors.ENDC)
                            else:
                                print(Colors.BLUE + "DEBUG: 로그인 전환 모달이 숨겨져 있음" + Colors.ENDC)
                        except Exception as e:
                            # 모달이 나타나지 않았거나 이미 사라진 경우 (정상)
                            print(Colors.BLUE + f"DEBUG: 로그인 전환 모달 없음 (정상) - {str(e)[:100]}" + Colors.ENDC)

                except Exception as e:
                    print(Colors.RED + f"❌ 로그인 과정에서 오류 발생: {e}" + Colors.ENDC)
                    return False  # 로그인 실패 시 함수 종료

                driver.implicitly_wait(3)

                print(Colors.BLUE + f"DEBUG: 차량번호 검색 - {search_id}" + Colors.ENDC)
                # 차량번호 입력 필드 - XPath인지 ID인지 자동 판별
                search_selector = web_info[WebInfo.inputSearch]
                wait_search = WebDriverWait(driver, 10)
                
                if park_id in [29364, 29361, 29362]:
                    # 29364 주차장: React/Vue 프레임워크 대응 - JavaScript로 입력
                    try:
                        # ID로 요소 찾기
                        search_field = wait_search.until(
                            EC.presence_of_element_located((By.ID, "hho"))
                        )
                        # JavaScript로 값 입력 및 이벤트 트리거
                        driver.execute_script(
                            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true })); arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                            search_field, search_id
                        )
                        print(Colors.GREEN + "✅ 차량번호 입력 완료 (JavaScript)" + Colors.ENDC)
                        Util.sleep(1)
                    except Exception as e:
                        print(Colors.RED + f"❌ 차량번호 입력 실패: {e}" + Colors.ENDC)
                        return False
                else:
                    # 다른 주차장: 기존 방식
                    if search_selector.startswith("//") or search_selector.startswith("/"):
                        # XPath 사용
                        search_field = wait_search.until(
                            EC.presence_of_element_located((By.XPATH, search_selector))
                        )
                        search_field.send_keys(search_id)
                    else:
                        # ID 사용
                        search_field = wait_search.until(
                            EC.presence_of_element_located((By.ID, search_selector))
                        )
                        search_field.send_keys(search_id)
                    Util.sleep(3)

                print(Colors.BLUE + f"DEBUG: 검색 버튼 클릭 - {web_info[WebInfo.btnSearch]}" + Colors.ENDC)
                if park_id in [29364, 29361, 29362]:
                    # 29364 주차장: JavaScript로 클릭
                    try:
                        # 차량번호 입력 필드와 같은 부모 안의 검색 버튼 찾기
                        search_button = wait_search.until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'mh-search-wrap')]/input[@id='hho']/following-sibling::button[contains(@class, 'button-submit')]"))
                        )
                    except:
                        # 위 방법이 실패하면 일반적인 button-submit 찾기
                        search_button = wait_search.until(
                            EC.presence_of_element_located((By.XPATH, web_info[WebInfo.btnSearch]))
                        )
                    driver.execute_script("arguments[0].click();", search_button)
                    print(Colors.GREEN + "✅ 검색 버튼 클릭 완료 (JavaScript)" + Colors.ENDC)
                else:
                    search_button = wait_search.until(
                        EC.element_to_be_clickable((By.XPATH, web_info[WebInfo.btnSearch]))
                    )
                    search_button.click()
                Util.sleep(2)
                print(Colors.GREEN + "✅ 차량 검색 완료" + Colors.ENDC)

                print(Colors.BLUE + f"DEBUG: ParkUtil.check_search({park_id}, driver) 호출 직전..." + Colors.ENDC)
                print(Colors.BLUE + f"DEBUG: 현재 페이지 URL: {driver.current_url}" + Colors.ENDC)

                if park_id in [29218, 18996]:
                    target_car_number = ori_car_num.replace(" ", "")  # 차량번호 공백제거

                    # 결과 tr 리스트에서 원하는 차량 tr을 찾아 클릭
                    tr_list = WebDriverWait(driver, 5).until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, "//table[tbody/tr/th/h1[contains(text(), '입차 차량 조회 내역')]]/tbody/tr[td]")
                        )
                    )
                    matched = False
                    for tr in tr_list:
                        td_list = tr.find_elements(By.TAG_NAME, "td")
                        for td in td_list:
                            # 차량번호 추출 후 비교 (공백제거 등 필요시 추가)
                            car_number_text = td.text.replace(" ", "")
                            if target_car_number in car_number_text:
                                driver.execute_script("arguments[0].click();", tr)
                                print(f"✅ 차량번호 {target_car_number} 선택 클릭 완료")
                                matched = True
                                break
                        if matched:
                            break
                    if not matched:
                        print(f"❌ '{target_car_number}' 번호에 해당하는 차량이 조회 결과에 없습니다.")
                        return False

                print(Colors.BLUE + f"DEBUG: ParkUtil.check_search({park_id}, driver) 확인 중..." + Colors.ENDC)
                check_search_result = ParkUtil.check_search(park_id, driver)
                print(Colors.BLUE + f"DEBUG: ParkUtil.check_search 결과: {check_search_result}" + Colors.ENDC)
                
                # 29364 & 29361 & 29362 주차장: URL이 할인 등록 페이지면 바로 심야권 처리로 진행
                if park_id in [29364, 29361, 29362] and "/discount/regist/" in driver.current_url:
                    print(Colors.BLUE + "DEBUG: (29364/29361/29362) 할인 등록 페이지 감지 - 할인 처리로 진행" + Colors.ENDC)
                    return process_highcity_2936x_discount(driver, ticket_name, park_id)

                if check_search_result:
                    print(Colors.BLUE + f"DEBUG: ParkUtil.check_same_car_num({park_id}, {ori_car_num}, driver) 확인 중..." + Colors.ENDC)
                    check_same_car_result = ParkUtil.check_same_car_num(park_id, ori_car_num, driver)
                    print(Colors.BLUE + f"DEBUG: ParkUtil.check_same_car_num 결과: {check_same_car_result}" + Colors.ENDC)
                    
                    if check_same_car_result:

                        # 29364 & 29361 & 29362 주차장: 심야권 처리
                        if park_id in [29364, 29361, 29362] and ticket_name == "심야권":
                            try:
                                wait_ticket = WebDriverWait(driver, 10)
                                
                                # 1. "심야권" 쿠폰 항목 찾기 및 plus 버튼 클릭
                                print(Colors.BLUE + "DEBUG: 심야권 쿠폰 항목 찾는 중..." + Colors.ENDC)
                                night_ticket_item = wait_ticket.until(
                                    EC.presence_of_element_located((By.XPATH, "//div[@class='discount-coupon-item']//span[@class='coupon-type' and text()='심야권']/ancestor::div[@class='discount-coupon-item']"))
                                )
                                
                                # plus 버튼 클릭
                                plus_button = night_ticket_item.find_element(By.XPATH, ".//button[contains(@class, 'plus-button')]")
                                driver.execute_script("arguments[0].click();", plus_button)
                                print(Colors.GREEN + "✅ 심야권 plus 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(1)
                                
                                # 2. "할인하기" 버튼 클릭
                                print(Colors.BLUE + "DEBUG: 할인하기 버튼 찾는 중..." + Colors.ENDC)
                                discount_button = wait_ticket.until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@class='reduce-parking-fees-footer']//button[contains(@class, 'discount-button')]//span[text()='할인하기']/ancestor::button"))
                                )
                                driver.execute_script("arguments[0].click();", discount_button)
                                print(Colors.GREEN + "✅ 할인하기 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(1.5)
                                
                                # 3. 확인 모달 - "확인" 버튼 클릭
                                print(Colors.BLUE + "DEBUG: 할인 확인 모달 찾는 중..." + Colors.ENDC)
                                confirm_modal = wait_ticket.until(
                                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '할인을')]"))
                                )
                                confirm_button = wait_ticket.until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@class='modal-container']//button[contains(@class, 'modal-submit-button')]"))
                                )
                                driver.execute_script("arguments[0].click();", confirm_button)
                                print(Colors.GREEN + "✅ 할인 확인 모달 '확인' 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(4)  # 4초 대기
                                
                                # 4. 로그아웃 처리
                                print(Colors.BLUE + "DEBUG: 로그아웃 처리 시작" + Colors.ENDC)
                                wait_logout = WebDriverWait(driver, 10)
                                
                                # 햄버거 메뉴 버튼 클릭
                                menu_button = wait_logout.until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@class='am-header']//button[contains(@class, 'am-image-button')]//i[contains(@class, 'i-ico-hamburger')]/ancestor::button[1]"))
                                )
                                driver.execute_script("arguments[0].click();", menu_button)
                                print(Colors.GREEN + "✅ 햄버거 메뉴 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(1.5)
                                
                                # 프로필 버튼 클릭
                                profile_button = wait_logout.until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[@id='my' and contains(@class, 'am-image-button')]"))
                                )
                                driver.execute_script("arguments[0].click();", profile_button)
                                print(Colors.GREEN + "✅ 프로필 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(1.5)
                                
                                # 로그아웃 버튼 클릭
                                logout_button = wait_logout.until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@class='my-control']//button[contains(@class, 'am-button')]//span[text()='로그아웃']/ancestor::button[1]"))
                                )
                                driver.execute_script("arguments[0].click();", logout_button)
                                print(Colors.GREEN + "✅ 로그아웃 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(1.5)
                                
                                # 로그아웃 확인 모달 - "예" 버튼 클릭
                                modal_text = wait_logout.until(
                                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '계정을 로그아웃')]"))
                                )
                                print(Colors.BLUE + "DEBUG: 로그아웃 확인 모달 감지됨" + Colors.ENDC)
                                
                                confirm_logout_button = wait_logout.until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@class='modal-container']//button[contains(@class, 'modal-submit-button')]"))
                                )
                                driver.execute_script("arguments[0].click();", confirm_logout_button)
                                print(Colors.GREEN + "✅ 로그아웃 확인 모달 '예' 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(2)
                                
                                print(Colors.GREEN + "✅ 심야권 할인 처리 완료 - True 반환" + Colors.ENDC)
                                return True
                                
                            except Exception as e:
                                print(Colors.RED + f"❌ 29364/29361/29362 심야권 처리 실패: {e}" + Colors.ENDC)
                                return False
                    else:
                        print(Colors.YELLOW + f"⚠️ 29364/29361/29362 할인 등록 페이지이지만 ticket_name이 '심야권'이 아님: {ticket_name}" + Colors.ENDC)
                        return False
                
                # 29364 & 29361 & 29362 주차장: 검색 실패 시 뒤로가기 버튼 클릭 후 로그아웃
                if park_id in [29364, 29361, 29362] and not check_search_result:
                    try:
                        # "차량을 찾지 못했습니다" 메시지 확인
                        empty_results = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'empty-results')]"))
                        )
                        print(Colors.YELLOW + "⚠️ 차량 검색 실패 - 뒤로가기 버튼 클릭" + Colors.ENDC)
                        # 뒤로가기 버튼 클릭
                        goback_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'button-goback')]"))
                        )
                        driver.execute_script("arguments[0].click();", goback_button)
                        print(Colors.GREEN + "✅ 뒤로가기 버튼 클릭 완료" + Colors.ENDC)
                        Util.sleep(2)  # 페이지 전환 대기
                        
                        # 로그아웃 처리
                        print(Colors.BLUE + "DEBUG: 로그아웃 처리 시작" + Colors.ENDC)
                        try:
                            wait_logout = WebDriverWait(driver, 10)
                            
                            # 1. 햄버거 메뉴 버튼 클릭
                            menu_button = wait_logout.until(
                                EC.element_to_be_clickable((By.XPATH, "//div[@class='am-header']//button[contains(@class, 'am-image-button')]//i[contains(@class, 'i-ico-hamburger')]/ancestor::button[1]"))
                            )
                            driver.execute_script("arguments[0].click();", menu_button)
                            print(Colors.GREEN + "✅ 햄버거 메뉴 버튼 클릭 완료" + Colors.ENDC)
                            Util.sleep(1.5)
                            
                            # 2. 프로필 버튼 클릭
                            profile_button = wait_logout.until(
                                EC.element_to_be_clickable((By.XPATH, "//button[@id='my' and contains(@class, 'am-image-button')]"))
                            )
                            driver.execute_script("arguments[0].click();", profile_button)
                            print(Colors.GREEN + "✅ 프로필 버튼 클릭 완료" + Colors.ENDC)
                            Util.sleep(1.5)
                            
                            # 3. 로그아웃 버튼 클릭
                            logout_button = wait_logout.until(
                                EC.element_to_be_clickable((By.XPATH, "//div[@class='my-control']//button[contains(@class, 'am-button')]//span[text()='로그아웃']/ancestor::button[1]"))
                            )
                            driver.execute_script("arguments[0].click();", logout_button)
                            print(Colors.GREEN + "✅ 로그아웃 버튼 클릭 완료" + Colors.ENDC)
                            Util.sleep(1.5)
                            
                            # 4. 로그아웃 확인 모달 - "예" 버튼 클릭
                            try:
                                # 모달 텍스트 확인 ("계정을 로그아웃" 포함)
                                modal_text = wait_logout.until(
                                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '계정을 로그아웃')]"))
                                )
                                print(Colors.BLUE + "DEBUG: 로그아웃 확인 모달 감지됨" + Colors.ENDC)
                                
                                # "예" 버튼 클릭
                                confirm_button = wait_logout.until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@class='modal-container']//button[contains(@class, 'modal-submit-button')]"))
                                )
                                driver.execute_script("arguments[0].click();", confirm_button)
                                print(Colors.GREEN + "✅ 로그아웃 확인 모달 '예' 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(2)  # 로그아웃 완료 대기
                                
                            except Exception as modal_e:
                                print(Colors.YELLOW + f"⚠️ 로그아웃 확인 모달 처리 실패: {modal_e}" + Colors.ENDC)
                            
                            print(Colors.BLUE + "DEBUG: 로그아웃 처리 완료 - False 반환" + Colors.ENDC)
                            return False
                            
                        except Exception as logout_e:
                            print(Colors.RED + f"❌ 로그아웃 처리 실패: {logout_e}" + Colors.ENDC)
                            return False
                            
                    except Exception as e:
                        print(Colors.YELLOW + f"⚠️ 뒤로가기 버튼 클릭 실패 또는 검색 결과 페이지가 아님: {e}" + Colors.ENDC)
                        return False
                
                if check_search_result:
                    print(Colors.BLUE + f"DEBUG: ParkUtil.check_same_car_num({park_id}, {ori_car_num}, driver) 확인 중..." + Colors.ENDC)
                    check_same_car_result = ParkUtil.check_same_car_num(park_id, ori_car_num, driver)
                    print(Colors.BLUE + f"DEBUG: ParkUtil.check_same_car_num 결과: {check_same_car_result}" + Colors.ENDC)
                    
                    if check_same_car_result:

                        # 29364 & 29361 & 29362 주차장: 심야권 처리
                        if park_id in [29364, 29361, 29362] and ticket_name == "심야권":
                            try:
                                wait_ticket = WebDriverWait(driver, 10)
                                
                                # 1. "심야권" 쿠폰 항목 찾기 및 plus 버튼 클릭
                                print(Colors.BLUE + "DEBUG: 심야권 쿠폰 항목 찾는 중..." + Colors.ENDC)
                                night_ticket_item = wait_ticket.until(
                                    EC.presence_of_element_located((By.XPATH, "//div[@class='discount-coupon-item']//span[@class='coupon-type' and text()='심야권']/ancestor::div[@class='discount-coupon-item']"))
                                )
                                
                                # plus 버튼 클릭
                                plus_button = night_ticket_item.find_element(By.XPATH, ".//button[contains(@class, 'plus-button')]")
                                driver.execute_script("arguments[0].click();", plus_button)
                                print(Colors.GREEN + "✅ 심야권 plus 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(1)
                                
                                # 2. "할인하기" 버튼 클릭
                                print(Colors.BLUE + "DEBUG: 할인하기 버튼 찾는 중..." + Colors.ENDC)
                                discount_button = wait_ticket.until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@class='reduce-parking-fees-footer']//button[contains(@class, 'discount-button')]//span[text()='할인하기']/ancestor::button"))
                                )
                                driver.execute_script("arguments[0].click();", discount_button)
                                print(Colors.GREEN + "✅ 할인하기 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(1.5)
                                
                                # 3. 확인 모달 - "확인" 버튼 클릭
                                print(Colors.BLUE + "DEBUG: 할인 확인 모달 찾는 중..." + Colors.ENDC)
                                confirm_modal = wait_ticket.until(
                                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '할인을')]"))
                                )
                                confirm_button = wait_ticket.until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@class='modal-container']//button[contains(@class, 'modal-submit-button')]"))
                                )
                                driver.execute_script("arguments[0].click();", confirm_button)
                                print(Colors.GREEN + "✅ 할인 확인 모달 '확인' 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(4)  # 4초 대기
                                
                                # 4. 로그아웃 처리
                                print(Colors.BLUE + "DEBUG: 로그아웃 처리 시작" + Colors.ENDC)
                                wait_logout = WebDriverWait(driver, 10)
                                
                                # 햄버거 메뉴 버튼 클릭
                                menu_button = wait_logout.until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@class='am-header']//button[contains(@class, 'am-image-button')]//i[contains(@class, 'i-ico-hamburger')]/ancestor::button[1]"))
                                )
                                driver.execute_script("arguments[0].click();", menu_button)
                                print(Colors.GREEN + "✅ 햄버거 메뉴 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(1.5)
                                
                                # 프로필 버튼 클릭
                                profile_button = wait_logout.until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[@id='my' and contains(@class, 'am-image-button')]"))
                                )
                                driver.execute_script("arguments[0].click();", profile_button)
                                print(Colors.GREEN + "✅ 프로필 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(1.5)
                                
                                # 로그아웃 버튼 클릭
                                logout_button = wait_logout.until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@class='my-control']//button[contains(@class, 'am-button')]//span[text()='로그아웃']/ancestor::button[1]"))
                                )
                                driver.execute_script("arguments[0].click();", logout_button)
                                print(Colors.GREEN + "✅ 로그아웃 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(1.5)
                                
                                # 로그아웃 확인 모달 - "예" 버튼 클릭
                                modal_text = wait_logout.until(
                                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '계정을 로그아웃')]"))
                                )
                                print(Colors.BLUE + "DEBUG: 로그아웃 확인 모달 감지됨" + Colors.ENDC)
                                
                                confirm_logout_button = wait_logout.until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@class='modal-container']//button[contains(@class, 'modal-submit-button')]"))
                                )
                                driver.execute_script("arguments[0].click();", confirm_logout_button)
                                print(Colors.GREEN + "✅ 로그아웃 확인 모달 '예' 버튼 클릭 완료" + Colors.ENDC)
                                Util.sleep(2)
                                
                                print(Colors.GREEN + "✅ 심야권 할인 처리 완료 - True 반환" + Colors.ENDC)
                                return True
                                
                            except Exception as e:
                                print(Colors.RED + f"❌ 29364/29361/29362 심야권 처리 실패: {e}" + Colors.ENDC)
                                return False

                        # ✅ 여기에 radio 체크 처리 삽입
                        btn_item = web_info[WebInfo.btnItem]

                        if park_id != 19492 and btn_item and btn_item != "-":
                            try:
                                radio = WebDriverWait(driver, 3).until(
                                    EC.presence_of_element_located((By.ID, btn_item)))
                                driver.execute_script("arguments[0].click();", radio)
                                print(Colors.GREEN + f"✅ 차량 라디오 버튼 클릭 완료 ({btn_item})" + Colors.ENDC)
                                Util.sleep(1)
                            except Exception as e:
                                print(Colors.RED + f"❌ 차량 라디오 버튼 클릭 실패: {e}" + Colors.ENDC)
                                return False


                        if park_id == 19456:
                            if ticket_name == "휴일 당일권":
                                try:
                                    btn = WebDriverWait(driver, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, '//input[@type="button" and @value="ppark"]'))
                                    )
                                    driver.execute_script("arguments[0].click();", btn)
                                    print(Colors.GREEN + "✅ 'ppark' 버튼 클릭 성공 (19456, 휴일 당일권)" + Colors.ENDC)

                                    # Alert 처리
                                    try:
                                        WebDriverWait(driver, 3).until(EC.alert_is_present())
                                        alert = driver.switch_to.alert
                                        print(Colors.BLUE + f"할인 알림창 텍스트: {alert.text}" + Colors.ENDC)
                                        alert.accept()
                                        print(Colors.GREEN + "✅ 알림창 확인 완료 (19456)" + Colors.ENDC)
                                    except Exception as e:
                                        print(Colors.YELLOW + f"⚠️ 알림창 없음 또는 확인 실패: {e}" + Colors.ENDC)

                                    return True

                                except Exception as e:
                                    print(Colors.RED + f"❌ 'ppark' 버튼 클릭 실패 (19456): {e}" + Colors.ENDC)
                                    return False

                        if park_id == 19492:
                            try:
                                # 1. 차량 행 클릭 → 팝업 열기
                                if is_discount_already_applied(driver, ticket_name):
                                    return True  # 이미 동일한 할인권 적용 → 성공


                                tr = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "#tbData > tbody > tr"))
                                )
                                driver.execute_script("arguments[0].click();", tr)
                                print(Colors.GREEN + "✅ 19492 차량 선택 <tr> 클릭 성공" + Colors.ENDC)
                                Util.sleep(1.5)  # 팝업 로딩 시간 대기

                                # 2. ticket_name → 할인 버튼 텍스트 매핑
                                if ticket_name == "평일1일권":
                                    button_text = "24시간(유료)"
                                elif ticket_name == "12시간권":
                                    button_text = "12시간(유료)"
                                elif ticket_name == "주말1일권":
                                    button_text = "휴일당일권"
                                else:
                                    print(Colors.RED + "❌ 정의되지 않은 ticket_name" + Colors.ENDC)
                                    return False

                                # 3. 할인 적용 내역 중복 확인
                                already_applied = False
                                try:
                                    table = driver.find_element(By.ID, "tbData_detail")
                                    if button_text in table.text:
                                        print(Colors.YELLOW + f"⚠️ 이미 할인된 내역 존재: {button_text}" + Colors.ENDC)
                                        already_applied = True
                                except Exception:
                                    pass  # 테이블이 없는 경우 무시

                                if already_applied:
                                    return True  # 이미 적용된 경우 성공 처리

                                # 4. 할인 버튼 클릭 (팝업 내에서)
                                btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, f"//button[@name='btnDckey' and text()='{button_text}']"))
                                )
                                driver.execute_script("arguments[0].click();", btn)
                                print(Colors.GREEN + f"✅ 팝업 내 할인 버튼 클릭 성공: {button_text}" + Colors.ENDC)

                                # 5. Alert 처리 및 메시지 분석
                                try:
                                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                                    alert = driver.switch_to.alert
                                    alert_text = alert.text
                                    print(Colors.BLUE + f"할인 알림창 텍스트: {alert_text}" + Colors.ENDC)
                                    alert.accept()

                                    if "취소하시겠습니다" in alert_text or "할인을 취소" in alert_text:
                                        print(Colors.RED + "❌ 이미 할인된 항목 재클릭 → 할인 취소됨" + Colors.ENDC)
                                        return False
                                    elif "할인 되었습니다" in alert_text or "등록되었습니다" in alert_text:
                                        return True
                                    else:
                                        print(Colors.YELLOW + "⚠️ 알림창 텍스트가 성공인지 불확실 → 실패 처리" + Colors.ENDC)
                                        return False

                                except Exception as e:
                                    print(Colors.RED + f"❌ 알림창 확인 실패: {e}" + Colors.ENDC)
                                    return False

                            except Exception as e:
                                print(Colors.RED + f"❌ 19492 할인 처리 중 오류: {e}" + Colors.ENDC)
                                return False

                        if park_id == 29248:
                            try:
                                # <a class="sale-popup-open"> 요소 클릭 (차량 선택)
                                a_tag = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.sale-popup-open"))
                                )
                                driver.execute_script("arguments[0].click();", a_tag)
                                print(Colors.GREEN + "✅ 29248 차량 클릭 성공" + Colors.ENDC)

                                Util.sleep(1.5)  # 팝업 또는 화면 전환 대기

                                # ticket_name에 따라 할인권 선택
                                if ticket_name in ["평일 당일권", "휴일 당일권"]:
                                    select_element = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder_ddlDiscountName"))
                                    )
                                    select = Select(select_element)
                                    select.select_by_visible_text("일일권")
                                    print(Colors.GREEN + "✅ '일일권' 선택 성공" + Colors.ENDC)

                                    # 적용 버튼 클릭
                                    apply_button = WebDriverWait(driver, 5).until(
                                        EC.element_to_be_clickable((By.ID, "ContentPlaceHolder_lbtnDiscountApply"))
                                    )
                                    apply_button.click()
                                    print(Colors.GREEN + "✅ 할인 적용 버튼 클릭 완료" + Colors.ENDC)

                                    # 알림창 처리
                                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                                    alert = driver.switch_to.alert
                                    print(f"알림창 텍스트: {alert.text}")
                                    alert.accept()
                                    print(Colors.GREEN + "✅ 알림창 확인 완료" + Colors.ENDC)

                                    return True
                                else:
                                    print(Colors.RED + f"❌ 정의되지 않은 ticket_name: {ticket_name}" + Colors.ENDC)
                                    return False

                            except Exception as e:
                                print(Colors.RED + f"❌ 29248 처리 중 오류: {e}" + Colors.ENDC)
                                return False

                        if park_id == 15313:
                            try:
                                # 차량번호 입력
                                driver.find_element(By.ID, web_info[WebInfo.inputSearch]).clear()
                                driver.find_element(By.ID, web_info[WebInfo.inputSearch]).send_keys(search_id)
                                Util.sleep(1.5)  # 자동 검색 대기

                                # ✅ <tr> 직접 클릭해서 팝업 띄우기
                                tr_element = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable(
                                        (By.CSS_SELECTOR, "#tbData > tbody > tr[data-toggle='modal']"))
                                )
                                driver.execute_script("arguments[0].click();", tr_element)
                                print(Colors.GREEN + "✅ 차량 행(<tr>) 클릭 성공, 팝업 호출됨 (15313)" + Colors.ENDC)

                                Util.sleep(1.5)

                                # 할인 버튼 텍스트 매핑
                                if ticket_name == "주말1일권":
                                    button_text = "어플주말당일권(웹할인)"
                                elif ticket_name == "평일1일권":
                                    button_text = "어플평일당일권1(웹할인)"
                                elif ticket_name == "평일 저녁권":
                                    button_text = "어플평일야간권(웹할인)"
                                else:
                                    print(Colors.RED + f"❌ 정의되지 않은 ticket_name: {ticket_name}" + Colors.ENDC)
                                    return False


                                # 팝업 내 할인 버튼 클릭 (텍스트 정확히 일치하는 버튼 탐색)
                                discount_btns = WebDriverWait(driver, 5).until(
                                    EC.presence_of_all_elements_located((By.XPATH, "//button[@name='btnDckey']"))
                                )

                                matched = False
                                for btn in discount_btns:
                                    if btn.text.strip() == button_text:
                                        driver.execute_script("arguments[0].click();", btn)
                                        matched = True
                                        print(Colors.GREEN + f"✅ 할인 버튼 클릭 성공: {button_text}" + Colors.ENDC)
                                        break

                                if not matched:
                                    print(Colors.RED + f"❌ 정확히 일치하는 할인 버튼을 찾지 못했습니다: {button_text}" + Colors.ENDC)
                                    return False


                                # Alert 처리
                                try:
                                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                                    alert = driver.switch_to.alert
                                    print(f"할인 알림창 텍스트: {alert.text}")
                                    alert.accept()
                                    print(Colors.GREEN + "✅ 알림창 확인 완료" + Colors.ENDC)
                                except Exception as e:
                                    print(Colors.YELLOW + f"⚠️ 알림창 없음 또는 확인 실패: {e}" + Colors.ENDC)

                                return True

                            except Exception as e:
                                print(Colors.RED + f"❌ 15313 처리 중 오류: {e}" + Colors.ENDC)
                                return False

                        elif park_id == 19517:
                            try:
                                # 차량번호 입력
                                driver.find_element(By.ID, web_info[WebInfo.inputSearch]).clear()
                                driver.find_element(By.ID, web_info[WebInfo.inputSearch]).send_keys(search_id)
                                Util.sleep(1.5)  # 자동 검색 대기

                                # ✅ <tr> 직접 클릭해서 팝업 띄우기
                                tr_element = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable(
                                        (By.CSS_SELECTOR, "#tbData > tbody > tr[data-toggle='modal']"))
                                )
                                driver.execute_script("arguments[0].click();", tr_element)
                                print(Colors.GREEN + "✅ 차량 행(<tr>) 클릭 성공, 팝업 호출됨 (19517)" + Colors.ENDC)

                                Util.sleep(1.5)

                                # 할인 버튼 텍스트 매핑
                                if ticket_name == "평일1일권":
                                    button_text = "(유료)당일권"
                                else:
                                    print(Colors.RED + f"❌ 정의되지 않은 ticket_name: {ticket_name}" + Colors.ENDC)
                                    return False

                                # 팝업 내 할인 버튼 클릭 (텍스트 정확히 일치하는 버튼 탐색)
                                discount_btns = WebDriverWait(driver, 5).until(
                                    EC.presence_of_all_elements_located((By.XPATH, "//button[@name='btnDckey']"))
                                )

                                matched = False
                                for btn in discount_btns:
                                    if btn.text.strip() == button_text:
                                        driver.execute_script("arguments[0].click();", btn)
                                        matched = True
                                        print(Colors.GREEN + f"✅ 할인 버튼 클릭 성공: {button_text}" + Colors.ENDC)
                                        break

                                if not matched:
                                    print(Colors.RED + f"❌ 정확히 일치하는 할인 버튼을 찾지 못했습니다: {button_text}" + Colors.ENDC)
                                    return False

                                # Alert 처리
                                try:
                                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                                    alert = driver.switch_to.alert
                                    print(f"할인 알림창 텍스트: {alert.text}")
                                    alert.accept()
                                    print(Colors.GREEN + "✅ 알림창 확인 완료" + Colors.ENDC)
                                except Exception as e:
                                    print(Colors.YELLOW + f"⚠️ 알림창 없음 또는 확인 실패: {e}" + Colors.ENDC)

                                return True

                            except Exception as e:
                                print(Colors.RED + f"❌ 19517 처리 중 오류: {e}" + Colors.ENDC)
                                return False


                        if park_id == 13007:
                            print(f"DEBUG: 13007 전용 할인 처리 시작 (ticket_name={ticket_name})")

                            ticket_button_map = {
                                "평일 당일권": "파킹박",
                                "평일 당일권(월)": "파킹박",
                                "평일 당일권(화)": "파킹박",
                                "평일 당일권(수)": "파킹박",
                                "평일 당일권(목)": "파킹박",
                                "평일 당일권(금)": "파킹박",
                                "휴일 당일권": "파킹박",
                                "평일 3시간권": "평일3시간권(공유서비스)",
                                "평일 6시간권": "6시간권",
                                "휴일 6시간권": "6시간권",
                                "휴일 24시간권": "휴일24시간(공유서비스)"
                            }

                            button_text = ticket_button_map.get(ticket_name)
                            if not button_text:
                                print(f"ERROR: 13007에서 처리할 수 없는 ticket_name: {ticket_name}")
                                return False

                            try:
                                # 해당 텍스트를 가진 버튼 찾기
                                button = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, f"//input[@type='button' and @value='{button_text}']"))
                                )
                                driver.execute_script("arguments[0].click();", button)
                                print(f"DEBUG: 버튼 클릭 완료 (텍스트: {button_text})")

                                # Alert 처리
                                try:
                                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                                    alert = driver.switch_to.alert
                                    print(f"DEBUG: 알림창 텍스트: {alert.text}")
                                    alert.accept()
                                    print("DEBUG: 알림창 확인 완료")
                                except Exception as e:
                                    print(f"WARNING: 알림창 확인 실패 또는 없음: {e}")

                                return True

                            except Exception as e:
                                print(
                                    Colors.RED + f"❌ 할인 버튼 클릭 실패: {ticket_name} ({button_text}) / 예외: {e}" + Colors.ENDC)
                                return False


                        if park_id in [29218, 18996]:
                            print(Colors.BLUE + f"DEBUG: 18996 주차장 처리 시작 - ticket_name: {ticket_name}" + Colors.ENDC)
                            try:
                                ori_car_num = ori_car_num.replace(" ", "")  # 차량번호 공백 제거
                                print(Colors.BLUE + f"DEBUG: 처리할 차량번호: {ori_car_num}" + Colors.ENDC)

                                # 차량 정보 영역 확인
                                print(Colors.BLUE + "DEBUG: 차량 정보 영역 찾는 중..." + Colors.ENDC)
                                info_td = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, "//td[h3[contains(text(), '차량 정보')]]"))
                                )
                                text = info_td.text.strip()
                                print(Colors.BLUE + f"DEBUG: 차량 정보 영역 텍스트: {text[:200]}..." + Colors.ENDC)

                                # 차량번호 추출
                                site_car_num = None
                                for line in text.splitlines():
                                    if "차량번호:" in line:
                                        site_car_num = line.split("차량번호:")[1].strip()
                                        print(f"DEBUG: 사이트 표시 차량번호: {site_car_num}")
                                        break

                                if not site_car_num:
                                    print(Colors.RED + "❌ 차량번호 정보 찾기 실패 (29218/18996)" + Colors.ENDC)
                                    return False

                                # 유사 매칭
                                if ori_car_num == site_car_num or ori_car_num[-7:] == site_car_num[-7:] or ori_car_num[
                                                                                                           -6:] == site_car_num[
                                                                                                                   -6:]:
                                    print(Colors.GREEN + "차량번호 일치 확인 완료 (29218/18996)" + Colors.ENDC)
                                else:
                                    print(
                                        Colors.MARGENTA + f"차량번호 불일치 (입력: {ori_car_num}, 사이트: {site_car_num})" + Colors.ENDC)
                                    return False

                                # ticket_name → 버튼 ID 매핑
                                if ticket_name in ["평일 당일권","평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                                    btn_id = "BTN_종일권 (공유서비스)"
                                elif ticket_name == "휴일 당일권":
                                    btn_id = "BTN_주말권 (공유서비스)"
                                elif ticket_name in ["평일 3시간권", "휴일 3시간권"]:
                                    btn_id = "BTN_3시간권 (공유서비스)"
                                else:
                                    print(Colors.RED + f"❌ 정의되지 않은 ticket_name: {ticket_name}" + Colors.ENDC)
                                    return False

                                # 버튼 클릭
                                print(Colors.BLUE + f"DEBUG: 버튼 ID: {btn_id}" + Colors.ENDC)

                                # 페이지의 모든 버튼 확인
                                all_buttons = driver.find_elements(By.TAG_NAME, "input")
                                print(Colors.BLUE + f"DEBUG: 페이지의 모든 input 버튼 수: {len(all_buttons)}" + Colors.ENDC)
                                for i, btn in enumerate(all_buttons[:5]):  # 처음 5개만 출력
                                    print(Colors.BLUE + f"DEBUG: 버튼 {i+1} - ID: {btn.get_attribute('id')}, Value: {btn.get_attribute('value')}" + Colors.ENDC)

                                # 버튼이 존재하는지 먼저 확인
                                try:
                                    print(Colors.BLUE + f"DEBUG: 버튼 {btn_id} 찾는 중..." + Colors.ENDC)
                                    btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, btn_id)))
                                    print(Colors.GREEN + f"✅ 버튼 발견: {btn_id}" + Colors.ENDC)

                                    # 버튼이 클릭 가능한 상태인지 확인
                                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, btn_id)))

                                    # 스크롤하여 버튼을 화면에 보이게 함
                                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                                    Util.sleep(1)

                                    # JavaScript로 클릭
                                    driver.execute_script("arguments[0].click();", btn)
                                    print(Colors.GREEN + f"✅ 할인 버튼 클릭 성공: {btn_id}" + Colors.ENDC)

                                except Exception as e:
                                    print(Colors.RED + f"❌ 버튼 클릭 실패: {btn_id}, 오류: {e}" + Colors.ENDC)
                                    print(Colors.RED + f"DEBUG: 현재 페이지 URL: {driver.current_url}" + Colors.ENDC)
                                    return False

                                # Alert 처리
                                try:
                                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                                    alert = driver.switch_to.alert
                                    print(Colors.BLUE + f"알림창 텍스트: {alert.text}" + Colors.ENDC)
                                    alert.accept()
                                    print(Colors.GREEN + "✅ 알림창 확인 완료" + Colors.ENDC)
                                except Exception as e:
                                    print(Colors.YELLOW + f"⚠️ 알림창 처리 실패 또는 없음: {e}" + Colors.ENDC)

                                return True

                            except Exception as e:
                                print(Colors.RED + f"❌ 29218/18996 처리 중 오류: {e}" + Colors.ENDC)
                                return False

                        if park_id == 16159:
                            try:
                                ori_car_num = ori_car_num.replace(" ", "")  # 차량번호 공백 제거

                                # 차량 정보 영역이 나타날 때까지 대기
                                car_info_td = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, "//td[h3[contains(text(), '차량 정보')]]"))
                                )
                                text = car_info_td.text.strip()

                                # 차량번호 줄에서 실제 번호 추출
                                site_car_num = None
                                for line in text.splitlines():
                                    if "차량번호:" in line:
                                        site_car_num = line.split("차량번호:")[1].strip()
                                        print(f"DEBUG: 사이트 표시 차량번호: {site_car_num}")
                                        break

                                if not site_car_num:
                                    print(Colors.RED + "❌ 차량번호 정보를 찾을 수 없습니다 (16159)" + Colors.ENDC)
                                    return False

                                if ori_car_num == site_car_num or ori_car_num[-7:] == site_car_num[-7:] or ori_car_num[
                                                                                                           -6:] == site_car_num[
                                                                                                                   -6:]:
                                    print(Colors.GREEN + "차량번호 정확 또는 유사 일치 (16159)" + Colors.ENDC)
                                else:
                                    print(
                                        Colors.MARGENTA + f"차량번호 불일치 (입력: {ori_car_num}, 사이트: {site_car_num})" + Colors.ENDC)
                                    return False

                                # ticket_name 에 따라 버튼 ID 결정
                                if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                                    btn_id = "BTN_종일권 (일일권)"
                                elif ticket_name == "휴일 당일권":
                                    btn_id = "BTN_주말권 (일일권)"
                                else:
                                    print(Colors.RED + f"❌ 정의되지 않은 ticket_name: {ticket_name}" + Colors.ENDC)
                                    return False

                                # 버튼 존재 확인
                                print(Colors.BLUE + f"버튼 ID: {btn_id}" + Colors.ENDC)
                                btn = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.ID, btn_id))
                                )

                                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                                driver.execute_script("arguments[0].click();", btn)
                                print(Colors.GREEN + f"✅ 할인 버튼 클릭 성공: {btn_id}" + Colors.ENDC)

                                # Alert 처리
                                try:
                                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                                    alert = driver.switch_to.alert
                                    print(Colors.BLUE + f"알림창 텍스트: {alert.text}" + Colors.ENDC)
                                    alert.accept()
                                    print(Colors.GREEN + "✅ 알림창 확인 완료" + Colors.ENDC)
                                except Exception as e:
                                    print(Colors.YELLOW + f"⚠️ 알림창 처리 실패 또는 없음: {e}" + Colors.ENDC)

                                return True

                            except Exception as e:
                                print(Colors.RED + f"❌ 16159 할인 처리 실패: {e}" + Colors.ENDC)
                                return False

                        btn_item = web_info[WebInfo.btnItem]
                        if park_id not in [19492] and btn_item and btn_item != "-":
                            driver.find_element(By.ID, btn_item).click()

                        harin_script = get_har_in_script(park_id, ticket_name)
                        print(f"🎯 get_har_in_script({park_id}, {ticket_name}) → {harin_script}")
                        if not harin_script:
                            print("유효하지 않은 ticket_name 입니다.")  # 실패 메시지
                            return False  # 프로세스 종료 (더 진행 안 함)

                        # ✅ 할인 스크립트 실행 직전에 chk 강제 체크 추가
                        if park_id == 19325:
                            try:
                                chk_elem = WebDriverWait(driver, 3).until(
                                    EC.presence_of_element_located((By.ID, "chk")))
                                driver.execute_script("arguments[0].checked = true;", chk_elem)
                                print("✅ (재확인) 라디오 버튼 'chk' 강제 체크 완료 (19325)")
                                Util.sleep(0.3)
                            except Exception as e:
                                print(f"⚠️ (재확인) chk 체크 실패: {e}")

                        try:
                            if harin_script.startswith("BTN_"):
                                # ✅ 19174는 JavaScript로 클릭하고 Alert 처리
                                if park_id == 19174:
                                    try:
                                        btn_element = driver.find_element(By.ID, harin_script)
                                        # JavaScript로 클릭 (Alert가 나타나도 예외 발생 안 함)
                                        driver.execute_script("arguments[0].click();", btn_element)
                                        print(f"✅ 버튼 클릭 완료 (JavaScript): {harin_script}")
                                        
                                        # Alert 처리
                                        WebDriverWait(driver, 5).until(EC.alert_is_present())
                                        alert = driver.switch_to.alert
                                        alert_text = alert.text
                                        print(f"✅ Alert 텍스트: {alert_text}")
                                        alert.accept()
                                        print("✅ Alert 확인 완료 (19174)")
                                        
                                        # 페이지 전환 및 할인 승인 내역 테이블 로딩 대기
                                        Util.sleep(2)  # 페이지 전환 대기
                                        
                                        # ✅ 할인 승인 내역 테이블에 데이터가 실제로 추가되었는지 확인
                                        try:
                                            # "할인 승인 내역" 테이블의 tbody > tr 요소 확인
                                            wait_table = WebDriverWait(driver, 5)
                                            # 테이블이 로드될 때까지 대기
                                            table = wait_table.until(
                                                EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), '할인 승인 내역')]/following-sibling::table"))
                                            )
                                            
                                            # tbody 내부의 tr 요소 확인 (헤더 제외)
                                            rows = table.find_elements(By.XPATH, ".//tbody/tr[td]")
                                            
                                            if len(rows) > 0:
                                                # 데이터가 있는 경우, 승인 정보 컬럼 확인
                                                for row in rows:
                                                    cells = row.find_elements(By.TAG_NAME, "td")
                                                    if len(cells) >= 3:
                                                        approval_info = cells[2].text.strip()
                                                        print(f"✅ 할인 승인 내역 확인됨: {approval_info}")
                                                        return True
                                                
                                                print("✅ 할인 승인 내역 테이블에 데이터 있음")
                                                return True
                                            else:
                                                print("❌ 할인 승인 내역 테이블에 데이터 없음")
                                                return False
                                                
                                        except Exception as table_e:
                                            print(f"⚠️ 할인 승인 내역 테이블 확인 실패: {table_e}")
                                            return False
                                        
                                    except Exception as e:
                                        print(f"⚠️ 19174 Alert 처리 실패: {e}")
                                        return False
                                else:
                                    driver.find_element(By.ID, harin_script).click()

                                    # ✅ 버튼 클릭 직후 Alert 수동 처리
                                    try:
                                        WebDriverWait(driver, 5).until(EC.alert_is_present())
                                        alert = driver.switch_to.alert
                                        print(f"✅ Alert 텍스트: {alert.text}")
                                        alert.accept()
                                        print("✅ Alert 확인 완료")
                                    except Exception as e:
                                        print(f"⚠️ Alert 처리 실패 또는 없음: {e}")


                            else:
                                driver.execute_script(harin_script)

                            print("할인 스크립트 실행 완료")
                            return check_discount_alert(driver, park_id)
                        except UnexpectedAlertPresentException:
                            try:
                                alert = driver.switch_to.alert
                                alert_text = alert.text
                                print(f"[ERROR 처리 중 Alert 발생] Alert Text: {alert_text}")
                                alert.accept()
                                print("✅ Alert 확인 완료 (UnexpectedAlertPresentException 처리)")
                                
                                # ✅ 19174의 경우 Alert 확인 후 할인 승인 내역 확인
                                if park_id == 19174:
                                    Util.sleep(2)  # 페이지 전환 대기
                                    
                                    # ✅ 할인 승인 내역 테이블에 데이터가 실제로 추가되었는지 확인
                                    try:
                                        # "할인 승인 내역" 테이블의 tbody > tr 요소 확인
                                        wait_table = WebDriverWait(driver, 5)
                                        # 테이블이 로드될 때까지 대기
                                        table = wait_table.until(
                                            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), '할인 승인 내역')]/following-sibling::table"))
                                        )
                                        
                                        # tbody 내부의 tr 요소 확인 (헤더 제외)
                                        rows = table.find_elements(By.XPATH, ".//tbody/tr[td]")
                                        
                                        if len(rows) > 0:
                                            # 데이터가 있는 경우, 승인 정보 컬럼 확인
                                            for row in rows:
                                                cells = row.find_elements(By.TAG_NAME, "td")
                                                if len(cells) >= 3:
                                                    approval_info = cells[2].text.strip()
                                                    print(f"✅ 할인 승인 내역 확인됨: {approval_info}")
                                                    return True
                                            
                                            print("✅ 할인 승인 내역 테이블에 데이터 있음")
                                            return True
                                        else:
                                            print("❌ 할인 승인 내역 테이블에 데이터 없음")
                                            return False
                                            
                                    except Exception as table_e:
                                        print(f"⚠️ 할인 승인 내역 테이블 확인 실패: {table_e}")
                                        return False
                                else:
                                    return False
                            except NoAlertPresentException:
                                pass
                            return False
                        except Exception as e:
                            print(f"할인 스크립트 실행 중 오류 발생: {e}")
                            return False

                return False
            else:
                print(Colors.RED + f"DEBUG: ParkUtil.first_access가 False를 반환했습니다. 재접속으로 간주됨." + Colors.ENDC)
                print(Colors.RED + f"DEBUG: else 블록 실행 중..." + Colors.ENDC)
                print(Colors.BLUE + f"DEBUG: ParkUtil.check_search({park_id}, driver) 확인 중..." + Colors.ENDC)
                check_search_result = ParkUtil.check_search(park_id, driver)
                print(Colors.BLUE + f"DEBUG: ParkUtil.check_search 결과: {check_search_result}" + Colors.ENDC)
                
                if check_search_result:
                    print(Colors.BLUE + f"DEBUG: ParkUtil.check_same_car_num({park_id}, {ori_car_num}, driver) 확인 중..." + Colors.ENDC)
                    check_same_car_result = ParkUtil.check_same_car_num(park_id, ori_car_num, driver)
                    print(Colors.BLUE + f"DEBUG: ParkUtil.check_same_car_num 결과: {check_same_car_result}" + Colors.ENDC)
                    
                    if check_same_car_result:
                        # 18996 주차장 특별 처리 로직을 여기에 추가
                        print(Colors.BLUE + f"DEBUG: 18996 주차장 특별 처리 로직 실행" + Colors.ENDC)
                        # 기존의 18996 처리 로직을 여기에 복사
                    else:
                        print(Colors.RED + f"DEBUG: ParkUtil.check_same_car_num이 False를 반환했습니다." + Colors.ENDC)
                        return False
                else:
                    print(Colors.RED + f"DEBUG: ParkUtil.check_search가 False를 반환했습니다." + Colors.ENDC)
                    return False

        else:
            print(Colors.BLUE + "high현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False


def process_highcity_2936x_discount(driver, ticket_name, park_id):
    """
    29364 / 29361 / 29362 전용 할인 처리 공통 로직
    """
    # 29362는 제휴당일권 사용
    if park_id == 29362:
        ticket_name_map = {
            "심야권": ["심야권"],
            "평일 3시간권": ["평일3시간권", "평일 3시간권"],
            "평일3시간권": ["평일3시간권", "평일 3시간권"],
            "평일 당일권": ["제휴평일당일권"],
            "평일당일권": ["제휴평일당일권"],
            "평일 당일권(월)": ["제휴평일당일권"],
            "평일 당일권(화)": ["제휴평일당일권"],
            "평일 당일권(수)": ["제휴평일당일권"],
            "평일 당일권(목)": ["제휴평일당일권"],
            "평일 당일권(금)": ["제휴평일당일권"],
            "휴일 4시간권": ["휴일4시간권", "휴일 4시간권"],
            "휴일4시간권": ["휴일4시간권", "휴일 4시간권"],
            "휴일 당일권": ["제휴휴일당일권"],
            "휴일당일권": ["제휴휴일당일권"],
        }
    else:
        # 29364, 29361은 기존 매핑 사용
        ticket_name_map = {
            "심야권": ["심야권"],
            "평일 3시간권": ["평일3시간권", "평일 3시간권"],
            "평일3시간권": ["평일3시간권", "평일 3시간권"],
            "평일 당일권": ["평일당일권", "평일 당일권"],
            "평일당일권": ["평일당일권", "평일 당일권"],
            "휴일 4시간권": ["휴일4시간권", "휴일 4시간권"],
            "휴일4시간권": ["휴일4시간권", "휴일 4시간권"],
            "휴일 당일권": ["휴일당일권", "휴일 당일권"],
            "휴일당일권": ["휴일당일권", "휴일 당일권"],
        }

    candidates = ticket_name_map.get(ticket_name)
    if not candidates:
        print(Colors.YELLOW + f"⚠️ {park_id}에서 처리할 수 없는 ticket_name: {ticket_name}" + Colors.ENDC)
        return False

    wait_ticket = WebDriverWait(driver, 10)
    coupon_element = None

    for candidate in candidates:
        normalized = candidate.strip()
        try:
            coupon_element = wait_ticket.until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     f"//div[@class='discount-coupon-item']//span[@class='coupon-type' and normalize-space(text())='{normalized}']/ancestor::div[@class='discount-coupon-item']")
                )
            )
            if coupon_element:
                print(Colors.GREEN + f"✅ 할인권 항목 찾음: {normalized}" + Colors.ENDC)
                break
        except Exception:
            continue

    if not coupon_element:
        print(Colors.RED + f"❌ 할인권 항목 찾기 실패: {ticket_name}" + Colors.ENDC)
        return False

    try:
        # plus 버튼 클릭
        plus_button = coupon_element.find_element(By.XPATH, ".//button[contains(@class, 'plus-button')]")
        driver.execute_script("arguments[0].click();", plus_button)
        print(Colors.GREEN + "✅ 할인권 plus 버튼 클릭 완료" + Colors.ENDC)
        Util.sleep(1)

        # 할인하기 버튼 클릭
        discount_button = wait_ticket.until(
            EC.element_to_be_clickable((By.XPATH,
                                         "//div[@class='reduce-parking-fees-footer']//button[contains(@class, 'discount-button')]//span[text()='할인하기']/ancestor::button"))
        )
        driver.execute_script("arguments[0].click();", discount_button)
        print(Colors.GREEN + "✅ 할인하기 버튼 클릭 완료" + Colors.ENDC)
        Util.sleep(1.5)

        # 확인 모달 처리
        print(Colors.BLUE + "DEBUG: 할인 확인 모달 찾는 중..." + Colors.ENDC)
        Util.sleep(2)
        wait_modal = WebDriverWait(driver, 10)
        modal_container = wait_modal.until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='modal-container']"))
        )

        is_visible = driver.execute_script(
            "var style = window.getComputedStyle(arguments[0]); return style.display !== 'none' && style.visibility !== 'hidden';",
            modal_container
        )

        if not is_visible:
            print(Colors.YELLOW + "⚠️ 모달이 숨겨져 있음, 추가 대기..." + Colors.ENDC)
            Util.sleep(1)

        try:
            wait_modal.until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='modal-container']//div[contains(text(), '할인을')]"))
            )
        except Exception:
            try:
                wait_modal.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='modal-container']//div[contains(text(), '등록하시겠습니까')]"))
                )
            except Exception:
                wait_modal.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='modal-container']//div[@class='inform-message']"))
                )

        confirm_button = wait_modal.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='modal-container']//button[contains(@class, 'modal-submit-button')]"))
        )
        driver.execute_script("arguments[0].click();", confirm_button)
        print(Colors.GREEN + "✅ 할인 확인 모달 '확인' 버튼 클릭 완료" + Colors.ENDC)
        Util.sleep(4)

        # 로그아웃 처리
        print(Colors.BLUE + "DEBUG: 로그아웃 처리 시작" + Colors.ENDC)
        wait_logout = WebDriverWait(driver, 10)

        menu_button = wait_logout.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='am-header']//button[contains(@class, 'am-image-button')]//i[contains(@class, 'i-ico-hamburger')]/ancestor::button[1]"))
        )
        driver.execute_script("arguments[0].click();", menu_button)
        print(Colors.GREEN + "✅ 햄버거 메뉴 버튼 클릭 완료" + Colors.ENDC)
        Util.sleep(1.5)

        profile_button = wait_logout.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@id='my' and contains(@class, 'am-image-button')]"))
        )
        driver.execute_script("arguments[0].click();", profile_button)
        print(Colors.GREEN + "✅ 프로필 버튼 클릭 완료" + Colors.ENDC)
        Util.sleep(1.5)

        logout_button = wait_logout.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='my-control']//button[contains(@class, 'am-button')]//span[text()='로그아웃']/ancestor::button[1]"))
        )
        driver.execute_script("arguments[0].click();", logout_button)
        print(Colors.GREEN + "✅ 로그아웃 버튼 클릭 완료" + Colors.ENDC)
        Util.sleep(1.5)

        modal_text = wait_logout.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '계정을 로그아웃')]"))
        )
        print(Colors.BLUE + "DEBUG: 로그아웃 확인 모달 감지됨" + Colors.ENDC)

        confirm_logout_button = wait_logout.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='modal-container']//button[contains(@class, 'modal-submit-button')]"))
        )
        driver.execute_script("arguments[0].click();", confirm_logout_button)
        print(Colors.GREEN + "✅ 로그아웃 확인 모달 '예' 버튼 클릭 완료" + Colors.ENDC)
        Util.sleep(2)

        print(Colors.GREEN + "✅ 할인 처리 완료 - True 반환" + Colors.ENDC)
        return True

    except Exception as e:
        print(Colors.RED + f"❌ {park_id} 할인 처리 실패: {e}" + Colors.ENDC)
        return False
