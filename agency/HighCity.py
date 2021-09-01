# -*- coding: utf-8 -*-
import Util
import Colors
from park import ParkUtil, ParkType, Parks
import WebInfo

mapIdToWebInfo = {
    # HighCity 동일타워
    15313: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('10', '1', '', '어플평일당일권(웹할인)', '1', '0');",
            "javascript:applyDiscount('09', '1', '', '어플주말당일권(웹할인)', '1', '0');"],
    # 남산스퀘어
    13007: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('62', '1', '', '파킹박', '1')",
            "javascript:applyDiscount('62', '1', '', '파킹박', '1')",
            "javascript:applyDiscount('66', '1', '', '파킹박(야간)', '1') ",
            ],
    # 플래티넘타워
    12130: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('20', '1', '', '파킹박');",
            "javascript:applyDiscount('20', '1', '', '파킹박');",
            "javascript:applyDiscount('91', '1', '', '파킹박(야간)');"],

    # 와이즈파크
    15644: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('11', '1', '', '파킹박 종일권', '1', '0');",
            "javascript:applyDiscount('11', '1', '', '파킹박 종일권', '1', '0');",
            "javascript:applyDiscount('03', '2', '01|09|10|', '3시간무료', '1', '0');"],
    # K스퀘어
    11917: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('94', '1', '', '파킹박');",
            "javascript:applyDiscount('94', '1', '', '파킹박');"],
    # AIA 타워
    18958: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('14', '1', '', '파킹박(평일)', '999999999', '0');",
            "javascript:applyDiscount('15', '1', '', '파킹박(주말)', '999999999', '0');",
            "javascript:applyDiscount('17', '1', '', '파킹박(야간)', '999999999', '0');"],
    # 구의웰츠타워
    15437: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('16', '1', '', '파킹박(평일)');",
            "javascript:applyDiscount('18', '1', '', '파킹박(주말)');",
            "javascript:applyDiscount('17', '1', '', '파킹박(야간)');"],
    # 아이콘역삼
    15008: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('94', '1', '', '파킹박');",
            "javascript:applyDiscount('94', '1', '', '파킹박');",
            "javascript:applyDiscount('91', '1', '', '파킹박(야간)', '1', '0');"],
    # 에코테라스
    14994: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('95', '1', '76|', '파킹박', '1', '0');",
            "javascript:applyDiscount('90', '1', '76|', '파킹박(주말)', '1', '0');",
            "javascript:applyDiscount('89', '1', '76|', '파킹박(야간)', '1', '0');"],
    # 와이즈타워
    12904: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//input[@type='button']",
            "chk",
            "javascript:applyDiscount('96', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('93', '1', '', '파킹박(주말)', '1', '0');",
            "javascript:applyDiscount('92', '1', '', '파킹박(야간)', '1', '0');"],
    # 역삼 아크플레이스
    11349: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('95', '1', '', '파킹박', '1');",
            "javascript:applyDiscount('95', '1', '', '파킹박', '1');",
            "javascript:applyDiscount('82', '1', '', '파킹박(야간)', '1') ;",
            ""],
    # 알파돔타워
    19089: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('24', '1', '06|', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('24', '1', '06|', '파킹박', '999999999', '0');",
            ""],
    # SC_BANK
    12750: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('23', '1', '16|25|', '파킹박 (web)', '999999999');",
            "javascript:applyDiscount('23', '1', '16|25|', '파킹박 (web)', '999999999');",
            ""],
    # 시그니쳐타워
    12951: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('17', '1', '07|09|10|23|', '파킹박(평일)', '999999999', '0');",
            "javascript:applyDiscount('19', '1', '07|09|10|23|', '파킹박(주말)', '999999999', '0');",
            "javascript:applyDiscount('18', '1', '07|09|10|23|', '파킹박(야간)', '999999999', '0');"
            ],

    # 트윈시티남산
    16003: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('98', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('98', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('92', '1', '', '파킹박(야간)', '1', '0');"

            ],
    # HSBC
    16184: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('15', '1', '13|', '파킹박');",
            "javascript:applyDiscount('15', '1', '13|', '파킹박');"
            ],
    # 시티플라자 기계식
    18956: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('16', '1', '', '파킹박');",
            "javascript:applyDiscount('16', '1', '', '파킹박');"
            ],
    # 시티플라자 지하
    18970: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('16', '1', '', '파킹박');",
            "javascript:applyDiscount('16', '1', '', '파킹박');"
            ],
    # 명동 우리금융남산타워
    16175: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('14', '1', '04|15|', '파킹박(평일)');",
            "javascript:applyDiscount('18', '1', '', '파킹박(주말)');",
            "javascript:applyDiscount('17', '1', '', '파킹박(야간)');"
            ],
    # 센터플레이스
    16210: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('96', '1', '01|', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('96', '1', '01|', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('82', '1', '', '파킹박(야간)', '999999999', '0') ;",
            ],
    # 서소문한화빌딩
    18972: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('17', '1', '21|23|', '파킹박(평일)', '999891999');",
            "javascript:applyDiscount('25', '1', '23|', '파킹박(주말)', '999891999');"
            ],
    # 홍대 롯데호텔 L7
    19038: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('20', '1', '', '파킹박 종일권', '1');",
            "javascript:applyDiscount('20', '1', '', '파킹박 종일권', '1');"
            ],
    # 패스트파이브 타워
    16170: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('05', 'CP0802', '1', '', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('05', 'CP0802', '1', '', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('32', '1', '', '파킹박(야간)', '999999999', '0') ;",
            ],
    # 센트럴플레이스
    12997: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('95', '1', '01|', '파킹박', '1', '0');",
            "javascript:applyDiscount('95', '1', '01|', '파킹박', '1', '0');"
            ],
    # 선릉역 위워크타워
    19086: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('95', '1', '01|23|58|', '파킹박', '1', '0');",
            "javascript:applyDiscount('89', '1', '01|23|58|', '파킹박(주말)', '1', '0');",
            "javascript:applyDiscount('88', '1', '01|23|58|', '파킹박(야간)', '1', '0');"
            ],
    # 점프밀라노
    11367: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('15', '1', '', '파킹박', '1');",
            "javascript:applyDiscount('15', '1', '', '파킹박', '1');"
            ],
    # 시청역 태평로빌딩
    19090: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('97', '1', '', '파킹박', '999999999');",
            "javascript:applyDiscount('97', '1', '', '파킹박', '999999999');",
            "javascript:applyDiscount('91', '1', '', '파킹박(야간)', '999999999') ;",
            ],
    # 여의도 리버타워
    20863: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('19', '1', '20|', '파킹박');",
            "javascript:applyDiscount('19', '1', '20|', '파킹박');"
            ],
    # 	(하이파킹) 평택ts-one
    18981: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('19', '1', '05|', '파킹박', '100000000');",
            "javascript:applyDiscount('20', '1', '05|', '파킹박(주말)', '100000000');"
            ],
    # (하이파킹) 여의도 KTB빌딩
    16360: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('96', '1', '', '파킹박');",
            "javascript:applyDiscount('96', '1', '', '파킹박');",
            "javascript:applyDiscount('89', '1', '', '파킹박(야간)') ;",
            ],
    # (하이파킹) 왕십리 W스퀘어(RAK성동빌딩)
    12183: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('97', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('97', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('81', '1', '26|27|', '파킹박(야간)', '1', '0') ;",
            ],
    # (하이파킹) DGB금융센터 주차장
    18971: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('05', '1', '13|', '파킹박(평일)', '999999999', '0');",
            "javascript:applyDiscount('08', '1', '13|', '파킹박(주말)', '999999999', '0');",
            "javascript:applyDiscount('20', '1', '', '파킹박(야간)', '999999999', '0');"
            ],
    # (하이파킹) 판교알파리움타워(상가동)
    18996: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('13', '1', '14|16|17|', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('13', '1', '14|16|17|', '파킹박', '999999999', '0');"
            ],
    # (하이시티파킹) 충정로역 센트럴타워
    16215: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('94', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('87', '1', '', '파킹박(주말)', '1', '0');",
            "javascript:applyDiscount('86', '1', '', '파킹박(야간)', '1', '0');"
            ],
    # (하이파킹) 신논현역 KI타워
    19091: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('95', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('95', '1', '', '파킹박', '1', '0');",
            ""
            ],
    # (하이파킹) 제일오피스텔
    18969: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('29', '1', '07|33|', '파킹박(평일)');",
            "javascript:applyDiscount('31', '1', '07|33|', '파킹박(주말)');",
            "javascript:applyDiscount('30', '1', '07|33|', '파킹박(야간)');"
            ],
    # (하이파킹) 수송스퀘어
    19087: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('99', '1', '', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('92', '1', '', '파킹박(주말)', '999999999', '0');",
            "javascript:applyDiscount('91', '1', '', '파킹박(야간)', '999999999', '0');"
            ],
    # (하이파킹) 을지트윈타워
    19174: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('34', '1', '47|', '파킹박', '1', '0');",
            "javascript:applyDiscount('34', '1', '47|', '파킹박', '1', '0');",
            "javascript:applyDiscount('35', '1', '47|', '파킹박(야간)', '1', '0');",
            "javascript:applyDiscount('43', '1', '47|', '파킹박(3시간)', '1', '0');"
            ],
    # (하이파킹) 강남 롯데호텔L7
    19004: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('09', '1', '06|11|20|22|', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('09', '1', '06|11|20|22|', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('31', '1', '', '파킹박(야간)', '999999999', '0');"
            ],
    # 	(하이시티파킹) 코스모타워 주차장
    12184: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('94', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('94', '1', '', '파킹박', '1', '0');"
            ],
    # 	메리츠화재여의도사옥
    19198: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('15', '1', '', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('15', '1', '', 'ppark', '999999999', '0');"
            ],
    # (하이파킹)인사동 오라카이 스위츠
    12766: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('81', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('81', '1', '', '파킹박', '1', '0');"
            ],
    # (하이파킹) 양우드라마시티
    19073: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('93', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('93', '1', '', 'ppark', '1', '0');"
            ],
    # EG빌딩
    19194: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('20', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('20', '1', '', 'ppark', '1', '0');",
            "javascript:applyDiscount('32', '1', '', 'ppark(야간)', '1', '0') ;",
            ],
    # (하이파킹)오투타워(구 HP빌딩)
    19083: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('95', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('95', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('89', '1', '', '파킹박(야간)', '1', '0') ;",

            ],
    # 오렌지센터
    19197: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('16', '1', '', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('16', '1', '', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('31', '1', '', 'ppark(야간)', '999999999', '0') ;",
            ],
    # (하이파킹) 오라카이대학로
    19181: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('21', '1', '', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('21', '1', '', 'ppark', '999999999', '0');"
            ],
    # 건대 몰오브케이
    18997: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('04', '1', '', '파킹박 종일권', '1');",
            "javascript:applyDiscount('04', '1', '', '파킹박 종일권', '1');"
            ],
    # 	센터마크호텔
    14588: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('93', '1', '', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('93', '1', '', 'ppark', '999999999', '0');"
            ],
    #  (하이파킹) 삼성역 KTnG 대치타워
    19084: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('96', '1', '', '파킹박');",
            "javascript:applyDiscount('96', '1', '', '파킹박');",
            "javascript:applyDiscount('88', '1', '', '파킹박(야간)') ;",
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
    #  ING오렌지타워
    19085: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('99', '1', '', '파킹박', '1', '0');",
            "javascript:applyDiscount('92', '1', '', '파킹박(주말)', '1', '0');",
            "javascript:applyDiscount('91', '1', '', '파킹박(야간)', '1', '0');"
            ],
    #  KT&G수원 주차장
    22982: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('96', '1', '09|14|16|17|18|19|20|', '파킹박', '999999999', '0');",
            "javascript:applyDiscount('96', '1', '09|14|16|17|18|19|20|', '파킹박', '999999999', '0');"
            ],
    #  강남빌딩
    19271: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('07', '0', '01|02|10|11|12|13|14|15|', 'ppark', '1', '0');",
            "javascript:applyDiscount('07', '0', '01|02|10|11|12|13|14|15|', 'ppark', '1', '0');",
            "javascript:applyDiscount('91', '1', '', 'ppark(야간)', '1', '0');"
            ],
    #  양재공영
    19321: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('10', '1', '', '종일권(유료)', '1', '0');",
            "javascript:applyDiscount('10', '1', '', '종일권(유료)', '1', '0');",
            "javascript:applyDiscount('10', '1', '', '종일권(유료)', '1', '0');"
            ],
    #  동산마을공영
    19276: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '1', '0');",
            ],
    #  신논현역 W타
    12124: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('94', '1', '', '파킹박');",
            "javascript:applyDiscount('94', '1', '', '파킹박');",
            "javascript:applyDiscount('81', '1', '', '파킹박(야간)');",
            ],
    #  D타워
    19325: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('14', '1', '11|', 'ppark', 'Y');",
            "javascript:applyDiscount('14', '1', '11|', 'ppark', 'Y');",
            "javascript:applyDiscount('17', '1', '11|', 'ppark(야간)', 'Y');",
            ],
    #  반포동방음언덕형공영
    19273: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '05|', 'PPark', '1', '0');",
            "javascript:applyDiscount('08', '1', '05|', 'PPark', '1', '0');",
            "javascript:applyDiscount('08', '1', '05|', 'PPark', '1', '0');",
            ],
    # (하이시티파킹) 수원역전시장
    19324: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('09', '1', '04|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('09', '1', '04|', 'ppark', '999999999', '0');",
            "",
            ],
    # 그랜드센트럴
    19364: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('08', '1', '01|', 'ppark', '999999999', '0');",
            "javascript:applyDiscount('91', '1', '', 'ppark(야간)', '999999999', '0'); ",
            ],
    # 미성빌딩
    19266: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('12', '1', '04|09|03|06|02|01|05|10|11|13|14|97|98|', 'ppark');",
            "javascript:applyDiscount('12', '1', '04|09|03|06|02|01|05|10|11|13|14|97|98|', 'ppark');",
            "",
            ],
    # NH농협은행광명시지부
    19329: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('07', '1', '01|15|16|', 'ppark', '1', '0');",
            "javascript:applyDiscount('07', '1', '01|15|16|', 'ppark', '1', '0');",
            "javascript:applyDiscount('91', '1', '', 'ppark(야간)', '1', '0');",
            ],
    # (하이시티파킹) 역삼우정에쉐르2차
    19374: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('08', '1', '04|', 'ppark', '1', '0');",
            "javascript:applyDiscount('08', '1', '04|', 'ppark', '1', '0');",
            "",
            ],

    # (하이파킹) 더프라임타워
    16001: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "",
            "javascript:applyDiscount('17', '5', '16|', '파킹박(주말)', '999934499');",  # 주말1일권
            "",
            ],

    # (하이파킹) 서대문 NH농협생명 빌딩2
    19122: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('99', '1', '01|', '파킹박', '1', '0');",  # 평일1일권
            "javascript:applyDiscount('99', '1', '01|', '파킹박', '1', '0');",  # 주말1일권
            "javascript:applyDiscount('91', '1', '', '파킹박(야간)', '1', '0');",  # 심야권
            ],

    # (하이파킹) 서울역 주차장
    20864: ["user_id", "password", "//*[@id='login_form']/table[2]/tbody/tr[1]/td[3]/input",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('12', '', '5', '01|', 'ppark', '1', '0');",  # 평일1일권
            "",
            "",
            ],
    # (하이파킹) 디아뜨갤러리 1차 updated web
    19170: ["user_id", "password", "//input[@type='button']",
            "license_plate_number",  "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('07', 'CP0802', '1', '01|', 'ppark', '999999999', '0') ",  # 평일1일권
            "",
            "",],

    # 분당서현빌딩
    19204: ["user_id", "password", "//input[@type='button']",
            "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
            "chk",
            "javascript:applyDiscount('92', '1', '', 'ppark', '999995999')  ",  # 평일1일권
            "javascript:applyDiscount('95', '1', '', 'ppark(야간)', '999995999') ",#야간권
            "", ],
     # 현대인텔렉스
     15111: ["user_id", "password", "//input[@type='button']",
                "license_plate_number", "//*[@id='search_form']/table/tbody/tr/td[1]/table/tbody/tr/td/input[2]",
                "chk",
                "javascript:applyDiscount('92', '1', '', 'ppark', '999995999')  ",  # 평일1일권
                "javascript:applyDiscount('95', '1', '', 'ppark(야간)', '999995999') ",  # 야간권
                "", ],
}


def get_har_in_script(park_id, ticket_name):
    if ticket_name[-3:] == "심야권" or ticket_name[-3:] == "야간권":
        return mapIdToWebInfo[park_id][WebInfo.night]
    elif ticket_name == "평일1일권":
        return mapIdToWebInfo[park_id][WebInfo.weekday]
    elif ticket_name == "주말1일권" or ticket_name == "토요일권" or ticket_name == "일요일권":
        return mapIdToWebInfo[park_id][WebInfo.weekend]
    else:
        if park_id == Parks.WISE_PARK:  # 와이즈파크
            if ticket_name == "3시간권":
                return mapIdToWebInfo[park_id][WebInfo.methodHarIn3]
            else:
                return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]

        elif park_id == Parks.GUUI_WELLTZ:
            if str(ticket_name).endswith("연박권"):
                return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]

        elif park_id == Parks.ULGI_TWIN_TOWER:
            if ticket_name == "3시간권":
                return mapIdToWebInfo[park_id][9]
        elif park_id == Parks.W_SQARE:
            if ticket_name == "저녁권":
                return mapIdToWebInfo[park_id][WebInfo.night]
        else:
            # todo 요일 구분이 필요없는 현장 1969, 2868
            if Util.get_week_or_weekend() == 0:
                return mapIdToWebInfo[park_id][WebInfo.methodHarIn1]
            else:
                return mapIdToWebInfo[park_id][WebInfo.methodHarIn2]


def web_har_in(target, driver):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]
    park_type = ParkType.get_park_type(park_id)

    if park_id == 20864 and ticket_name != "평일1일권":
        print("서울역주차장 연박권")
        return False
    if park_id == 16001 and ticket_name != "주말1일권":
        print("더프라임타워 연박권")
        return False

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
                        driver.find_element_by_id(web_info[WebInfo.btnItem]).click()
                        harin_script = get_har_in_script(park_id, ticket_name)
                        driver.execute_script(harin_script)
                        return True

                return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
