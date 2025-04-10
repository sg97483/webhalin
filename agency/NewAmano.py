 # -*- coding: utf-8 -*-
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymysql
import Util
import Colors
from park import ParkUtil, ParkType
import WebInfo
import time

# DB 연결 정보
DB_CONFIG = {
    'host': '49.236.134.172',
    'port': 3306,
    'user': 'root',
    'password': '#orange8398@@',
    'db': 'parkingpark',
    'charset': 'utf8'
}

# 로그인 버튼 및 네비게이션 버튼 XPath
btn_confirm_xpath = "/html/body/mhp-console/div/div[2]/div/div/main/div[2]/div[1]/div[2]/div/div/div/div[2]/div[1]/div/div/div[2]/button[2]"
side_nav_xpath = "/html/body/div[3]/table/tbody/tr/td[2]/button"

# 대상 URL 리스트
TARGET_URLS = ["https://a14926.parkingweb.kr/login","https://a05203.parkingweb.kr","http://112.216.125.10/discount/registration"
    ,"https://a18822.pweb.kr","https://a14041.parkingweb.kr/","https://a18147.pweb.kr/",
               "https://a12647.parkingweb.kr/","https://www.amanopark.co.kr/"
    ,"https://a093.parkingweb.kr/","https://a17687.pweb.kr/","http://112.217.102.42/"
    ,"http://a15820.parkingweb.kr/","https://a02248.parkingweb.kr/login","http://www.amanopark.co.kr","http://a03428.parkingweb.kr"
,"http://1.225.4.44","http://59.15.76.103","http://121.160.237.7","https://a17389.parkingweb.kr/"
    ,"https://a04088.parkingweb.kr","http://112.220.251.2","http://211.217.212.176/"
    ,"https://a15061.parkingweb.kr/discount/registration","https://a18134.pweb.kr/login"
,"http://175.114.59.25/discount/registration","http://211.202.87.149",
               "http://211.244.148.17/","https://a15337.parkingweb.kr","http://121.134.61.62/login"
    ,"http://a05388.parkingweb.kr","http://175.195.124.15","https://a14705.parkingweb.kr/login"
    ,"https://a13687.parkingweb.kr/login","https://s1148.parkingweb.kr/login"
    ,"https://s1151.parkingweb.kr:6650/login","https://a14417.parkingweb.kr/login","http://123.214.186.154"
,"https://a17902.pweb.kr","https://a15891.parkingweb.kr"
               ]

def get_park_ids_by_urls(target_urls):
    """
    DB에서 특정 URL 리스트와 매칭된 park_id를 가져옴.
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        curs = conn.cursor()
        format_strings = ','.join(['%s'] * len(target_urls))
        sql = f"SELECT parkId FROM T_PARKING_WEB WHERE url IN ({format_strings})"
        curs.execute(sql, target_urls)
        rows = curs.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"DB 쿼리 실패: {e}")
        return []
    finally:
        if conn:
            conn.close()

# DB에서 park_id 동적 조회
dynamic_park_ids = get_park_ids_by_urls(TARGET_URLS)

# 🔍 디버깅 코드: `parkId`가 올바르게 로드되는지 확인
#print(f"DEBUG: {TARGET_URLS}에 대한 park_id 조회 결과: {dynamic_park_ids}")

# 🚨 TARGET_URLS가 park_id 리스트로 바뀌었으면 원래 URL 리스트로 복구
if isinstance(TARGET_URLS, list) and all(isinstance(url, int) for url in TARGET_URLS):
    #print("🚨 DEBUG: TARGET_URLS가 park_id 리스트로 변경됨! 원래 URL 리스트로 복구")
    TARGET_URLS = ["https://a14926.parkingweb.kr/login", "https://a05203.parkingweb.kr",
                   "http://112.216.125.10/discount/registration","https://a18822.pweb.kr",
                   "https://a14041.parkingweb.kr/","https://a18147.pweb.kr/","https://a12647.parkingweb.kr/"
        ,"https://www.amanopark.co.kr/","https://a093.parkingweb.kr/"
        ,"https://a17687.pweb.kr/","http://112.217.102.42/"
        ,"http://a15820.parkingweb.kr/","https://a02248.parkingweb.kr/login","http://www.amanopark.co.kr"
                   ,"http://a03428.parkingweb.kr","http://1.225.4.44","http://59.15.76.103"
        ,"http://121.160.237.7","https://a17389.parkingweb.kr/","https://a04088.parkingweb.kr"
        ,"http://112.220.251.2","http://211.217.212.176/"
        ,"https://a15061.parkingweb.kr/discount/registration","https://a18134.pweb.kr/login"
                   ,"http://175.114.59.25/discount/registration","http://211.202.87.149"
        ,"http://211.244.148.17/","https://a15337.parkingweb.kr","http://121.134.61.62/login"
        ,"http://a05388.parkingweb.kr","http://175.195.124.15","https://a14705.parkingweb.kr/login"
        ,"https://a13687.parkingweb.kr/login","https://s1148.parkingweb.kr/login"
        ,"https://s1151.parkingweb.kr:6650/login","https://a14417.parkingweb.kr/login"
        ,"http://123.214.186.154","https://a17902.pweb.kr","https://a15891.parkingweb.kr"]

# mapIdToWebInfo 동적 생성
mapIdToWebInfo = {park_id: ["userId", "userPwd", "//*[@id='btnLogin']", "schCarNo", "//*[@id='sForm']/input[3]"]
                  for park_id in dynamic_park_ids}

# 🔍 `mapIdToWebInfo`가 정상적으로 생성되었는지 확인
#print(f"DEBUG: mapIdToWebInfo={mapIdToWebInfo}")

def enter_user_id(driver, user_id):
    """
    로그인 페이지의 ID 입력 필드가 로드될 때까지 대기한 후 값을 입력
    """
    try:
        id_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='userId']"))
        )
        driver.execute_script("arguments[0].removeAttribute('readonly')", id_field)
        driver.execute_script("arguments[0].removeAttribute('disabled')", id_field)
        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                              id_field, user_id)
        print(f"DEBUG: 아이디 '{user_id}' 입력 성공")

    except TimeoutException:
        print("ERROR: ID 입력 필드를 찾을 수 없음.")
    except Exception as e:
        print(f"ERROR: ID 입력 중 예외 발생: {e}")

def handle_alert(driver):
    """
    로그인 과정에서 Alert 창이 뜰 경우 자동으로 닫음.
    """
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"DEBUG: Alert 발견 - {alert.text}")
        alert.accept()
        print("DEBUG: Alert 닫기 완료")
    except TimeoutException:
        print("DEBUG: Alert이 감지되지 않음")

def close_vehicle_number_popup(driver):
    """
    차량번호 입력 후 뜨는 '2자리 이상 입력하세요' 팝업을 감지하고 자동으로 닫음.
    """
    try:
        popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "modal-window"))
        )
        print("DEBUG: 차량번호 입력 오류 팝업 감지됨.")

        # "OK" 버튼 클릭
        ok_button = popup.find_element(By.XPATH, ".//a[@class='modal-btn']")
        ok_button.click()
        print("DEBUG: '차량번호 2자리 이상 입력' 팝업 닫기 완료.")

        # 팝업이 완전히 사라질 때까지 대기
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element((By.ID, "modal-window"))
        )
        print("DEBUG: 팝업이 완전히 사라짐.")

    except TimeoutException:
        print("DEBUG: 차량번호 입력 팝업이 감지되지 않음.")  # 팝업이 없으면 문제없음.




def handle_no_search_results_popup(driver, park_id):
    """
    차량 검색 후 '검색 결과가 없습니다.' 팝업을 감지하고 OK 버튼을 클릭한 뒤 로그아웃.
    """
    try:
        popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-box"))
        )
        print("DEBUG: '검색 결과 없음' 팝업 감지됨.")

        # "OK" 버튼 클릭
        ok_button = popup.find_element(By.XPATH, ".//a[@class='modal-btn']")
        ok_button.click()
        print("DEBUG: '검색 결과 없음' 팝업 OK 버튼 클릭 완료.")

        # 팝업이 완전히 닫힐 때까지 대기
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element((By.CLASS_NAME, "modal-box"))
        )
        print("DEBUG: '검색 결과 없음' 팝업이 닫혔음.")

        # 🚀 로그아웃 버튼 클릭
        try:
            logout_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, side_nav_xpath))
            )
            logout_button.click()
            print("DEBUG: 로그아웃 버튼 클릭 완료.")
        except TimeoutException:
            print("ERROR: 로그아웃 버튼을 찾을 수 없음.")

        return False  # 🚀 검색 결과가 없으면 종료

    except TimeoutException:
        print("DEBUG: '검색 결과 없음' 팝업이 감지되지 않음.")
        return True  # 🚀 검색 성공했으면 할인 진행



def enter_car_number(driver, car_number_last4, park_id):
    """
    차량번호 뒤 4자리를 입력하고 '검색' 버튼 클릭.
    """
    try:
        close_vehicle_number_popup(driver)  # 차량번호 입력 전 팝업 닫기

        # 차량번호 입력 필드 찾기
        input_field = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "schCarNo"))
        )
        input_field.clear()
        print("DEBUG: 차량번호 입력 필드 초기화 완료.")

        # 차량번호 입력
        input_field.send_keys(car_number_last4)
        print(f"DEBUG: 차량번호 '{car_number_last4}' 입력 완료.")

        # park_id별 검색 버튼 처리
        if park_id in [18938, 18577, 19906, 19258, 19239, 19331,19077,16096,45010,14618,19253]:  # 특정 park_id 전용 처리
            search_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@class='btnS1_1 btn' and @value='검색']"))
            )
        else:
            search_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='sForm']/input[3]"))
            )

        search_button.click()
        print("DEBUG: 차량번호 검색 버튼 클릭 완료.")

        # "검색 결과가 없습니다." 팝업 확인 후 처리 (✅ park_id 추가)
        if not handle_no_search_results_popup(driver, park_id):
            print("DEBUG: 차량 검색 실패, 할인 진행 중단.")
            return False  # 🚨 검색 실패 시 즉시 중단

        return True

    except TimeoutException:
        print(f"ERROR: 차량번호 입력 중 TimeoutException 발생. park_id={park_id}")
        return False  # 🚨 입력 필드를 찾지 못하면 즉시 실패 반환




def handle_notice_popup_and_redirect(driver, park_id):
    """
    park_id == 29118 일 때 로그인 후 '안내' 팝업 닫고, 할인 페이지로 이동하는 함수
    """
    if park_id != 29118:
        return  # 다른 주차장은 처리하지 않음

    try:
        # 팝업 상위 div (modal-window) 감지
        popup_window = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "modal-window"))
        )
        print("DEBUG: '안내' 팝업 (modal-window) 감지됨.")

        # 내부 '닫기' 버튼 찾기
        close_button = popup_window.find_elements(By.CLASS_NAME, "modal-btn")[1]  # 두 번째 버튼이 '닫기'
        close_button.click()
        print("DEBUG: '안내' 팝업 닫기 버튼 클릭 완료.")

        # 팝업이 사라질 때까지 대기
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "modal-window"))
        )
        print("DEBUG: '안내' 팝업 사라짐.")

    except TimeoutException:
        print("DEBUG: '안내' 팝업이 감지되지 않음. 할인 페이지로 바로 이동 시도.")

    # 팝업 유무와 관계없이 할인 페이지 이동
    try:
        discount_url = "https://a18822.pweb.kr/discount/registration"
        driver.get(discount_url)
        print("DEBUG: 할인 페이지로 이동 완료.")

        # 할인 페이지 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='schCarNo']"))
        )
        print("DEBUG: 할인 페이지 로딩 완료.")
    except TimeoutException:
        print("ERROR: 할인 페이지 로딩 실패.")



def handle_popup_and_go_discount(driver, park_id):
    """
    특정 park_id에 따라 팝업 닫기와 할인 페이지 이동 처리
    """
    park_popup_and_discount_url = {
        19335: "http://112.216.125.10/discount/registration",
        19934: "https://a17687.pweb.kr/discount/registration",
        19253: "https://175.195.124.15/discount/registration",
        19887: "https://a15820.parkingweb.kr/discount/registration",
        19842: "https://a14417.parkingweb.kr/discount/registration",
        19903: "https://s1151.parkingweb.kr:6650/discount/registration",
        19941: "https://a17902.pweb.kr/discount/registration"

    }

    if park_id not in park_popup_and_discount_url:
        print(f"DEBUG: park_id={park_id}는 별도 팝업/할인 페이지 처리 대상 아님.")
        return

    # 공통 팝업 닫기 로직
    try:
        popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-box"))
        )
        print(f"DEBUG: park_id={park_id} 로그인 후 안내 팝업 감지됨.")

        close_button = popup.find_elements(By.CLASS_NAME, "modal-btn")[-1]
        close_button.click()
        print(f"DEBUG: park_id={park_id} 팝업 '닫기' 버튼 클릭 완료.")

        WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CLASS_NAME, "modal-box")))
        print(f"DEBUG: park_id={park_id} 팝업이 완전히 사라짐.")
    except TimeoutException:
        print(f"DEBUG: park_id={park_id} 로그인 후 안내 팝업이 감지되지 않음.")  # 없을 수도 있음

    # 할인 페이지 이동
    discount_url = park_popup_and_discount_url[park_id]
    try:
        driver.get(discount_url)
        print(f"DEBUG: park_id={park_id} 할인 페이지로 이동: {discount_url}")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='schCarNo']"))
        )
        print(f"DEBUG: park_id={park_id} 할인 페이지 로딩 완료.")
    except TimeoutException:
        print(f"ERROR: park_id={park_id} 할인 페이지 로딩 실패.")



def click_discount_menu(driver):
    """
    park_id = 19335 에서 '할인' 메뉴 클릭
    """
    try:
        discount_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '할인')]"))
        )
        discount_button.click()

    except TimeoutException:
        print("ERROR: '할인' 버튼을 찾을 수 없음.")


def process_ticket_and_logout(driver, button_id, park_id):
    """
    할인권 클릭 및 로그아웃까지 처리하는 함수
    """
    try:
        driver.find_element(By.ID, button_id).click()
        print(f"DEBUG: 할인권 버튼(id={button_id}) 클릭 완료.")
        WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
        print("DEBUG: 할인권 적용 확인 알림 닫기 완료.")
    except TimeoutException:
        print("DEBUG: 할인권 적용 알림 없음 (정상일 수 있음).")
    except Exception as e:
        print(f"ERROR: 할인권 클릭 중 예외 발생: {e}")
        return False  # 🚨 실패로 처리

    # 팝업 처리
    try:
        popup = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-box"))
        )
        popup.find_element(By.XPATH, ".//a[@class='modal-btn']").click()
        WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CLASS_NAME, "modal-box")))
        print("DEBUG: 할인 이후 팝업 닫기 완료.")
    except TimeoutException:
        print("DEBUG: 할인 이후 팝업 감지되지 않음.")

    # 🚨 주차장에 따른 로그아웃 분기
    return logout(driver, park_id)


def enter_password(driver, user_password, park_id):
    """
    비밀번호 입력 처리 (특정 park_id에 따라 다름)
    """
    try:
        # 19489, 18938 전용
        if park_id in [19489, 18938, 19906,19258,19239,19331,19077,16096,45010,14618,19253]:
            print(f"DEBUG: {park_id} 전용 비밀번호 필드 탐색")
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "userPwd"))
            )

        # 18577 전용
        elif park_id == 18577:
            print("DEBUG: 18577 전용 비밀번호 필드 탐색 (class='input')")
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='userPwd']"))
            )

        # 일반 (ID 기반)
        else:
            print("DEBUG: 일반 비밀번호 필드 탐색")
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "userPwd"))
            )

        # 속성 제거 (존재할 때만)
        driver.execute_script(
            "if(arguments[0].hasAttribute('readonly')) arguments[0].removeAttribute('readonly');",
            password_field
        )
        driver.execute_script(
            "if(arguments[0].hasAttribute('disabled')) arguments[0].removeAttribute('disabled');",
            password_field
        )

        # 비밀번호 값 입력
        password_field.clear()
        password_field.send_keys(user_password)
        print("DEBUG: 비밀번호 입력 성공")
        return True

    except Exception as e:
        print(f"ERROR: 비밀번호 입력 실패: {e}")
        return False


def wait_and_click_discount_button(driver, button_id):
     """
     18938 전용 - 차량 검색 후 버튼 대기 후 클릭
     """
     try:
         print(f"DEBUG: 18938 전용 할인 버튼 대기 시작 (id={button_id})")

         # 최대 10초 대기 (버튼이 나타날 때까지)
         button = WebDriverWait(driver, 10).until(
             EC.element_to_be_clickable((By.ID, button_id))
         )
         print(f"DEBUG: 할인 버튼(id={button_id}) 활성화 확인")

         button.click()
         print(f"DEBUG: 할인 버튼(id={button_id}) 클릭 완료")
         return True

     except TimeoutException:
         print(f"ERROR: 할인 버튼(id={button_id})을 찾을 수 없음.")
         return False


def search_car_number_and_wait_discount(driver, car_number_last4, discount_button_id, park_id):
    """
    18938 전용: 차량번호 검색 후 할인권 버튼이 나타날 때까지 대기
    """
    try:
        close_vehicle_number_popup(driver)  # 팝업 닫기

        # 차량번호 입력 필드
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "schCarNo"))
        )
        input_field.clear()
        print("DEBUG: 차량번호 입력 필드 초기화 완료.")
        input_field.send_keys(car_number_last4)
        print(f"DEBUG: 차량번호 '{car_number_last4}' 입력 완료.")

        # 검색 버튼 클릭
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='sForm']/input[3]"))
        )
        search_button.click()
        print("DEBUG: 차량번호 검색 버튼 클릭 완료.")

        # "검색 결과가 없습니다." 팝업 감지
        if not handle_no_search_results_popup(driver,park_id):
            print("DEBUG: 차량 검색 결과 없음으로 종료.")
            return False

        # 🔑 할인권 버튼이 나타날 때까지 대기
        print(f"DEBUG: 할인권 버튼(id={discount_button_id}) 나타날 때까지 대기 중...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, discount_button_id))
        )
        print(f"DEBUG: 할인권 버튼(id={discount_button_id}) 감지 완료.")
        return True

    except Exception as e:
        print(f"ERROR: 차량 검색 또는 할인권 대기 중 오류: {e}")
        return False

def enter_memo_for_18577(driver):
    """
    18577 전용 - 메모란에 '파킹박' 입력
    """
    try:
        memo_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "memo"))
        )
        print("DEBUG: 메모 필드(memo) 감지됨.")

        # 값 설정
        memo_field.clear()
        memo_field.send_keys("파킹박")
        print("DEBUG: 메모 필드에 '파킹박' 입력 완료.")
        return True
    except TimeoutException:
        print("ERROR: 메모 필드(memo)를 찾을 수 없음.")
        return False


def handle_ticket(driver, park_id, ticket_name, entry_day_of_week=None):
    """
    주차장 및 주차권에 따른 할인권 처리
    entry_day_of_week: 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' 형식
    """
    # 전체 할인권 매핑
    ticket_map = {
        19892: {"평일 심야권": "15", "주말 심야권": "15", "휴일 당일권": "8"},
        19489: {"평일1일권": "8", "주말1일권": "10", "평일 심야권": "9"},
        19130: {"평일1일권": "14", "평일 심야권": "15"},
        19335: {"평일1일권": "6", "평일 심야권": "15"},
        19210: {"평일1일권": "3", "주말1일권": "5", "심야권": "4"},
        19887: {"평일 당일권": "13", "주말 당일권": "14", "심야권": "15", "4시간권": "10", "6시간권": "11"},
        18577: {"평일1일권(화~금)": "838", "주말1일권": "5"},
        18945: {"평일 당일권": "19", "휴일 당일권": "16", "평일 심야권": "18"},
        19934: {"평일12시간권": "7", "주말당일권": "6", "심야권": "8"},  # 심야권 분기 처리
        19258: {"평일1일권": "15", "주말1일권": "15", "평일 심야권": "14"},
        19444: {"평일 1일권": "17", "평일 6시간권": "17", "주말1일권": "17", "평일 저녁권": "42"},
        18938: {"평일1일권": "778", "주말1일권": "778", "심야권": "780", "평일 3시간권": "781"},
        19906: {"평일3시간권": "21", "주말1일권": "22", "공휴일권": "22"},
        29122: {"3시간권": "9", "평일 심야권": "13", "주말1일권(일, 공휴일)": "12", "주말1일권(토요일)": "12"},
        19331: {"평일1일권": "7"},
        19239: {"평일1일권": "8", "평일 심야권": "8"},
        19334: {"평일1일권": "8", "토요일권": "8"},
        19391: {"평일1일권": "9", "주말1일권": "9"},
        19858: {"평일1일권": "4", "주말1일권": "4"},
        19869: {"평일1일권": "9", "주말1일권": "9"},
        19941: {"평일당일권": "15", "휴일당일권": "15", "심야권": "18", "3시간권": "16"},
        19842: {"평일 2시간권": "13", "평일 4시간권": "18", "평일 6시간권": "19", "심야권": "20", "평일 당일권": "12", "주말 당일권": "14"},
        19903: {"평일4시간권": "9", "평일 당일권": "13", "주말1일권": "11"},
        19253: {"평일1일권": "15", "주말1일권": "16", "평일 2시간권": "13", "평일 4시간권": "14", "주말 2시간권": "13"},
        16096: {"평일1일권": "734", "토요일 12시간권": "73", "3시간권": "372"},
        19820: {"평일1일권(월)": "15", "평일1일권(화)": "15", "평일1일권(수~금)": "15"},
        19437: {"평일1일권": "9", "주말1일권": "10", "심야권": "11"},
        19935: {"평일 2시간권": "5", "평일 4시간권": "6"},
        19904: {"평일4시간권": "5", "주말 당일권": "6"},
        19376: {"주말1일권": "20", "심야권": "13"},
        45010: {"평일1일권": "851", "심야권": "10", "2시간권": "850"},
        19899: {"평일 3시간권": "7", "평일 당일권": "8", "토요일 2시간권": "17"},
        19453: {"휴일 당일권": "8", "평일 심야권": "12", "휴일 심야권": "12"},
        14618: {"평일 16시간권(기계식,승용)": "13", "휴일 16시간권(기계식,승용)": "13", "평일 당일권(자주식)": "19"},
        19077: {"평일1일권": "36", "주말1일권": "36", "심야권": "35", "주말 3시간권": "37"},
        29105: {"평일 2시간권": "7", "평일 3시간권": "8", "평일 당일권": "9", "평일 심야권": "13", "주말 당일권": "9"},
        19250: {"평일 6시간권": "18", "평일 당일권(월,화)": "18", "평일 당일권(수~금)": "18", "금토 2일연박권": "44", "주말 당일권(일요일)": "18", "주말 당일권(토요일)": "18", "평일 심야권": "19"},
        19852: {"평일 당일권": "14"},
        19920: {"평일 당일권": "6"},
        29118: {"평일 1일권": "11", "주말 1일권(토요일)": "11", "3시간권": "6", "평일 오후권": "19", "평일 심야권(월~목)": "17"},
        19954: {"평일 당일권": "4", "휴일 당일권": "4", "평일 6시간권": "7", "평일 심야권": "9"}
    }

    # ✅ 45010 전용 메모 입력
    if park_id == 45010:
        try:
            memo_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "memo"))
            )
            memo_field.clear()
            memo_field.send_keys("파킹박")
            print("DEBUG: 45010 메모 입력 완료")
        except TimeoutException:
            print("ERROR: 45010 메모 필드 찾기 실패")
            return False

    # ✅ 19820 전용 처리ddddd
    if park_id == 19820:
        if ticket_name in ["평일1일권(월)", "평일1일권(화)", "평일1일권(수~금)"]:
            button_id = "15"  # 종일권(평일) 버튼의 id
        else:
            print(f"ERROR: park_id=19820, ticket_name={ticket_name} 은 유효하지 않음.")
            return False


    # ✅ 19934 심야권 요일 분기 처리
    if park_id == 19934 and ticket_name == "심야권":
        button_id = "9" if entry_day_of_week in ["Fri", "Sat"] else "8"
        print(f"DEBUG: 19934 심야권 - {entry_day_of_week} 요일로 버튼 id={button_id} 선택")
    else:
        if park_id not in ticket_map or ticket_name not in ticket_map[park_id]:
            print(f"ERROR: No matching ticket found for park_id={park_id}, ticket_name={ticket_name}")
            return False
        button_id = ticket_map[park_id][ticket_name]

    if park_id == 16096:
        button_id = ticket_map[park_id][ticket_name]  # 예: "73"
        try:
            print(f"DEBUG: 16096 - 할인권 버튼 로딩 대기 시작 (id={button_id})")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, button_id))
            )
            print(f"DEBUG: 16096 - 할인권 버튼(id={button_id}) 로딩 완료")
        except TimeoutException:
            print(f"ERROR: 16096 - 할인권 버튼(id={button_id}) 로딩 실패")
            return False



    # ✅ 18577 메모 필드 입력
    if park_id == 18577:
        try:
            memo_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "memo"))
            )
            memo_field.clear()
            memo_field.send_keys("파킹박")
            print("DEBUG: 18577 메모 입력 완료")
        except TimeoutException:
            print("ERROR: 18577 메모 필드 찾기 실패")
            return False

    if park_id in [18938, 45010]:
        print("DEBUG: 18938 전용 할인 로직 진행 중...")
        if not search_car_number_and_wait_discount(driver, driver.car_number_last4, button_id, park_id):
            return False
        return wait_and_click_discount_button(driver, button_id)  # 🚨 여기서 종료!

    # 🚨 차량번호 입력 실패 시 즉시 중단 (들여쓰기 오류 수정)
    #if not enter_car_number(driver, driver.car_number_last4, park_id):
    #    print("ERROR: 차량번호 검색 실패로 할인 중단.")
    #    return False

    # ✅ 일반적인 할인 버튼 클릭 및 로그아웃 처리
    return process_ticket_and_logout(driver, button_id, park_id)




def logout(driver, park_id):
    """
    주차장 ID에 따른 로그아웃 처리 함수
    """
    try:
        if park_id == 18577:
            print("DEBUG: 18577 전용 로그아웃 버튼 찾기")
            logout_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='btnDelete btn' and @onclick='logout()']"))
            )

        elif park_id == 16096:
            print("DEBUG: 16096 전용 로그아웃 버튼 XPath로 탐색")
            try:
                logout_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@onclick='logout()']"))
                )
            except TimeoutException:
                logout_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'LOGOUT')]"))
                )

        else:
            print("DEBUG: 일반 주차장 로그아웃 버튼 찾기")
            logout_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/table/tbody/tr/td[2]/button"))
            )

        logout_button.click()
        print("DEBUG: 로그아웃 버튼 클릭 완료.")
        return True

    except TimeoutException:
        print("ERROR: 로그아웃 버튼을 찾을 수 없음.")
        return False



def try_force_logout_if_already_logged_in(driver, park_id):
    """
    로그인 시 이미 로그인된 상태일 경우:
    - 가려진 팝업 닫기
    - 로그아웃 버튼 클릭
    - '로그아웃하시겠습니까?' 팝업에서 Yes 클릭
    - 로그인 페이지 복귀 확인
    """
    try:
        # 로그아웃 버튼으로 로그인 상태 판단
        logout_button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, side_nav_xpath))
        )
        print("DEBUG: 이미 로그인된 상태 감지됨. 로그아웃 시도.")

        # ✅ modal-window 팝업이 있을 경우 우선 닫기
        try:
            modal = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.ID, "modal-window"))
            )
            print("DEBUG: modal-window 감지됨. 닫기 시도.")
            close_btn = modal.find_element(By.CLASS_NAME, "modal-btn")
            close_btn.click()
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element((By.ID, "modal-window"))
            )
            print("DEBUG: modal-window 닫기 완료.")
        except TimeoutException:
            print("DEBUG: modal-window 없음 (닫을 팝업 없음).")

        # 로그아웃 버튼 클릭
        logout_button.click()
        print("DEBUG: 로그아웃 버튼 클릭 완료.")

        # ✅ 로그아웃 확인 팝업 ('로그아웃하시겠습니까?') → Yes 버튼 클릭
        try:
            confirm_yes_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-box .modal-btn.btn-light-blue"))
            )
            confirm_yes_button.click()
            print("DEBUG: 로그아웃 확인 팝업 'Yes' 버튼 클릭 완료.")
        except TimeoutException:
            print("DEBUG: 로그아웃 확인 팝업이 감지되지 않음 (정상일 수도 있음).")

        # ✅ Alert 창이 있을 경우 닫기
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
            print("DEBUG: 로그아웃 Alert 닫기 완료.")
        except TimeoutException:
            pass

        # ✅ 로그인 페이지로 복귀했는지 확인 (ID 입력 필드 기준)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "userId"))
        )
        print("DEBUG: 로그아웃 후 로그인 페이지 로딩 완료.")
        return True

    except TimeoutException:
        print("DEBUG: 사전 로그인 상태는 아닌 것으로 판단.")
        return False

def close_popup_window_for_19239(driver, park_id):
    """
    park_id=19239 전용. 로그인 후 새로 뜨는 팝업 창에서 X 버튼 클릭하여 닫기
    """
    if park_id != 19239:
        return

    main_window = driver.current_window_handle
    all_windows = driver.window_handles

    # 새 창이 떴는지 확인
    if len(all_windows) <= 1:
        print("DEBUG: 새 창 팝업이 감지되지 않음.")
        return

    for handle in all_windows:
        if handle != main_window:
            print("DEBUG: 19239 팝업 창 감지됨. 전환 후 X 버튼 클릭 시도.")
            driver.switch_to.window(handle)
            try:
                # 닫기 버튼 감지 및 클릭
                close_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@id='close_div']//label[contains(text(), 'X')]"))
                )
                close_button.click()
                print("DEBUG: 팝업 X 버튼 클릭 완료.")
            except TimeoutException:
                print("ERROR: 팝업 X 버튼을 찾을 수 없음.")
            except NoSuchElementException:
                print("ERROR: 팝업 닫기 버튼 요소 없음.")
            except Exception as e:
                print(f"ERROR: 팝업 닫기 중 예외 발생: {e}")

            # 팝업 닫혔을 것으로 간주하고 메인 창으로 복귀
            driver.switch_to.window(main_window)
            break

def web_har_in(target, driver):
    """
    주차권 할인을 처리하는 메인 함수
    """
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]

    if ParkUtil.is_park_in(park_id) and park_id in mapIdToWebInfo:

        if park_id == 19335:
            login_url = "http://112.216.125.10/discount/registration"
            driver.get(login_url)
            print("✅ 19335: 로그인 페이지 접속 완료")
        else:
            login_url = ParkUtil.get_park_url(park_id)
            driver.get(login_url)


        # ✅ 여기! 로그인 상태라면 강제 로그아웃 시도
        try_force_logout_if_already_logged_in(driver, park_id)

        web_har_in_info = ParkUtil.get_park_lot_option(park_id)
        user_id = web_har_in_info[WebInfo.webHarInId]
        user_password = web_har_in_info[WebInfo.webHarInPw]

        try:
            enter_user_id(driver, user_id)

            # 비밀번호 입력 (park_id 예외 반영)
            if not enter_password(driver, user_password, park_id):
                print("ERROR: 비밀번호 입력 실패로 중단")
                return False

            #password_field = WebDriverWait(driver, 10).until(
            #    EC.presence_of_element_located((By.ID, "userPwd"))
            #)
            #password_field.send_keys(user_password)

            print("로그인 버튼 클릭 전 3초 대기...")
            time.sleep(3)

            # 로그인 버튼 찾기 및 클릭
            try:
                if park_id == 16096:
                    print("DEBUG: 16096 전용 로그인 처리 (form submit 방식)")

                    try:
                        form = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "loginForm"))
                        )
                        form.submit()
                        print("✅ 16096 로그인 form.submit() 성공")
                    except Exception as e:
                        print(f"⚠️ 16096 form.submit() 실패, JS 클릭 시도: {e}")
                        # 실패 시 JS 클릭 방식 시도
                        login_button = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "login_area_btn"))
                        )
                        driver.execute_script("arguments[0].click();", login_button)
                        print("✅ 16096 로그인 JS 클릭 성공")

                elif park_id in [18938, 18577, 19906, 19258, 19239, 19331, 19077, 45010, 14618, 19253]:
                    print(f"DEBUG: {park_id} 전용 로그인 버튼 클릭")
                    login_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "login_area_btn"))
                    )
                    login_button.click()
                    print("로그인 버튼 클릭 완료!")

                else:
                    login_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='btnLogin']"))
                    )
                    login_button.click()
                    print("로그인 버튼 클릭 완료!")

            except TimeoutException:
                print("ERROR: 로그인 버튼을 찾을 수 없음.")

            handle_alert(driver)

            # 🔽 팝업 감지 후 X버튼 클릭 시도
            close_popup_window_for_19239(driver, park_id)

            # ✅ 29118인 경우 팝업 처리 및 할인 페이지 이동
            handle_notice_popup_and_redirect(driver, park_id)

            # ✅ 19335일 경우, 팝업 닫고 할인 버튼 클릭 추가
            handle_popup_and_go_discount(driver, park_id)

            close_vehicle_number_popup(driver)

            # ✅ 차량번호 입력 후 실패 여부 확인
            driver.car_number_last4 = ori_car_num[-4:]
            if not enter_car_number(driver, ori_car_num[-4:], park_id):
                print("ERROR: 차량번호 입력 실패로 할인 중단.")
                return False  # 🚨 차량번호 입력 실패 시 즉시 중단

            # ✅ 할인권 처리
            entry_day_of_week = target[4].strftime('%a')
            return handle_ticket(driver, park_id, ticket_name, entry_day_of_week=entry_day_of_week)



        except NoSuchElementException as ex:
            print(f"할인 처리 중 오류 발생: {ex}")
            return False

    return False