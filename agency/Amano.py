# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoSuchElementException

import Util
import Colors
from park import ParkUtil, ParkType, Parks
import WebInfo
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.keys import Keys

mapIdToWebInfo = {
    # T타워 남산트라팰리스
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
    # 동익드미라벨
    18973: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#tblList > tbody > tr",
            "31",
            "",
            "",
            "javascript:document.getElementById('btnSave').click",
            "",
            ""
            ],

    # 와이플러스
    19028: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//input[@type='button']",  # "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "15",  # 당일권(파킹셰어) (판매 : 19000 )
            "9",  # 주말 24시간권
            "",
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "10"  # 3시간권
            ],
    # 파크엠 1일권
    19121: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "19",  # 평일1일권
            "20",  # 주말1일권
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
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "18"  # 3시간권
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
            "29",  # 주말1일권
            "30",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "31"  # 주말 3시간권
            ],
    # 포도몰 PODO_MALL
    11558: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "11",  # 12시간
            "11",  # 12시간 (12) 주말 12시간
            "",
            "javascript:document.getElementById('discountTypeValue').click",
            "3"  # 3시간할인
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
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "7"  # 3시간권 (판매 : 6000 )
            ],
    # 트윈트리
    12868: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "20",  # 당일권(평일) (판매 : 12000 )
            "21",  # 당일권(주말) (판매 : 8700 )
            "",
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "22"  # 6시간권 (판매 : 8000 )
            ],
    # 골든타워
    18577: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[4]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "838",  # 종일권(평일) (판매 : 8000 )
            "839",  # 종일권(주말) (판매 : 5000 )
            "",
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "129",  # 완전무료
            ],
    # JS호텔 분당
    19155: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "16",  # 종일권
            "16",  # 종일권
            "",  #
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "14"  # 3시간권
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
            "7",  # 토/일/공휴일 종일권
            "",
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "5",  # 4시간권
            "8"  # 토/일/공휴일 2시간
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
            "15",  # 야간권
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "12",  # 3시간권
            "11",  # 5시간권
            "10"  # 12시간권
            ],
    # (자주식)교대역 하림인터내셔날
    19029: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "21",  # 평일당일권(파킹셰어) (판매 : 20000 )
            "22",  # 주말당일권(파킹셰어) (판매 : 10000 )
            "23",  # 심야권(파킹셰어) (판매 : 5000 )
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "24",  # 2시간권(파킹셰어) (판매 : 10000 )
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
            "",
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "17",  # 3시간권
            "16"  # 2시간권
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
            "",  #
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "15",  # 3시간권
            "5"  # 2시간권
            ],
    # 오목교주차장
    19235: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "2",  # 평일종일권(파킹셰어)
            "",  #
            "",  #
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "5",  # 3시간권
            "4"  # 2시간권
            ],
    # 마곡류마타워2
    19234: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "5",  # 평일종일권(파킹셰어)
            "8",  # 종일권(주말) (판매 : 6000 )
            "",  #
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "7"  # 3시간권
            ],
    # 눈스퀘어
    19247: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "19",  # 평일1일권 1호기
            "20",  # 주말권
            "20",  # 평일1일권 2호기
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
            "19",  # 야간권(PS)
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
    # # 건국빌딩
    # 19206: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
    #         "schCarNo", "//*[@id='sForm']/input[3]",
    #         "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
    #         "16",  # 저녁권
    #         "17",  # 심야권
    #         "",  #
    #         "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    #         ],
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
            "4",  # 파킹셰어 야간권 (판매 : 5000 )
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
    19334: ["userId", "userPwd", "//*[@id='btnLogin']",
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
            ],
    # 종로 더케이손해보험
    2810: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
           "schCarNo", "//*[@id='sForm']/input[3]",
           "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
           "9",  # 평일 종일권
           "10",  #
           "",
           "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
           "8"  # 유료 3시간
           ],
    # 합정역 청년주택
    19328: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "13",  # 당일권(파킹셰어)
            "",  #
            "13",  # 심야권(파킹셰어) (판매 : 5500 )
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 롯데시티호텔명동
    19336: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "6",  # 당일권 (판매 : 20000 )
            "",  #
            "",
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "5",  # 3시간권 (판매 : 7000 )
            "4"  # 2시간권 (판매 : 5000 )
            ],
    # 강남파이낸스프라자
    18945: ["userId", "userPwd", "//*[@id='loginForm']/li[3]/input",
            "schCarNo", "//*[@id='sForm']/input[4]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "",  #
            "812",  # 주말종일권 (판매 : 5000 )
            "811",  # 심야권 (판매 : 7000 )
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 그레이스타워
    45304: ["userId", "userPwd", "//*[@id='loginForm']/li[3]/input",
            "schCarNo", "//*[@id='sForm']/input[4]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "775",  # 파킹셰어평일당일권 (판매 : 13000 )
            "",  #
            "",
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],
    # 파인에비뉴
    16212: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "11",  # 평일당일권(파킹셰어) (판매 : 20000 )
            "9",
            "8",  # 평일 심야권 (판매 : 7000 )
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "10"  # 평일 3시간권 (판매 : 10000 )
            ],
    # 동신교회
    16096: ["userId", "userPwd", """//*[@id="loginForm"]/li[3]/input""",
            "schCarNo", "//*[@id='sForm']/input[4]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "11",  # 평일당일권(파킹셰어) (판매 : 20000 )
            "10",  # 평일 3시간권 (판매 : 10000 )
            "",
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            ""
            ],

    # 유림트윈파크(하이파킹)
    19397: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "7",
            "7",
            "",
            "javascript:document.getElementById('discountTypeValue').click"
            ],
    # 뉴욕프라자주차장(마두역)
    45010: ["userId", "userPwd", "//*[@id='loginForm']/li[3]/input",
            "schCarNo", "//*[@id='sForm']/input[4]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "848",  # 당일권(평일)
            "",
            "",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",
            "",
            "847"  # 2시간권(파킹셰어)
            ],

    # 송파빌딩
    12373: ["userId", "userPwd", "//*[@id='loginForm']/li[3]/input",
            "schCarNo", "//*[@id='sForm']/input[4]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "",  # 당일권(평일)
            "812",
            "",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",
            "",
            "847"  # 2시간권(파킹셰어)
            ],

    # 돈암동일하이빌
    19130: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "14",  # 24시간/당일권(평일)
            "",
            "15",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",
            "11",  # 2시간권(파킹셰어)
            "12"  # 3시간권(파킹셰어)
            ],

    # 미사메디피아타워
    19407: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "",  # 24시간/당일권(평일)
            "",
            "15",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",
            "",  # 2시간권(파킹셰어)
            ""  # 3시간권(파킹셰어)
            ],

    # 상암DDMC
    19391: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "9",  # 24시간/당일권(평일)
            "9",
            "",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",
            "",  # 2시간권(파킹셰어)
            ""  # 3시간권(파킹셰어)
            ],

    # 홈런 주차장
    19371: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "11",  # 12시간 평일
            "12",  # 12시간 주말
            "",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",
            "13",  # 5시간권
            ""
            ],
    # (안국역) 삼환빌딩 주차장
    12817: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "11",  # 평일1일권
            "12",  # 주말1일권
            "",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",
            "",  # 2시간권
            ""
            ],

    # 상암 전자회관
    19376: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "",  #
            "14",  # 주말1일권
            "13",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",
            "",
            ""
            ],
    # NC백화점 강서점
    19333: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "8",  # 평일1일권
            "8",  # 주말1일권
            "",
            "javascript:document.getElementById('discountTypeValue').click",
            "",
            ""
            ],

    # 북한연구소
    18946: ["userId", "userPwd", "//*[@id='loginForm']/li[3]/input",
            "schCarNo", "//*[@id='sForm']/input[4]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "808",  # 평일1일권
            "",  # 주말1일권
            "",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",
            "",
            ""
            ],

    # NC백화점 중앙로점
    19335: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "6",  # 평일1일권
            "6",  # 주말1일권
            "",
            "javascript:document.getElementById('discountTypeValue').click",
            "",
            ""
            ],

    # T412 빌딩(구 대치2빌딩)(선릉역)
    19064: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "",
            "",
            "24",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click",
            "",
            ""
            ],

}

amano_need_log_out = [
    Parks.GOLDEN_TOWER,
    Parks.GANG_NAM_FINANCE,
    Parks.HAP_JEONG_STATION_YOUTH_HOUSE,
    Parks.SONGPA_BUILDING,
    Parks.ACE_TOWER,
    19130,
    Parks.URIM_TWIN_PARK,
    Parks.SUN_HWA_BUILDING,
    19391,
    18946
]

have_not_tree_time = {
    Parks.T_TOWER,
    Parks.TWIN_TREE,
    Parks.GOLDEN_TOWER,
    Parks.JANG_AN_SPIZON,
    Parks.HARIM_INTERNATIONAL,
    Parks.NC_GANG_NAM,
    Parks.NICE_HONG_MUN_KWAN,
    19391
}


def log_out_web(park_id, driver):
    if park_id in amano_need_log_out:
        driver.execute_script("javascript:logout();")
        driver.implicitly_wait(3)
        driver.find_element_by_xpath("//*[@id='modal-window']/div/div/div[3]/a[2]").click()
        Util.sleep(3)
        print(Colors.BLUE + "로그아웃" + Colors.ENDC)


def get_har_in_value(park_id, ticket_name):
    web_info = mapIdToWebInfo[park_id]

    if ticket_name[-3:] == "심야권" or ticket_name[-3:] == "야간권":
        return web_info[WebInfo.night]
    elif ticket_name == "평일1일권":
        return web_info[WebInfo.weekday]
    elif ticket_name == "주말1일권" or ticket_name == "토요일권" or ticket_name == "일요일권":
        return web_info[WebInfo.weekend]
    else:
        if park_id not in have_not_tree_time:
            if ticket_name[-4:] == "3시간권":
                return web_info[WebInfo.three]
            elif Util.get_week_or_weekend() == 0:
                return web_info[WebInfo.weekday]
            else:
                return web_info[WebInfo.weekend]
        else:
            if park_id == Parks.T_TOWER:
                if ticket_name == "금토일연박권" \
                        or ticket_name == "3일권":
                    return web_info[11]
                elif ticket_name[-3:] == "연박권" \
                        or ticket_name == "2일권":
                    return web_info[10]
                elif str(ticket_name).startswith("일주차"):
                    return web_info[WebInfo.weekday]

            elif park_id == Parks.TWIN_TREE \
                    or park_id == Parks.JIN_YANG_BUILDING:
                if ticket_name == "6시간권":
                    return web_info[10]

            elif park_id == Parks.JANG_AN_SPIZON:
                if ticket_name == "4시간권":
                    return web_info[10]

            elif park_id == Parks.YEOKSAM_BUILDING:
                if str(ticket_name).startswith("주간권"):
                    return web_info[12]
                elif str(ticket_name).startswith("5시간권"):
                    return web_info[11]
                elif str(ticket_name).startswith("야간권"):
                    return web_info[8]

            elif park_id == Parks.JAYANG_PALACE \
                    or park_id == Parks.OMOK_BRIDGE \
                    or park_id == Parks.LOTTE_CITY_HOTEL_MYEONG_DONG \
                    or park_id == Parks.NEWYORK_PLAZA:
                if ticket_name[-4:] == "2시간권":
                    return web_info[11]

            elif park_id == Parks.NC_GANG_NAM:
                if ticket_name[-3:] == "1일권":
                    return web_info[WebInfo.methodHarIn1]
                elif ticket_name[-3:] == "2일권":
                    return web_info[10]
                elif ticket_name[-3:] == "3일권":
                    return web_info[11]
                elif ticket_name[-3:] == "4일권":
                    return web_info[12]
                elif ticket_name[-3:] == "5일권":
                    return web_info[13]

            elif park_id == Parks.NICE_HONG_MUN_KWAN:
                if ticket_name == "4시간권":
                    return web_info[10]
                elif ticket_name == "8시간권":
                    return web_info[11]

            elif park_id == 19130:
                if ticket_name == "2시간권":
                    return web_info[10]
                elif ticket_name == "3시간권":
                    return web_info[11]
            # elif park_id == Parks.DONGSIN_CHURCH:
            #     if ticket_name == "평일1일권":
            #         return web_info[]
            #     elif ticket_name == "3시간권":
            #         return web_info[]

            elif park_id == 19247:  # 아마노 눈스퀘어
                if ticket_name == "평일1일권(1호기)":
                    return web_info[6]
                elif ticket_name == "평일1일권(2호기)":
                    return web_info[7]

            elif park_id == 19371:
                if ticket_name == "12시간권":
                    if Util.get_week_or_weekend() == 0:
                        return web_info[WebInfo.weekday]
                    else:
                        return web_info[WebInfo.weekend]
                elif ticket_name == "5시간권":
                    return web_info[10]

            else:
                if Util.get_week_or_weekend() == 0:
                    return web_info[WebInfo.weekday]
                else:
                    return web_info[WebInfo.weekend]


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

    if park_id == Parks.NICE_HONG_MUN_KWAN or \
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

    # 동익드미라벨 연박권
    if park_id == 18973 and ticket_name != "1일권":
        print("1일권이 아님")
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
            # todo 현재 URL을 가지고와서 비교 후 자동로그인

            # 재접속이 아닐 때, 그러니까 처음 접속할 때
            if ParkUtil.first_access(park_id, driver.current_url):
                web_har_in_login(driver, park_id)

            Util.close_popup(driver)
            Util.close_modal(driver)

            if park_id == 12050:
                driver.find_element_by_id(web_info[WebInfo.inputSearch]).clear()
            driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
            Util.sleep(3)

            driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()

            Util.sleep(1)

            # 차량번호 검색
            if ParkUtil.check_search(park_id, driver):
                driver.implicitly_wait(3)
                try:
                    driver.find_element_by_css_selector(web_info[WebInfo.btnItem]).click()
                except NoSuchElementException:
                    log_out_web(park_id, driver)
                    return False

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                # T타워 / 동익드미라벨
                if park_id == Parks.T_TOWER or park_id == 18973:
                    car_num = soup.find(id='tblList')
                else:
                    car_num = driver.find_element_by_xpath('''//*[@id="carNo"]''')

                car_text = car_num.text
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

                        # T타워 / 동익드미라벨
                        if park_id == Parks.T_TOWER or park_id == 18973:
                            pe_id = driver.find_element_by_id('peId')
                            driver.execute_script("arguments[0].value = '" + pe_id_value + "';", pe_id)
                            car_no = driver.find_element_by_id('carNo')
                            driver.execute_script("arguments[0].value = '" + car_no_value + "';", car_no)
                            discount_type = driver.find_element_by_id('discountType')
                            driver.execute_script("arguments[0].value = '" + discount_type_value + "';",
                                                  discount_type)

                        # 비고에 텍스트 입력
                        if park_id == Parks.GOLDEN_TOWER or park_id == Parks.GANG_NAM_FINANCE:
                            element_text_area = driver.find_element_by_id('memo')
                            Util.sleep(1)
                            element_text_area.send_keys("11")
                            Util.sleep(1)

                        # 홍문관
                        if park_id == Parks.NICE_HONG_MUN_KWAN:
                            create_date = target[4]
                            if not ParkUtil.check_nice_date(park_id, create_date, driver):
                                print(Colors.RED + "입차 후 결제입니다." + Colors.ENDC)
                                return False
                            print(Colors.RED + "입차 전 결제입니다." + Colors.ENDC)

                        # 차량번호 일치하는지 확인
                        if ParkUtil.check_same_car_num(park_id, ori_car_num, driver):
                            har_in_script = web_info[WebInfo.methodHarInFunc].replace("discountTypeValue",
                                                                                      discount_type_value) + "()"
                            print(Colors.RED + har_in_script + Colors.ENDC)
                            Util.sleep(2)
                            driver.execute_script(har_in_script)
                            Util.sleep(2)
                            Util.close_modal(driver)
                            log_out_web(park_id, driver)

                            return True

                log_out_web(park_id, driver)
                return False

            return False
        else:
            print(Colors.BLUE + "현재 웹할인 페이지 분석이 되어 있지 않는 주차장입니다." + Colors.ENDC)
            return False
    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)
        return False
