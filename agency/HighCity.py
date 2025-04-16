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

    # AIA 타워
    18958: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('14', '1', '', '파킹박(평일)', '999999999', '0');",
            "javascript:applyDiscount('15', '1', '', '파킹박(주말)', '999999999', '0');",
            "javascript:applyDiscount('17', '1', '', '파킹박(야간)', '999999999', '0');"],
    # SC_BANK
    12750: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('23', '1', '16|25|', '파킹박 (web)', '999999999');",
            "javascript:applyDiscount('23', '1', '16|25|', '파킹박 (web)', '999999999');",
            ""],

    # 트윈시티남산
    16003: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('98', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('98', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('92', '1', '', '파킹박(야간)', '1', '0');"

            ],

    # 다동패스트파이브 타워
    16170: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('05', 'CP0802', '1', '', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('05', 'CP0802', '1', '', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('32', '1', '', '파킹박(야간)', '999999999', '0') ;",
            ],
    # 여의도 리버타워
    20863: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('19', '1', '20|', '파킹박');",
            "javascript:applyDiscount('19', '1', '20|', '파킹박');"
            ],
    # EG빌딩
    19194: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('20', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('20', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('32', '1', '', 'ppark(야간)', '1', '0') ;",
            ],
    # (하이파킹) 오라카이대학로
    19181: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('21', '1', '', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('21', '1', '', 'ppark', '999999999', '0');"
            ],

    #  문정플라자
    19022: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('35', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('35', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('98', '1', '04|', 'ppark(야간)', '1', '0') ;",
            ],
    #  코리아나호텔
    19248: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('13', '1', '01|02|03|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('13', '1', '01|02|03|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('31', '1', '', 'ppark(야간)', '999999999', '0');",
            ],
    #  힐스테이트에코마곡나루역
    19272: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '17|', 'ppark', '1', '0');",
            "javascript:applyDiscount('08', '1', '17|', 'ppark', '1', '0');"
            ],

    #  동산마을공영
    19276: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            ],
    #  D타워
    19325: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('14', '1', '11|20|21|', 'ppark', 'Y');",
            "javascript:applyDiscount('14', '1', '11|20|21|', 'ppark', 'Y');",
            "javascript:applyDiscount('17', '1', '11|20|21|', 'ppark(야간)', 'Y');",  # ← 이 부분 고쳐야 함
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


    # (하이파킹) 서울역 주차장
    20864: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('12', '', '5', '01|', 'ppark', '1', '0');",  # 평일1일권
            "javascript:applyDiscount('25', '', '1', '', 'ppark(연박2일)', '1', '0');",  # 연박2일권"",
            "javascript:applyDiscount('26', '', '1', '', 'ppark(연박3일)', '1', '0');",  # 연박3일권"",
            "javascript:applyDiscount('27', '', '1', '', 'ppark(연박4일)', '1', '0');",  # 연박4일권"",
            "javascript:applyDiscount('28', '', '1', '', 'ppark(연박5일)', '1', '0');",  # 연박5일권"",
            ],

    # TURU 을지트윈타워 (할인 버튼을 직접 클릭하므로 스크립트는 불필요)
    19174: [
        "name_form",  # 0: ID 입력 필드
        "pwd_form",  # 1: PW 입력 필드
        "//*[@id='login']/table[1]/tbody/tr[3]/td[2]/input",  # 2: 로그인 버튼
        "carNumber",  # 3: 차량번호 입력
        "/html/body/table[2]/tbody/tr[5]/td/input",  # 4: 검색 버튼
        "BTN_공유서비스 종일"  # 5: 할인 버튼 ID (예시)
    ],

    # 오라카이 청계산
    19185: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('31', '1', '', '파킹박', '1', '0')   ",  # 평일1일권
            "javascript:applyDiscount('31', '1', '', '파킹박', '1', '0')  ",  # 주말
            "javascript:applyDiscount('31', '1', '', '파킹박', '1', '0') ",
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


    # 하이파킹 평촌역점
    19740: ["name", "pwd", "/html/body/table/tbody/tr[3]/td[2]/input",
            "carNumber", "/html/body/table[2]/tbody/tr[5]/td/input",
            "",  # radio 버튼 처리 안함
            "-",  # btnItem 없음
            "-",  # weekday 스크립트 제거
            "-",  # weekend 스크립트 제거
            "-",  # night 스크립트 제거
            ],

    # 하이파킹 천안G스퀘어
    19323: ["login_id", "login_pw", "//*[@id='bodyCSS']/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td/div/div[1]/input",
            "searchCarNo", "//*[@id='btnSearch']",
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

# 	하이파킹 아이콘삼성
    35529: ["login_id", "login_pw",
            "/html/body/div/div/form/center/button[1]",
            "carNumber", "/html/body/div[2]/ul/li/button",
            "",  # radio 버튼 처리 안함
            "-",  # btnItem 없음
            "-",  # weekday 스크립트 제거
            "-",  # weekend 스크립트 제거
            "-",  # night 스크립트 제거
            ],

}

def get_har_in_script(park_id, ticket_name):
    # 1. 특정 주차장 + 특정 티켓 분기

    if park_id == 18958:
        if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
            return "javascript:applyDiscount('14', '1', '', '파킹박(평일)', '999999999', '0');"

        elif ticket_name == "휴일 당일권":
            return "javascript:applyDiscount('15', '1', '', '파킹박(주말)', '999999999', '0');"

        elif ticket_name in [
            "평일 12시간권(월~화)",
            "평일 12시간권(수~목)",
            "평일 12시간권(금)"
        ]:
            return "javascript:applyDiscount('23', '1', '', '12시간권', '999999999', '0');"

        elif ticket_name == "평일 심야권":
            return "javascript:applyDiscount('17', '1', '', '파킹박(야간)', '999999999', '0');"

        else:
            return False  # 정의되지 않은 티켓 이름은 실패 처리

    if park_id == 19272:
        if ticket_name in [
            "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)",
            "평일 당일권(목)", "평일 당일권(금)",
            "휴일 당일권(토)", "휴일 당일권(일)"
        ]:
            return "javascript:applyDiscount('08', '', '5', '17|27|', 'ppark', '1', '0');"
        elif ticket_name == "평일 오후권":
            return "javascript:applyDiscount('30', '', '1', '', '평일오후권(공유서비스)', '1', '0');"
        elif ticket_name in ["평일 심야권", "휴일 심야권"]:
            return "javascript:applyDiscount('32', '', '1', '', '심야권(공유서비스)', '1', '0');"
        elif ticket_name == "2일 연박권":
            return "javascript:applyDiscount('80', '', '1', '27|', '2일권', '1', '0');"
        elif ticket_name == "3일 연박권":
            return "javascript:applyDiscount('81', '', '1', '27|', '3일권', '1', '0');"
        elif ticket_name == "4일 연박권":
            return "javascript:applyDiscount('82', '', '1', '27|', '4일권', '1', '0');"
        elif ticket_name == "5일 연박권":
            return "javascript:applyDiscount('83', '', '1', '27|', '5일권', '1', '0');"
        elif ticket_name == "6일 연박권":
            return "javascript:applyDiscount('33', '', '1', '', '6연박권(공유서비스)', '1', '0');"
        elif ticket_name == "7일 연박권":
            return "javascript:applyDiscount('34', '', '1', '', '7연박권(공유서비스)', '1', '0');"
        elif ticket_name == "8일 연박권":
            return "javascript:applyDiscount('35', '', '1', '', '8연박권(공유서비스)', '1', '0');"
        else:
            return False


    if park_id == 20864:
        if ticket_name == "평일 3시간권":
            return "javascript:applyDiscount('88', '', '1', '', '평일3시간권(공유서비스)', '1', '0');"
        elif ticket_name == "평일 오후 6시간권":
            return "javascript:applyDiscount('90', '', '1', '', '평일오후6시간권(공유)', '1', '0');"
        elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
            return "javascript:applyDiscount('12', '', '5', '01|10|', 'ppark', '1', '0');"
        elif ticket_name == "2일권":
            return "javascript:applyDiscount('25', '', '1', '', 'ppark(연박2일)', '1', '0');"
        elif ticket_name == "3일권":
            return "javascript:applyDiscount('26', '', '1', '', 'ppark(연박3일)', '1', '0');"
        elif ticket_name == "4일권":
            return "javascript:applyDiscount('27', '', '1', '', 'ppark(연박4일)', '1', '0');"
        elif ticket_name == "5일권":
            return "javascript:applyDiscount('28', '', '1', '', 'ppark(연박5일)', '1', '0');"
        else:
            return False  # ❗️지정되지 않은 ticket_name은 처리하지 않음


        # ✅ 12750 전용 할인권 처리
    if park_id == 12750:
        if ticket_name in ["평일 3시간권", "평일 12시간권"]:
            return "javascript:applyDiscount('76', '1', '', '12시간권', '999999999');"
        elif ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)", "휴일 당일권"]:
            return "javascript:applyDiscount('23', '1', '36|16|25|35|', '파킹박 (web)', '999999999');"
        elif ticket_name in ["평일 심야권(일~목)", "휴일 심야권(금,토)"]:
            return "javascript:applyDiscount('37', '1', '36|', '파킹박(야간)', '999999999');"
        else:
            return False

    if park_id == 19325:
        if ticket_name in [
            "평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"
        ]:
            return "javascript:applyDiscount('14', '1', '11|20|21|', 'ppark', 'Y');"
        elif ticket_name in [
            "평일 12시간권(월)", "평일 12시간권(화~금)"
        ]:
            return "javascript:applyDiscount('75', '1', '', '12시간', '');"
        elif ticket_name == "휴일 당일권":
            return "javascript:applyDiscount('83', '1', '20|21|', 'ppark(주말24시간)', 'Y');"
        elif ticket_name in ["평일 심야권(일~목)", "심야권(금,토)"]:
            return "javascript:applyDiscount('17', '1', '11|20|21|', 'ppark(야간)', 'Y');"
        else:
            return False

    if park_id == 16003:
        if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)", "휴일 당일권"]:
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
        if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
            return "BTN_공유서비스 종일"
        elif ticket_name in ["휴일 24시간권(토)", "휴일 24시간권(일)"]:
            return "BTN_공유서비스 주말"
        elif ticket_name == "평일 12시간권(화~금)":
            return "BTN_12시간권_O2O"
        elif ticket_name in ["평일 심야권", "휴일 심야권"]:
            return "BTN_공유서비스 야간"
        elif ticket_name == "평일 3시간권":
            return "BTN_공유서비스 (3시간)"
        else:
            return False

    if park_id == 19364:
        if ticket_name in [
            "평일 당일권(월~화)",
            "평일 당일권(수~목)",
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
        elif ticket_name == "평일 3시간권":
            return "javascript:applyDiscount('25', 'CP0802', '1', '', '3시간권', '999999999', '0');"
        elif ticket_name in ["평일 심야권", "휴일 심야권"]:
            return "javascript:applyDiscount('90', 'CP0802', '1', '20|', '심야권(공유서비스)', '999999999', '0');"
        else:
            return False

    if park_id == 20863:
        if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)", "휴일 당일권"]:
            return "javascript:applyDiscount('19', '1', '05|', '파킹박');"
        else:
            return False  # ❗️20863에서 지정된 티켓 외는 실패 처리

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
    """
    할인 스크립트 실행 후 alert 창을 통해 성공 여부 판단
    단, 특정 주차장은 alert이 존재하지 않음 (예: 20863) → 예외 처리
    """
    if park_id in [20863, 19364, 19325, 18958, 16003,20864,19272]:
        print("✅ 할인 결과 알림창 없음 → 예외 없이 성공 처리 (예상된 구조)")
        return True

    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()

        print(f"할인 결과 알림창: {alert_text}")
        if "할인 되었습니다" in alert_text or "등록되었습니다" in alert_text:
            return True
        else:
            return False

    except Exception as e:
        print("❌ 할인 처리 후 알림창이 감지되지 않음:", e)
        return False




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

    if ParkUtil.is_park_in(park_id):
        if park_id in mapIdToWebInfo:
            login_url = ParkUtil.get_park_url(park_id)
            driver.implicitly_wait(3)
            driver.get(login_url)

            web_info = mapIdToWebInfo[park_id]
            web_har_in_info = ParkUtil.get_park_lot_option(park_id)

            # 재접속이 아닐 때, 그러니까 처음 접속할 때
            if ParkUtil.first_access(park_id, driver.current_url):

                driver.find_element_by_id(web_info[WebInfo.inputId]).send_keys(web_har_in_info[WebInfo.webHarInId])
                driver.find_element_by_id(web_info[WebInfo.inputPw]).send_keys(web_har_in_info[WebInfo.webHarInPw])
                driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()

                driver.implicitly_wait(3)

                driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
                Util.sleep(3)

                driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()
                Util.sleep(1)

                if ParkUtil.check_search(park_id, driver):

                    if ParkUtil.check_same_car_num(park_id, ori_car_num, driver):

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

                        if park_id == 12750:
                            harin_script = get_har_in_script(park_id, ticket_name)
                            if not harin_script:
                                print(Colors.RED + f"❌ 유효하지 않은 ticket_name: {ticket_name}" + Colors.ENDC)
                                return False

                            try:
                                driver.execute_script(harin_script)
                                print(Colors.GREEN + "✅ 할인 스크립트 직접 실행 완료 (12750)" + Colors.ENDC)

                                # 알림창 처리 (성공 여부 판단)
                                return check_discount_alert(driver, park_id)

                            except Exception as e:
                                print(Colors.RED + f"❌ 할인 스크립트 실행 실패 (12750): {e}" + Colors.ENDC)
                                return False

                        if park_id == 19492:
                            try:
                                # <tr> 클릭해서 팝업 띄우기
                                tr = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "#tbData > tbody > tr"))
                                )
                                driver.execute_script("arguments[0].click();", tr)
                                print(Colors.GREEN + "✅ 19492 <tr> 클릭으로 차량 선택 성공" + Colors.ENDC)

                                Util.sleep(1.5)  # 팝업 로딩 시간 대기

                                # ticket_name에 따라 할인 버튼 텍스트 선택
                                if ticket_name == "평일1일권":
                                    button_text = "24시간(유료)"
                                elif ticket_name == "12시간권":
                                    button_text = "12시간(유료)"
                                elif ticket_name == "주말1일권":
                                    button_text = "휴일당일권"
                                else:
                                    print(Colors.RED + "❌ 정의되지 않은 ticket_name" + Colors.ENDC)
                                    return False

                                # 팝업 내 할인 버튼 클릭
                                btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, f"//button[@name='btnDckey' and text()='{button_text}']"))
                                )
                                driver.execute_script("arguments[0].click();", btn)
                                print(Colors.GREEN + f"✅ 팝업 내 할인 버튼 클릭 성공 ({button_text})" + Colors.ENDC)

                                # ✅ Alert 처리 추가
                                try:
                                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                                    alert = driver.switch_to.alert
                                    print(Colors.BLUE + f"알림창 텍스트: {alert.text}" + Colors.ENDC)
                                    alert.accept()  # '확인' 버튼 누르기
                                    print(Colors.GREEN + "✅ 알림창 확인 클릭 완료" + Colors.ENDC)
                                except Exception as e:
                                    print(Colors.YELLOW + f"⚠️ 알림창이 뜨지 않거나 자동 확인 실패: {e}" + Colors.ENDC)

                                return True

                            except Exception as e:
                                print(Colors.RED + f"❌ 19492 할인 처리 실패: {e}" + Colors.ENDC)
                                return False

                        if park_id == 20863:
                            try:
                                # ✅ 이미 체크된 상태 유지 → 재클릭 없이 잠시 대기
                                Util.sleep(0.8)  # 체크박스 선택 적용 시간 확보

                                # ✅ 할인 버튼 클릭 (파킹박)
                                btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, "//input[@type='button' and @value='파킹박']")
                                    )
                                )
                                driver.execute_script("arguments[0].click();", btn)
                                print("✅ 파킹박 버튼 클릭 완료 (20863)")

                                Util.sleep(1.0)  # 반응 대기

                                # 20863은 alert 없음 → 체크 생략
                                return True

                            except Exception as e:
                                print(Colors.RED + f"❌ 20863 할인 처리 실패: {e}" + Colors.ENDC)
                                return False

                        if park_id == 19325:
                            try:
                                chk_elem = WebDriverWait(driver, 3).until(
                                    EC.presence_of_element_located((By.ID, "chk")))
                                is_checked = driver.execute_script("return arguments[0].checked;", chk_elem)
                                if not is_checked:
                                    driver.execute_script("arguments[0].checked = true;", chk_elem)
                                    print("✅ 라디오 버튼 'chk' 강제 체크 적용됨 (19325)")
                                else:
                                    print("✅ 라디오 버튼 'chk' 이미 체크되어 있음 (19325)")
                                Util.sleep(0.3)
                            except Exception as e:
                                print(f"⚠️ chk 체크 상태 확인 또는 강제화 실패: {e}")

                        if park_id == 35529:
                            try:
                                ori_car_num = ori_car_num.replace(" ", "")  # 차량번호 공백 제거

                                # 차량 검색 결과 영역에서 <a> 요소 목록 조회
                                car_links = WebDriverWait(driver, 5).until(
                                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#divAjaxCarList a"))
                                )

                                matched = False
                                for a_tag in car_links:
                                    site_car_num = a_tag.text.strip()
                                    if site_car_num == ori_car_num or site_car_num[-7:] == ori_car_num[-7:]:
                                        driver.execute_script("arguments[0].click();", a_tag)
                                        print(Colors.GREEN + f"✅ 차량번호 클릭 성공 (35529): {site_car_num}" + Colors.ENDC)
                                        matched = True
                                        break

                                if not matched:
                                    print(Colors.RED + f"❌ 일치하는 차량번호를 찾을 수 없습니다 (35529)" + Colors.ENDC)
                                    return False

                                Util.sleep(1.5)  # 페이지 전환 대기

                                if ticket_name in ["평일 당일권(월)", "평일 당일권(화)", "평일 당일권(수)", "평일 당일권(목)", "평일 당일권(금)"]:
                                    btn = WebDriverWait(driver, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH,
                                             "//td[@id='DCInfo']//input[@type='button' and contains(@value, '파킹박(평일종일)')]")
                                        )
                                    )
                                    driver.execute_script("arguments[0].click();", btn)
                                    print(Colors.GREEN + "✅ 할인 버튼 클릭 성공: 파킹박(평일종일) (35529)" + Colors.ENDC)

                                    # Alert 처리
                                    try:
                                        WebDriverWait(driver, 3).until(EC.alert_is_present())
                                        alert = driver.switch_to.alert
                                        print(Colors.BLUE + f"알림창 텍스트: {alert.text}" + Colors.ENDC)
                                        alert.accept()
                                        print(Colors.GREEN + "✅ 알림창 확인 완료 (35529)" + Colors.ENDC)
                                    except Exception as e:
                                        print(Colors.YELLOW + f"⚠️ 알림창 없음 또는 처리 실패: {e}" + Colors.ENDC)

                                    return True

                                else:
                                    print(Colors.RED + f"❌ 정의되지 않은 ticket_name: {ticket_name}" + Colors.ENDC)
                                    return False

                            except Exception as e:
                                print(Colors.RED + f"❌ 35529 할인 처리 실패: {e}" + Colors.ENDC)
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
                                if ticket_name in ["평일1일권", "주말1일권"]:
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

                        if park_id == 19323:
                            try:
                                # 차량번호 비교 성공 후: <a onclick="fnCarInfoTotal(...)"> 클릭 처리
                                car_link = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "#divAjaxCarList a"))
                                )
                                onclick_script = car_link.get_attribute("onclick")
                                if onclick_script:
                                    driver.execute_script(onclick_script)
                                    print(Colors.GREEN + "✅ 차량 클릭 스크립트 실행 완료 (19323)" + Colors.ENDC)
                                else:
                                    print(Colors.RED + "❌ 차량 클릭 스크립트 없음 (19323)" + Colors.ENDC)
                                    return False

                                Util.sleep(1.5)  # 팝업 로딩 대기

                                # ticket_name → 버튼 텍스트 매핑
                                ticket_button_map = {
                                    "평일 12시간권": "12시간(공유서비스)",
                                    "휴일 12시간권": "12시간(공유서비스)",
                                    "평일 24시간권": "24시간(공유서비스)",
                                    "휴일 24시간권": "24시간(공유서비스)",
                                    "평일 48시간권": "48시간(공유서비스)",
                                    "휴일 48시간권": "48시간(공유서비스)",
                                    "평일 60시간권": "60시간(공유서비스)",
                                    "휴일 60시간권": "60시간(공유서비스)",
                                }

                                if ticket_name not in ticket_button_map:
                                    print(Colors.RED + f"❌ 정의되지 않은 ticket_name: {ticket_name}" + Colors.ENDC)
                                    return False

                                button_text = ticket_button_map[ticket_name]

                                # 팝업 내 버튼 XPath 클릭
                                button_xpath = f"//div[@id='divAjaxFreeDiscount']//button[contains(text(), '{button_text}')]"
                                btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, button_xpath))
                                )
                                driver.execute_script("arguments[0].click();", btn)
                                print(Colors.GREEN + f"✅ 할인 버튼 클릭 성공 (19323): {button_text}" + Colors.ENDC)

                                # Alert 처리
                                try:
                                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                                    alert = driver.switch_to.alert
                                    print(Colors.BLUE + f"할인 알림창 텍스트: {alert.text}" + Colors.ENDC)
                                    alert.accept()
                                    print(Colors.GREEN + "✅ 알림창 확인 완료 (19323)" + Colors.ENDC)
                                except Exception as e:
                                    print(Colors.YELLOW + f"⚠️ 알림창 없음 또는 확인 실패: {e}" + Colors.ENDC)

                                return True

                            except Exception as e:
                                print(Colors.RED + f"❌ 19323 처리 중 오류: {e}" + Colors.ENDC)
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

                                # 팝업 내 할인 버튼 클릭
                                discount_btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, f"//button[@name='btnDckey' and contains(text(), '{button_text}')]"))
                                )
                                driver.execute_script("arguments[0].click();", discount_btn)
                                print(Colors.GREEN + f"✅ 할인 버튼 클릭 성공: {button_text}" + Colors.ENDC)

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

                        if park_id == 13007:
                            print(f"DEBUG: 13007 전용 할인 처리 시작 (ticket_name={ticket_name})")

                            ticket_button_map = {
                                "평일 당일권(월)": "파킹박",
                                "평일 당일권(화)": "파킹박",
                                "평일 당일권(수)": "파킹박",
                                "평일 당일권(목)": "파킹박",
                                "평일 당일권(금)": "파킹박",
                                "휴일 당일권": "파킹박",
                                "평일 3시간권": "평일3시간권(공유서비스)",
                                "평일 6시간권": "6시간권",
                                "휴일 6시간권": "6시간권",
                                "야간8시간권": "야간8시간권(공유서비스)",
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

                        if park_id == 19740:
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
                                    print(Colors.RED + "❌ 차량번호 정보를 찾을 수 없습니다 (19740)" + Colors.ENDC)
                                    return False

                                if ori_car_num == site_car_num or ori_car_num[-7:] == site_car_num[-7:] or ori_car_num[
                                                                                                           -6:] == site_car_num[
                                                                                                                   -6:]:
                                    print(Colors.GREEN + "차량번호 정확 또는 유사 일치 (19740)" + Colors.ENDC)
                                else:
                                    print(
                                        Colors.MARGENTA + f"차량번호 불일치 (입력: {ori_car_num}, 사이트: {site_car_num})" + Colors.ENDC)
                                    return False

                                # ticket_name에 따라 버튼 텍스트 매칭
                                if ticket_name == "평일 당일권":
                                    btn = WebDriverWait(driver, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//input[@type='button' and contains(@value, '평일당일권 (공유)')]")
                                        )
                                    )
                                    driver.execute_script("arguments[0].click();", btn)
                                    print(Colors.GREEN + "✅ 평일당일권 (공유) 버튼 클릭 성공 (19740)" + Colors.ENDC)

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
                                else:
                                    print(Colors.RED + f"❌ 정의되지 않은 ticket_name: {ticket_name}" + Colors.ENDC)
                                    return False

                            except Exception as e:
                                print(Colors.RED + f"❌ 19740 할인 처리 실패: {e}" + Colors.ENDC)
                                return False

                        if park_id in [29218, 18996]:
                            try:
                                ori_car_num = ori_car_num.replace(" ", "")  # 차량번호 공백 제거

                                # 차량 정보 영역 확인
                                info_td = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, "//td[h3[contains(text(), '차량 정보')]]"))
                                )
                                text = info_td.text.strip()

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
                                if ticket_name == "평일 당일권":
                                    btn_id = "BTN_종일권 (공유서비스)"
                                elif ticket_name == "휴일 당일권":
                                    btn_id = "BTN_주말권 (공유서비스)"
                                elif ticket_name in ["평일 3시간권", "휴일 3시간권"]:
                                    btn_id = "BTN_3시간권 (공유서비스)"
                                else:
                                    print(Colors.RED + f"❌ 정의되지 않은 ticket_name: {ticket_name}" + Colors.ENDC)
                                    return False

                                # 버튼 클릭
                                print(Colors.BLUE + f"버튼 ID: {btn_id}" + Colors.ENDC)
                                btn = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, btn_id)))
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
                                if ticket_name == "평일 당일권":
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
                        if park_id not in [12750, 19492] and btn_item and btn_item != "-":
                            driver.find_element_by_id(btn_item).click()

                        harin_script = get_har_in_script(park_id, ticket_name)
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
                                driver.find_element_by_id(harin_script).click()

                                # ✅ 버튼 클릭 후 confirm 팝업 자동 처리
                                WebDriverWait(driver, 5).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                print(f"Alert Text: {alert.text}")  # 팝업 메시지 로그 출력
                                alert.accept()  # 팝업 '확인' 클릭

                            else:
                                driver.execute_script(harin_script)

                            print("할인 스크립트 실행 완료")
                            return check_discount_alert(driver, park_id)
                        except UnexpectedAlertPresentException:
                            try:
                                alert = driver.switch_to.alert
                                print(f"[ERROR 처리 중 Alert 발생] Alert Text: {alert.text}")
                                alert.accept()
                            except NoAlertPresentException:
                                pass
                            return False
                        except Exception as e:
                            print(f"할인 스크립트 실행 중 오류 발생: {e}")
                            return False

                return False

        else:
            print(Colors.BLUE + "high현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
