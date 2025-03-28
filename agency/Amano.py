# -*- coding: utf-8 -*-
from telnetlib import EC

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import Util
import Colors
from park import ParkUtil, ParkType, Parks
import WebInfo
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

mapIdToWebInfo = {
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
            "15",  # 당일9권(파킹셰어)
            "16",  # 주말 9시간권
            "",
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수

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
    # 12050: ["userId", "userPwd", "//input[@type='submit']",
    #         "schCarNo", "//*[@id='sForm']/input[3]",
    #         "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
    #         "3",  # 평일1일권
    #         "4",  # 주말1일권
    #         "",
    #         "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
    #         ],

    # 서울기록원
    19428: ["userId", "userPwd", "btnLogin",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "4",  # 평일1일권
            "",  # 주말1일권 X
            "7",  # 심야권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            "9",  # 3시간권
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
            "19",
            "javascript:document.getElementById('discountTypeValue').click",  # 실행 함수
            "17",  # 3시간권
            "16"  # 2시간권
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

    # 서교동 나대지
    19238: ["userId", "userPwd", "//*[@id='loginForm']/li[4]/input",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "4",  # 파킹쉐어 16시간
            "4",  # 파킹쉐어 16시간
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

    # 효성레제스 오피스텔//*[@id="btnLogin"]///*[@id="sForm"]/input[3]
    18934: ["userId", "userPwd", "//*[@id='btnLogin']",
           "schCarNo", "//*[@id='sForm']/input[3]",
           "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
           "2",  # 24시간/당일권(평일)
           "",
           "",
           "javascript:document.getElementById('discountTypeValue').click"
           ],

    # 위워크선릉점
    #19892: ["userId", "userPwd", "//*[@id='btnLogin']",
    #       "schCarNo", "//*[@id='sForm']/input[3]",
    #       "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
    #       "7",  # 심야권
    #       "",
    #       "7",  # 심야권
    #       "javascript:document.getElementById('discountTypeValue').click",
    #       "7",  #심야권
    #       "7"  # 심야권
    #       ],

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
    # 12817: ["userId", "userPwd", "//*[@id='btnLogin']",
    #         "schCarNo", "//*[@id='sForm']/input[3]",
    #         "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
    #         "11",  # 평일1일권
    #         "12",  # 주말1일권
    #         "",  # 심야권
    #         "javascript:document.getElementById('discountTypeValue').click",
    #         "",  # 2시간권
    #         ""
    #         ],

    # 상암 전자회관
    19376: ["userId", "userPwd", "//*[@id='btnLogin']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "",  #
            "14",  # 주말1일권
            "14",  # 심야권
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

        # 메트로타워
        19437: ["userId", "userPwd", "//*[@id='btnLogin']",
                "schCarNo", "//*[@id='sForm']/input[3]",
                "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
                "9",  # 1일권
                "",  # 주말1일권
                "",  # 심야권
                "javascript:document.getElementById('discountTypeValue').click",
                "",
                ""
                ],
        # 니즈몰
        19451: ["userId", "userPwd", "//input[@type='submit']",
                "schCarNo", "//*[@id='sForm']/input[3]",
                "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
                "9",  # 평일 야간권 (판매 : 8000 )
                "9",  # 평일 야간권 (판매 : 8000 )
                "9",  # 평일 야간권 (판매 : 8000 )
                "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
                ],
        #교대역 동측 공영주차장(아이디값확인)
        19453: ["userId", "userPwd", "//input[@type='submit']",
                "schCarNo", "//*[@id='sForm']/input[3]",
                "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
                "4",  #
                "8",  #
                "8",  #
                "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
                ],
        # 여의도 우체국
        19438: ["userId", "userPwd", "//input[@type='submit']",
                "schCarNo", "//*[@id='sForm']/input[3]",
                "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
                "11",  # 평일 야간권 (판매 : 8000 )
                "11",  # 평일 야간권 (판매 : 8000 )
                "11",  # 평일 야간권 (판매 : 8000 )
                "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
                ],
        # 안양헤븐리치
        19017: ["userId", "userPwd", "//input[@type='submit']",
                "schCarNo", "//*[@id='sForm']/input[3]",
                "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
                "9",  # 평일 야간권 (판매 : 8000 )
                "11",  # 평일 야간권 (판매 : 8000 )
                "11",  # 평일 야간권 (판매 : 8000 )
                "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
                ],

        # 해동본타워
        19408: ["userId", "userPwd", "//input[@type='submit']",
                "schCarNo", "//*[@id='sForm']/input[3]",
                "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
                "15",
                "15",
                "15",
                "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
                ],
        # 운정메디컬프라자
        19455: ["userId", "userPwd", "//input[@type='submit']",
                "schCarNo", "//*[@id='sForm']/input[3]",
                "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
                "15",
                "15",
                "15",
                "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
                ],

        # 압구정 극동타워
        19061: ["userId", "userPwd", "//input[@type='submit']",
                "schCarNo", "//*[@id='sForm']/input[3]",
                "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
                "15",
                "15",
                "15",
                "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
                ],

        # ns홈쇼핑 별관(고급 x)
        19445: ["userId", "userPwd", "//input[@type='submit']",
                "schCarNo", "//*[@id='sForm']/input[3]",
                "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
                "9",#평일
                "7",#심야
                "8",#10시간
                "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
                ],

        # 현대델리안오피스텔
        19488: ["userId", "userPwd", "//input[@type='submit']",
                "schCarNo", "//*[@id='sForm']/input[3]",
                "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
                "8",
                "8",
                "8",
                "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
                ],

        # 당산동청년주택
        19869: ["userId", "userPwd", "//input[@type='submit']",
                "schCarNo", "//*[@id='sForm']/input[3]",
                "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
                "9",#당일권
                "",  # 주말권 (주말권이 없는 경우 빈 값으로 유지)
                "",  # 추가 항목 (예: 심야권, 현재 값이 없는 경우 빈 값)
                "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
                ],

        # SK 명동
        14618: ["userId", "userPwd", "//input[@type='submit']",
            "schCarNo", "//*[@id='sForm']/input[3]",
            "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected",
            "13",  # 8 : 일일권(16시간), 13 : 16시간권
            "11",  # 주말1일권
            "10",  # 야간권
            "javascript:document.getElementById('discountTypeValue').click"  # 실행 함수
            ],


}

amano_need_log_out = [
    Parks.HAP_JEONG_STATION_YOUTH_HOUSE,
    Parks.SONGPA_BUILDING,
    Parks.ACE_TOWER,
    18934,
    Parks.URIM_TWIN_PARK,
    Parks.SUN_HWA_BUILDING,
    18946,
    19438,
    19488,
    19437
]

have_not_tree_time = {
    Parks.TWIN_TREE,
    Parks.JANG_AN_SPIZON,
    Parks.HARIM_INTERNATIONAL,
    Parks.NC_GANG_NAM
}
def handle_popup(driver):
    try:
        # 팝업 루트 요소 확인
        popup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="modal-window"]'))
        )
        if popup.is_displayed():
            print("팝업이 감지되었습니다.")
            try:
                dismiss_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="modal-window"]/div/div/div[3]/a[1]'))
                )
                dismiss_button.click()
                print("'7일간 보지 않기' 버튼 클릭 완료.")
            except NoSuchElementException:
                print("'7일간 보지 않기' 버튼이 없습니다. 닫기 버튼을 시도합니다.")
            try:
                close_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="modal-window"]/div/div/div[3]/a[2]'))
                )
                close_button.click()
                print("'닫기' 버튼 클릭 완료.")
            except NoSuchElementException:
                print("'닫기' 버튼도 없습니다. 팝업을 처리하지 못했습니다.")
    except Exception as e:
        print(f"팝업 처리 중 오류 발생: {e}")


def handle_modal_popup(driver):
    """
    팝업을 감지하고 처리하는 함수.
    팝업이 있으면 'OK' 버튼을 클릭하고, 없으면 아무 작업도 하지 않음.
    """
    try:
        # 팝업 루트 요소 확인
        modal = driver.find_element_by_class_name("modal-inner")
        if modal.is_displayed():  # 팝업이 보이는지 확인
            print("팝업이 감지되었습니다.")
            try:
                ok_button = driver.find_element_by_class_name("modal-btn")  # "OK" 버튼
                ok_button.click()
                print("팝업의 'OK' 버튼을 클릭했습니다.")
                return True
            except Exception as e:
                print(f"'OK' 버튼을 클릭하는 중 오류 발생: {e}")
                return False
        else:
            print("팝업이 감지되지 않았습니다.")
            return False
    except Exception:
        print("팝업이 없습니다.")
        return False


def log_out_web(park_id, driver):
    try:
        if park_id in amano_need_log_out:
            print(f"AMANO 처리 중, park_id: {park_id}")
            driver.execute_script("javascript:logout();")
            driver.implicitly_wait(3)
            # 로그아웃 버튼 처리
            try:
                    WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[@id='modal-window']/div/div/div[3]/a[2]"))
                    ).click()
            except Exception as e:
                print(f"로그아웃 처리 중 오류 발생: {e}")
            Util.sleep(3)
            print(Colors.BLUE + "로그아웃 완료" + Colors.ENDC)
    except Exception as e:
        print(f"로그아웃 처리 중 오류 발생: {e}")


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
            if park_id == Parks.TWIN_TREE \
                    or park_id == Parks.JIN_YANG_BUILDING:
                if ticket_name == "6시간권":
                    return web_info[10]

            elif park_id == Parks.JANG_AN_SPIZON:
                if ticket_name == "4시간권":
                    return web_info[10]

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




            elif park_id == 18934:
                if ticket_name == "평일1일권":
                    return web_info[6]


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

    if park_id == Parks.SEOUL_GIROKWON or park_id == Parks.WEST_GATE:
        driver.find_element_by_id(web_info[WebInfo.btnLogin]).click()
        driver.implicitly_wait(3)
    elif park_id == Parks.NY_TOWER:
        Util.sleep(1)
        driver.find_element_by_id("btnLogin").click()
    else:
        driver.find_element_by_xpath(web_info[WebInfo.btnLogin]).click()


def web_har_in_login_seoul_girockwon(driver, park_id):
    web_info = mapIdToWebInfo[park_id]
    web_har_in_info = ParkUtil.get_park_lot_option(park_id)

    element_id = driver.find_element_by_name(web_info[WebInfo.inputId])
    element_id.clear()
    element_id.send_keys(web_har_in_info[WebInfo.webHarInId])



def is_logged_in(driver, park_id):
    """
    로그인 상태를 확인하는 함수.
    특정 park_id에 따라 로그인 확인 요소를 동적으로 설정.
    """
    try:
        if park_id in {19934}:  # 마제스타시티 및 새로운 ID 추가
            # 로그인된 상태에서는 특정 요소가 존재
            return driver.find_element_by_xpath("//*[@id='sidebar']/div/ul").is_displayed()
        # 다른 park_id에 대한 추가 로직 확장 가능
        else:
            return False
    except NoSuchElementException:
        # 로그인되지 않은 상태
        return False

def is_login_page(driver, park_id):
    """
    현재 페이지가 로그인 페이지인지 확인하는 함수.
    특정 park_id에 따라 로그인 확인 요소를 동적으로 설정.
    """
    try:
        if park_id in {19934}:  # 마제스타시티 및 새로운 ID 추가
            # 로그인 페이지에서만 존재하는 요소 확인
            return driver.find_element_by_name("userId").is_displayed()
        else:
            return False
    except NoSuchElementException:
        # 로그인 페이지가 아님
        return False


def web_har_in(target, driver):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ori_car_num = Util.all_trim(target[2])
    ticket_name = target[3]
    park_type = ParkType.get_park_type(park_id)

    if park_id == 18973 and ticket_name != "1일권":
        print("1일권이 아님")
        return False

    trim_car_num = Util.all_trim(ori_car_num)
    search_id = trim_car_num[-4:]

    print(f"parkId = {park_id}, searchId = {search_id}")
    print(Colors.BLUE + ticket_name + Colors.ENDC)

    if not ParkUtil.is_park_in(park_id):
        print("웹할인 페이지가 없는 주차장입니다.")
        return False

    if park_id not in mapIdToWebInfo:
        print("현재 아마노웹할인 페이지 분석이 되어 있지 않는 주차장입니다.")
        return False

    login_url = ParkUtil.get_park_url(park_id)
    driver.implicitly_wait(3)
    driver.get(login_url)

    handle_popup(driver)

    web_info = mapIdToWebInfo[park_id]

    if ParkUtil.first_access(park_id, driver.current_url):
        if is_login_page(driver, park_id):
            web_har_in_login(driver, park_id)
        elif is_logged_in(driver, park_id):
            print("이미 로그인된 상태입니다.")
        else:
            print("로그인 페이지가 아니며 로그인 상태도 확인되지 않았습니다.")
            return False

        Util.close_modal(driver)



    driver.find_element_by_id(web_info[WebInfo.inputSearch]).send_keys(search_id)
    Util.sleep(3)
    driver.find_element_by_xpath(web_info[WebInfo.btnSearch]).click()
    Util.sleep(1)

    if not ParkUtil.check_search(park_id, driver):
        print("차량 번호 검색에 실패했습니다.")
        log_out_web(park_id, driver)
        return False

    discount_type_value = get_har_in_value(park_id, ticket_name)
    if not discount_type_value:
        print("할인 유형 값이 유효하지 않습니다.")
        log_out_web(park_id, driver)
        return False

    # JavaScript 실행
    try:
        har_in_script = web_info[WebInfo.methodHarInFunc].replace("discountTypeValue", discount_type_value)
        print(f"Executing JavaScript: {har_in_script}")
        driver.execute_script(har_in_script)
        Util.sleep(2)
        Util.close_modal(driver)
        log_out_web(park_id, driver)
        return True
    except Exception as e:
        print(f"JavaScript 실행 중 오류 발생: {e}")
        log_out_web(park_id, driver)
        return False

