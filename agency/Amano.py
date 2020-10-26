# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoSuchElementException

import Util
import ParkType
import Colors
import ParkUtil
import WebInfo
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.keys import Keys

Parks = ParkType.Parks

mapIdToWebInfo = {
    # amano 남산트라펠리스
    16239: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//input[@type='button']",
            "#tblList > tbody > tr",
            "5",  # 1일권(판매:8000 차감 : 1440 )
            "5",  # 1일권(판매:8000 차감 : 1440 )
            "4",  # 심야권(판매:0 차감 : 720 )
            "javascript:document.getElementById('btnSave').click",
            "6",  # 2일권(판매:16000 차감 : 2880 )
            "7",  # 3일권(판매:24000 차감 : 4320 )
            # "#article > div > div.stitle > p > a > img"
            ],
    # 와이플러스
    19028: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//input[@type='button']",  # "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "8",  # 평일 24시간권
            "9",  # 주말 24시간권
            "10",  # 3시간권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            # "body > div:nth-child(4) > table > tbody > tr:nth-child(1) > td:nth-child(3) > button"
            ],
    # 파크엠 1일권
    19121: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "8",  # 평일1일권
            "10",  # 평일1일권
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 파크엠 야간권
    19124: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "9",  # 평일 야간권 (판매 : 8000 )
            "9",  # 평일 야간권 (판매 : 8000 )
            "9",  # 평일 야간권 (판매 : 8000 )
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # ECC
    12050: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "3",  # 평일1일권
            "4",  # 주말1일권
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 퍼시픽타워
    19151: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "15",  # 평일1일권
            "16",  # 주말1일권
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 서울기록원
    19128: ["userId", "userPwd", "btnLogin",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "4",  # 평일1일권
            "",  # 주말1일권 X
            "7",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 강남 N타워
    19077: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "28",  # 평일1일권
            "22",  # 주말1일권
            "30",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 포도몰 PODO_MALL
    11558: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "",  # 평일1일권 value : 5
            "",
            "11",  # 12시간권
            "javascript:document.getElementById('discountTypeValue').click"
            ],
    # SK 명동
    14618: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "13",  # 8 : 일일권(16시간), 13 : 16시간권
            "11",  # 주말1일권
            "10",  # 야간권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 웨스트게이트
    18913: ["userId", "userPwd", "btnLogin",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "4",  # 종일 평일(자주식)
            "",  # 종일 주말
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 트윈트리
    12868: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "14",  # 앱1일권
            "",
            "5",  # 6시간권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 골든타워
    18577: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[4]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "129",  # 완전무료
            "",
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # JS호텔 분당
    19155: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "16",  # 종일권
            "16",  # 종일권
            "14",  # 3시간권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # ECC
    19119: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "3",  # 평일1일권
            "4",  # 주말1일권
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # (장한평역) 장안스피존
    19110: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "3",  # 평일1일권
            "",
            "5",  # 4시간권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 진양빌딩 (서대문역)
    19000: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "5",  # 평일1일권
            "",
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 	강남역 역삼빌딩(세무서)
    19173: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "9",  # 24hr(플랫폼)
            "14",  # 주말(플랫폼)
            "10",  # 12시간권
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "11",  # 5시간권
            "12",  # 3시간권
            "13"  # 야간권
            ],
    # (자주식)교대역 하림인터내셔날
    19029: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "12",  # 평일1일권
            "14",  # 주말1일권
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 신라스테이 광화문(G타워)
    18936: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "20",  # 파킹박 종일권
            "20",  # 파킹박 종일권
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 마곡NY타워
    19190: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "2",  # 파킹박 종일권
            "2",  # 파킹박 종일권
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 서대문 에이스타워(KG타워)
    16209: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "12",  # 종일권(평일)
            "13",  # 종일권(주말)
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 자양래미안프리미어팰리스
    19193: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "15",  # 종일권
            "18",  # 종일권(주말)(파킹셰어) (판매 : 5000 )
            "16",  # 2시간권
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "17"  # 3시간권
            ],
    # 홍익대학교 홍문관
    19208: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "15",  # 평일1일권
            "17",  # 주말1일권
            "16",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "18",  # 4시간권
            "19"  # 8시간권
            ],
    # 충정로청년주택
    19191: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "2",  # 평일종일권(파킹셰어)
            "",  #
            "5",  # 2시간권
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "15"  # 3시간권
    ],
    # 오목교주차장
    19235: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "2",  # 평일종일권(파킹셰어)
            "",  #
            "4",  # 2시간권
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "5"  # 3시간권
    ],
    # 마곡류마타워2
    19234: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "5",  # 평일종일권(파킹셰어)
            "8",  # 종일권(주말) (판매 : 6000 )
            "7",  # 3시간권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # 눈스퀘어
    19247: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "1",  # 15시간권
            "1",  # 15시간권
            "",  #
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # 정안빌딩
    19267: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "9",  # ppar
            "9",  # ppark
            "",  #
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # 광화문S타워
    19250: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "18",  # 종일권(PS)
            "18",  # 종일권(PS)
            "",  #
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # MDM타워 당산
    19239: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "8",  # 24시간유료 (판매 : 15000 )
            "8",  # 24시간유료 (판매 : 15000 )
            "",  #
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # 하나금융 투자빌딩
    19040: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "",  #
            "3",  # 주말권
            "2",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # 건국빌딩
    19206: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "16",  # 저녁권
            "17",  # 심야권
            "",  #
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # 스테이트타워남산
    19258: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "15",  # 종일권(평일)
            "16",  # 파킹셰어 종일권(주말) (판매 : 10000 )
            "14",  # 야간권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # 서교동 나대지
    19238: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "4",  # 파킹쉐어 16시간
            "4",  # 파킹쉐어 16시간
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # 건대부중(건국대학교사범대학부속중학교)
    19210: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "3",  # 파킹셰어 종일권 (판매 : 10000 )
            "3",  # 파킹셰어 종일권 (판매 : 10000 )
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # 건국빌딩
    19331: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "7",  # 24시간권
            "7",  # 24시간권
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # 감신대
    19209: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "",  #
            "2",  # 종일권(주말) (판매 : 5000 )
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    ],
    # NC 강남점
    19334: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "8",  # 당일권 (판매 : 12000 )
            "8",  # 당일권 (판매 : 12000 )
            "",
            "javascript:document.getElementById('discountTypeValue').click",
            "9",  # 2일권 (판매 : 24000 )
            "10",  # 3일권 (판매 : 35000 )
            "11",  # 4일권 (판매 : 45000 )
            "12",  # 5일권 (판매 : 55000 )
    ]
}

amano_auto_search_one = [
    Parks.SK_MYEONGDONG,
    Parks.GOLDEN_TOWER,
    Parks.PARK_M,
    Parks.PARK_M_NIGHT,
    Parks.N_TOWER,
    Parks.JS_HOTEL,
    Parks.SINRA_STAY_G_TOWER,
    Parks.HONG_MUN_KWAN,
    Parks.CHUNGJEONGNO_HOUSE,
    Parks.OMOK_BRIDGE,
    Parks.MAGOK_RUMA_2,
    Parks.HANA_TOOJA_BUILDING,
    Parks.KUN_KUK_BUILDING,
    Parks.STATE_TOWER_NAMSAN,
    Parks.SEOGYO_DONG_NADAEJI,
    Parks.HUMAX_VILLAGE
]

amano_auto_search_two = [
    Parks.PACIFIC_TOWER,
    Parks.SEOUL_GIROKWON,
    Parks.TWIN_TREE,
    Parks.WEST_GATE,
    Parks.JIN_YANG_BUILDING,
    Parks.YEOKSAM_BUILDING,
    Parks.HARIM_INTERNATIONAL,
    Parks.NY_TOWER,
    Parks.JEONGAN_BUILDING,
    Parks.GWANG_HWA_MUN_S_TOWER,
    Parks.MDM_TOWER_DANG_SAN,
    Parks.PODO_MALL,
    Parks.ACE_TOWER,
    Parks.GS_GUN_GUK_BUILDING,
    Parks.GAM_SIN_DAE,
    Parks.NC_GANG_NAM
]

amano_pass = [
    Parks.PARK_M,
    Parks.PARK_M_NIGHT,
    Parks.ECC,
    Parks.Y_PLUS,
    Parks.PACIFIC_TOWER,
    Parks.SEOUL_GIROKWON,
    Parks.N_TOWER,
    Parks.SK_MYEONGDONG,
    Parks.WEST_GATE,
    Parks.TWIN_TREE,
    Parks.GOLDEN_TOWER,
    Parks.JS_HOTEL,
    Parks.ECC_MONTH,
    Parks.JANG_AN_SPIZON,
    Parks.JIN_YANG_BUILDING,
    Parks.YEOKSAM_BUILDING,
    Parks.HARIM_INTERNATIONAL,
    Parks.SINRA_STAY_G_TOWER,
    Parks.NY_TOWER,
    Parks.JAYANG_PALACE,
    Parks.HONG_MUN_KWAN,
    Parks.CHUNGJEONGNO_HOUSE,
    Parks.OMOK_BRIDGE,
    Parks.MAGOK_RUMA_2,
    Parks.NON_SQUARE,
    Parks.JEONGAN_BUILDING,
    Parks.GWANG_HWA_MUN_S_TOWER,
    Parks.MDM_TOWER_DANG_SAN,
    Parks.PODO_MALL,
    Parks.ACE_TOWER,
    Parks.HANA_TOOJA_BUILDING,
    Parks.KUN_KUK_BUILDING,
    Parks.STATE_TOWER_NAMSAN,
    Parks.SEOGYO_DONG_NADAEJI,
    Parks.KUN_KUK_MIDDLE,
    Parks.HUMAX_VILLAGE,
    Parks.GS_GUN_GUK_BUILDING,
    Parks.GAM_SIN_DAE,
    Parks.NC_GANG_NAM
]

amano_need_log_out = [
    Parks.GOLDEN_TOWER
]


def log_out_web(park_id, driver):
    if park_id in amano_need_log_out:
        driver.execute_script("javascript:logout();")
        driver.implicitly_wait(3)
        driver.find_element_by_xpath("//*[@id='modal-window']/div/div/div[3]/a[2]").click()
        Util.sleep(3)
        print(Colors.BLUE + "로그아웃" + Colors.ENDC)


def get_har_in_value(park_id, ticket_name):
    web_info = mapIdToWebInfo[park_id]
    discount_type_value = ""

    if park_id == Parks.T_TOWER:
        if ticket_name == "심야권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        elif ticket_name[-3:] == "1일권":
            discount_type_value = web_info[WebInfo.methodHarIn1]
        elif ticket_name == "금토일연박권":
            discount_type_value = web_info[11]
        elif ticket_name[-3:] == "연박권":
            discount_type_value = web_info[10]

    elif park_id == Parks.Y_PLUS or park_id == Parks.JS_HOTEL:
        if ticket_name == "3시간권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        elif ticket_name == "16시간권":
            discount_type_value = web_info[WebInfo.methodHarIn1]
        elif ticket_name[-3:] == "1일권":
            if Util.get_week_or_weekend() == 0:
                discount_type_value = web_info[WebInfo.methodHarIn1]
            else:
                discount_type_value = web_info[WebInfo.methodHarIn2]

    elif park_id == Parks.SK_MYEONGDONG:
        if ticket_name == "3시간권":
            discount_type_value = web_info[WebInfo.methodHarIn1]
        elif ticket_name == "심야권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        elif ticket_name == "16시간권":
            discount_type_value = web_info[WebInfo.methodHarIn1]
        else:
            discount_type_value = web_info[WebInfo.methodHarIn1]

    elif park_id == Parks.PARK_M or park_id == Parks.WEST_GATE or park_id == Parks.PARK_M_NIGHT:
        if Util.get_week_or_weekend() == 0:
            discount_type_value = web_info[WebInfo.methodHarIn1]
        else:
            discount_type_value = web_info[WebInfo.methodHarIn2]

    elif park_id == Parks.PODO_MALL:
        if str(ticket_name).startswith("12시간"):
            discount_type_value = web_info[WebInfo.methodHarIn3]

    elif park_id == Parks.TWIN_TREE:
        if ticket_name == "6시간권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        else:
            discount_type_value = web_info[WebInfo.methodHarIn1]

    elif park_id == Parks.JANG_AN_SPIZON:
        if ticket_name == "4시간권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        else:
            discount_type_value = web_info[WebInfo.methodHarIn1]

    elif park_id == Parks.JIN_YANG_BUILDING:
        if ticket_name == "6시간권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        else:
            discount_type_value = web_info[WebInfo.methodHarIn1]

    elif park_id == Parks.YEOKSAM_BUILDING:
        if ticket_name[-3:] == "1일권":
            discount_type_value = web_info[WebInfo.methodHarIn1]
        elif str(ticket_name).startswith("주간권"):
            discount_type_value = web_info[WebInfo.methodHarIn3]
        elif str(ticket_name).startswith("5시간권"):
            discount_type_value = web_info[10]
        elif str(ticket_name).startswith("3시간권"):
            discount_type_value = web_info[11]
        elif str(ticket_name).startswith("야간권"):
            discount_type_value = web_info[12]
        else:
            if Util.get_week_or_weekend() == 0:
                discount_type_value = web_info[WebInfo.methodHarIn1]
            else:
                discount_type_value = web_info[WebInfo.methodHarIn2]

    elif park_id == Parks.JAYANG_PALACE:
        if ticket_name[-3:] == "1일권":
            if Util.get_week_or_weekend() == 0:
                discount_type_value = web_info[WebInfo.methodHarIn1]
            else:
                discount_type_value = web_info[WebInfo.methodHarIn2]
        elif ticket_name[-4:] == "2시간권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        elif ticket_name[-4:] == "3시간권":
            discount_type_value = web_info[10]

    elif park_id == Parks.HONG_MUN_KWAN:
        if ticket_name[-3:] == "1일권":
            if Util.get_week_or_weekend() == 0:
                discount_type_value = web_info[WebInfo.methodHarIn1]
            else:
                discount_type_value = web_info[WebInfo.methodHarIn2]
        elif ticket_name == "심야권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        elif str(ticket_name).startswith("4시간권"):
            discount_type_value = web_info[10]
        elif str(ticket_name).startswith("8시간권"):
            discount_type_value = web_info[11]
        else:
            discount_type_value = web_info[WebInfo.methodHarIn1]

    elif park_id == Parks.MAGOK_RUMA_2:
        if ticket_name[-4:] == "3시간권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        elif Util.get_week_or_weekend() == 0:
            discount_type_value = web_info[WebInfo.methodHarIn1]
        else:
            discount_type_value = web_info[WebInfo.methodHarIn2]

    elif park_id == Parks.HANA_TOOJA_BUILDING:
        if ticket_name == "심야권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        elif ticket_name == "주말1일권":
            discount_type_value = web_info[WebInfo.methodHarIn2]
        else:
            discount_type_value = web_info[WebInfo.methodHarIn1]

    elif park_id == Parks.KUN_KUK_BUILDING:
        if ticket_name[-3:] == "저녁":
            discount_type_value = web_info[WebInfo.methodHarIn1]
        elif ticket_name[-3:] == "심야권":
            discount_type_value = web_info[WebInfo.methodHarIn2]
        else:
            discount_type_value = web_info[WebInfo.methodHarIn3]

    elif park_id == Parks.STATE_TOWER_NAMSAN:
        if ticket_name[-3:] == "심야권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        elif ticket_name == "평일1일권":
            discount_type_value = web_info[WebInfo.methodHarIn1]
        elif ticket_name == "주말1일권":
            discount_type_value = web_info[WebInfo.methodHarIn2]

    # 오목교주차장
    elif park_id == Parks.OMOK_BRIDGE:
        if ticket_name[-4:] == "2시간권":
            discount_type_value = web_info[WebInfo.methodHarIn3]
        elif ticket_name[-4:] == "3시간권":
            discount_type_value = web_info[10]
        elif ticket_name == "평일1일권":
            discount_type_value = web_info[WebInfo.methodHarIn1]
        elif ticket_name == "주말1일권":
            discount_type_value = web_info[WebInfo.methodHarIn2]

    elif park_id == Parks.NC_GANG_NAM:
        if ticket_name[-3:] == "1일권":
            discount_type_value = web_info[WebInfo.methodHarIn1]
        elif ticket_name[-3:] == "2일권":
            discount_type_value = web_info[10]
        elif ticket_name[-3:] == "3일권":
            discount_type_value = web_info[11]
        elif ticket_name[-3:] == "4일권":
            discount_type_value = web_info[12]
        elif ticket_name[-3:] == "5일권":
            discount_type_value = web_info[13]

    else:
        if Util.get_week_or_weekend() == 0:
            discount_type_value = web_info[WebInfo.methodHarIn1]
        else:
            discount_type_value = web_info[WebInfo.methodHarIn2]

    return discount_type_value


def web_har_in_login(driver, park_id):
    web_info = mapIdToWebInfo[park_id]
    web_har_in_info = ParkUtil.get_park_lot_option(park_id)

    element_id = driver.find_element_by_name(web_info[WebInfo.inputId])
    element_id.clear()
    element_id.send_keys(web_har_in_info[WebInfo.webHarInId])

    if park_id in ParkType.parkTypeAmano:  # 19121
        element_pw = driver.find_element_by_name(web_info[WebInfo.inputPw])
    else:
        element_pw = driver.find_element_by_id(web_info[WebInfo.inputPw])

    element_pw.clear()
    element_pw.send_keys(web_har_in_info[WebInfo.webHarInPw])

    if park_id == Parks.HONG_MUN_KWAN or \
            park_id == Parks.YEOKSAM_BUILDING:
        driver.find_element_by_css_selector("#loginForm > li:nth-child(5) > input").click()
    elif park_id == Parks.SEOUL_GIROKWON or park_id == Parks.WEST_GATE:
        driver.find_element_by_id(web_info[WebInfo.btnLogin]).click()
        driver.implicitly_wait(3)
    elif park_id == Parks.NY_TOWER:
        Util.sleep(1)
        driver.find_element_by_id("btnLogin").click()
    elif park_id == Parks.GS_GUN_GUK_BUILDING:
        driver.find_element_by_id("btnLogin").click()
        Util.sleep(2)
    else:
        driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()


def web_har_in_login_seoul_girockwon(driver, park_id):
    web_info = mapIdToWebInfo[park_id]
    web_har_in_info = ParkUtil.get_park_lot_option(park_id)

    element_id = driver.find_element_by_name(web_info[WebInfo.inputId])
    element_id.clear()
    element_id.send_keys(web_har_in_info[WebInfo.webHarInId])


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
            # todo 현재 URL을 가지고와서 비교 후 자동로그인
            # print(driver.current_url)
            # 재접속이 아닐 때, 그러니까 처음 접속할 때
            if ParkUtil.first_access(park_id, driver.current_url):
                if park_id == Parks.NY_TOWER:
                    driver.implicitly_wait(3)
                    driver.find_element_by_xpath("//*[@id='modal-window']/div/div/div[3]/a[1]").click()
                    Util.sleep(3)

                web_har_in_login(driver, park_id)

            if park_id in amano_auto_search_one:
                driver.find_element_by_css_selector("#modal-window > div > div > div.modal-buttons > a").click()
            else:
                discount_url = login_url + ParkUtil.get_park_discount_url(park_type)
                driver.get(discount_url)

            driver.implicitly_wait(3)

            driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
            Util.sleep(3)

            if park_id in amano_auto_search_two:
                driver.find_element_by_css_selector("#modal-window > div > div > div.modal-buttons > a").click()

            driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()

            Util.sleep(1)

            if ParkUtil.check_search(park_id, driver):
                driver.implicitly_wait(3)
                driver.find_element_by_css_selector(web_info[WebInfo.btnItem]).click()

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                if park_id == ParkType.Parks.T_TOWER:
                    car_num = soup.find(id='tblList')  # 트라팰리스
                else:
                    car_num = soup.find("tr")  # 와이플러스 및 나머지

                car_text = car_num.get_text()
                text = re.sub('<.+?>', '', car_text, 0, re.I | re.S)
                trim_text = text.strip()

                if trim_text == "검색된 데이터가 없습니다.":
                    print(Colors.YELLOW + "검색된 데이터가 없습니다." + Colors.ENDC)
                else:
                    pe_id_value = trim_text[0:6]
                    car_num_divider = 6 + len(ori_car_num)
                    car_no_value = trim_text[6:car_num_divider]
                    # todo 평일 1일권인지 심야권인지 판별
                    discount_type_value = get_har_in_value(park_id, ticket_name)

                    if discount_type_value != "":
                        if park_id in amano_pass:
                            pass
                        else:
                            pe_id = driver.find_element_by_id('peId')
                            driver.execute_script("arguments[0].value = '" + pe_id_value + "';", pe_id)
                            car_no = driver.find_element_by_id('carNo')
                            driver.execute_script("arguments[0].value = '" + car_no_value + "';", car_no)
                            discount_type = driver.find_element_by_id('discountType')
                            driver.execute_script("arguments[0].value = '" + discount_type_value + "';",
                                                  discount_type)

                        if park_id == Parks.GOLDEN_TOWER or \
                                park_id == Parks.KUN_KUK_BUILDING:
                            element_text_area = driver.find_element_by_id('memo')
                            element_text_area.send_keys(Keys.TAB)
                            element_text_area.clear()
                            element_text_area.send_keys("1")
                            Util.sleep(1)

                        if ParkUtil.check_same_car_num(park_id, ori_car_num, driver):
                            har_in_script = web_info[WebInfo.methodHarInFunc].replace("discountTypeValue", discount_type_value) + "()"
                            print(Colors.RED + har_in_script + Colors.ENDC)
                            Util.sleep(2)
                            driver.execute_script(har_in_script)
                            Util.sleep(2)

                            try:
                                driver.find_element_by_css_selector(
                                    "#modal-window > div > div > div.modal-buttons > a").click()
                                Util.sleep(2)
                            except NoSuchElementException:
                                print(Colors.RED + "팝업(모달뷰)에 확인을 누를 수 없습니다." + Colors.ENDC)

                            log_out_web(park_id, driver)
                            return True

                log_out_web(park_id, driver)
                return False

            log_out_web(park_id, driver)
            return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
