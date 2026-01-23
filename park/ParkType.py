# -*- coding: utf-8 -*-
from park import Parks
import pymysql

# 주차장 별 비교해야 될 셀럭터
HIGH_CITY = 20
BLUE = 22
DARAE = 23
AMANO = 21
I_PARKING = 24
GS = 25
IP_TIME = 26
GRANG_SEOUL = 27
OLD_AJ = 28
AJ_PARK = 29
HIGH_CITY_2 = 30
ETC = 31
NICE = 32
NICE_NEW = 43
GS2= 33
NEW_HIGH = 34
KAIT_TOWER = 35
ARC_PLACE = 37
HIGH_MHP = 38
HIGH_MHP_OPT = 42
CENTER_SQUARE_NEW = 39
CENTER_SQUARE = 40
NEW_AMANO = 46
NEW_KMPARK = 47
#CENTER_SQUARE =34

# 주차장 타입별 주차장들
parkTypeHighCity = [
    15313,
    13007,
    19517,
    Parks.DDMC,
    Parks.TWIN_CITY,
    Parks.RIVER_TOWER,
    Parks.EG_BUILDING,
    #Parks.MUNJUNG_PLAZA,
    Parks.KOREANA_HOTEL,
    Parks.DONGSAN_GONGYEONG,
    Parks.D_TOWER,
    Parks.BANPO_DONG_GONGYONG,
    Parks.GRAND_CENTRAL,
    Parks.MUGUNG,
    Parks.HAEUNDAE_IPARK,
    20864,
    19174,
    19185,
    19492,#반포2동공영
    29248,#DWI 마곡595빌딩 주차장
    29364,#역삼아르누보시티
    29362,#서초그랑자이그랑몰
    29361,#보타니끄논현오피스텔
    19740,#하이파킹 평촌역점
    29218,# 하이파킹 판교알파리움타워(2동)
    18996,# 하이파킹 판교알파리움타워(1동)
    16159

]

parkTypeHighCity2 = [
    Parks.ORAKAI_DAEHAKRO
]


parkTypeBlue = [
    4588,
    19082,
    Parks.KIUM_NADEGI,
    Parks.SAMSUNG_SERVICE_BUILDING,
    Parks.MILLENNIUM_SEOUL_HILTON,
    Parks.URIM_RODEO_SWEET,
    19416,
    19423
]

parkTypeDarae = [
    28864
]

parkTypeIparking = [
    19433, # 서초꽃마을
    19448, #예전빌딩
    19459,#동양프라자
    19461,#다산법조메디컬타워
    19462,#화광빌딩
    19476, #이마트TR송림점
    19921, #하이파킹 성수무신사캠퍼스N1
    19440, #용산베르디움프렌즈 주차장
    29220, #하이파킹 종로5가역하이뷰더광장
    29175, #하이파킹 SK-C타워(구, 충무로15빌딩)
    19945, # 신한은행 광교 주차장
    19508,
]
#tbody 있음
parkTypeGs = [
    Parks.KDB_LIFE,
    Parks.KANGDONG_HOMEPLUS,
    19237,
    19450, # 경제신문
    19493,#판교아이스퀘어C1
    19494,#판교아이스퀘어C2





]

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
DEFAULT_WEB_INFO = ["username", "password", "//*[@id='app']/div/div[2]/div/div/main/div/form/button",
                    "discountPlateNumberForm", "//*[@id='app']/div/div[2]/div/div/main/div[2]/div[1]/div[1]/form/button"]

DEFAULT_WEB_INFO_NICE = ["mf_wfm_body_ibx_empCd", "mf_wfm_body_sct_password", "mf_wfm_body_btn_login",
                    "mf_wfm_body_carNo", "mf_wfm_body_mobileOkBtn"]

DEFAULT_WEB_INFO_NEW_AMANO = ["userId", "userPwd", "btnLogin",
                    "schCarNo", "//*[@id='sForm']/input[3]"]

DEFAULT_WEB_INFO_NEW_KMPARK = ["userId", "userPwd", "btnLogin",
                    "schCarNo", "//*[@id='sForm']/input[3]"]



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

def get_park_ids_by_urls_nice(target_urls_nice):
    """
    DB에서 특정 URL 리스트와 매칭된 park_id를 가져옵니다.
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        curs = conn.cursor()
        # SQL 쿼리 실행
        format_strings = ','.join(['%s'] * len(target_urls_nice))
        sql = f"SELECT parkId FROM T_PARKING_WEB WHERE url IN ({format_strings})"
        curs.execute(sql, target_urls_nice)
        rows = curs.fetchall()
        return [row[0] for row in rows]  # park_id 리스트로 반환
    except Exception as e:
        print(f"DB 쿼리 실패: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_park_ids_by_urls_new_amano(target_urls_new_amano):
    """
    DB에서 특정 URL 리스트와 매칭된 park_id를 가져옵니다.
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        curs = conn.cursor()
        # SQL 쿼리 실행
        format_strings = ','.join(['%s'] * len(target_urls_new_amano))
        sql = f"SELECT parkId FROM T_PARKING_WEB WHERE url IN ({format_strings})"
        curs.execute(sql, target_urls_new_amano)
        rows = curs.fetchall()
        return [row[0] for row in rows]  # park_id 리스트로 반환
    except Exception as e:
        print(f"DB 쿼리 실패: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_park_ids_by_urls_new_kmpark(target_urls_new_kmpark):
    """
    DB에서 특정 URL 리스트와 매칭된 park_id를 가져옵니다.
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        curs = conn.cursor()
        # SQL 쿼리 실행
        format_strings = ','.join(['%s'] * len(target_urls_new_kmpark))
        sql = f"SELECT parkId FROM T_PARKING_WEB WHERE url IN ({format_strings})"
        curs.execute(sql, target_urls_new_kmpark)
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


# 대상 URL 리스트
TARGET_URLS_NICE = [
    "https://npdc-i.nicepark.co.kr/",
    "https://npdc-i.nicepark.co.kr",
    "http://npdc-i.nicepark.co.kr/",
    "http://npdc-i.nicepark.co.kr",
    "http://npdc.nicepark.co.kr"
]


# 대상 URL 리스트
TARGET_URLS_NEW_AMANO = [
    "https://a14926.parkingweb.kr/login","https://a05203.parkingweb.kr",
    "https://a18822.pweb.kr","https://a14041.parkingweb.kr/","https://a18147.pweb.kr/",
    "https://a12647.parkingweb.kr/","https://www.amanopark.co.kr/",
    "https://a093.parkingweb.kr/","https://a17687.pweb.kr/","http://112.217.102.42/","http://a15820.parkingweb.kr/",
"https://a02248.parkingweb.kr/login","http://www.amanopark.co.kr","http://a03428.parkingweb.kr","http://1.225.4.44"
,"http://59.15.76.103","http://121.160.237.7","https://a17389.parkingweb.kr/",
    "https://a04088.parkingweb.kr","http://112.220.251.2","http://211.217.212.176/"
    ,"https://a15061.parkingweb.kr/discount/registration","https://a18134.pweb.kr/login"
,"http://175.114.59.25/discount/registration","http://211.202.87.149"
    ,"http://211.244.148.17/","https://a15337.parkingweb.kr","http://121.134.61.62/login"
    ,"http://a05388.parkingweb.kr","http://175.195.124.15","https://a14705.parkingweb.kr/login"
    ,"https://a13687.parkingweb.kr/login","https://s1148.parkingweb.kr/login"
    ,"https://s1151.parkingweb.kr:6650/login","https://a14417.parkingweb.kr/login"
    ,"http://123.214.186.154","https://a17902.pweb.kr","https://a15891.parkingweb.kr"
    ,"https://a15521.parkingweb.kr/login","https://a20628.pweb.kr/","https://a15531.parkingweb.kr/"
    ,"https://a00150.parkingweb.kr/login","https://a3590.parkingweb.kr","https://a20297.pweb.kr/login"
    ,"http://vg.awp.co.kr","https://a2325.parkingweb.kr/","https://a17498.pweb.kr"
    ,"http://112.216.125.10/discount/registration","https://a02412.parkingweb.kr/login"
    ,"https://a103.parkingweb.kr/discount/registration","https://a17835.pweb.kr/","http://210.222.86.169"
    ,"https://s1153.parkingweb.kr/login","http://1.209.17.122","http://hipjungan.iptime.org"
    ,"https://cpost.parkingweb.kr/discount/registration","http://211.106.97.154/login","http://a12773.parkingweb.kr"
    ,"https://a16541.parkingweb.kr","https://a05386.parkingweb.kr"
    ,"https://a21877.pweb.kr/login","https://a03235.parkingweb.kr/",
    "https://a13660.parkingweb.kr","https://a16054.parkingweb.kr/login"
    ,"https://a00540.pweb.kr/login","https://postyud.parkingweb.kr/","https://a21504.pweb.kr/"
    ,"https://a15602.pweb.kr","https://a12859.parkingweb.kr/login","https://a21023.pweb.kr"
    ,"https://a22272.pweb.kr/","http://211.55.2.163/login","https://a19813.pweb.kr/",
    "https://a22037.pweb.kr","https://a21320.pweb.kr/","https://a21347.pweb.kr/"
    ,"https://a21351.pweb.kr/","http://a16591.parkingweb.kr","http://1.223.26.123/login"
    ,"https://a22496.pweb.kr/login","https://a22039.pweb.kr/login"
    ,"https://a21949.pweb.kr/login","https://a21771.pweb.kr/login"
]


# 대상 URL 리스트
TARGET_URLS_NEW_KMPARK = [
    "http://kmp0000798.iptime.org/","http://kmp0000601.iptime.org/","http://kmp0000483.iptime.org/"
    ,"http://kmp0000575.iptime.org/","http://kmp0000854.iptime.org/","http://kmp0000774.iptime.org/"
    ,"http://kmp0000089.iptime.org/","http://kmp0000403.iptime.org/","http://kmp0000131.iptime.org/"
    ,"http://kmp0000748.iptime.org/","http://kmp0000025.iptime.org/","http://kmp0000099.iptime.org/"
    ,"http://kmp0000871.iptime.org/","http://kmp0000869.iptime.org/","http://kmp0000525.iptime.org/"
    ,"http://kmp0000007.iptime.org/","http://kmp0000678.iptime.org"]

# DB에서 park_id 동적 조회
dynamic_park_ids = get_park_ids_by_urls(TARGET_URLS)

# DB에서 park_id 동적 조회
dynamic_park_ids_nice = get_park_ids_by_urls_nice(TARGET_URLS_NICE)

dynamic_park_ids_new_amano = get_park_ids_by_urls_new_amano(TARGET_URLS_NEW_AMANO)

dynamic_park_ids_new_kmpark = get_park_ids_by_urls_new_kmpark(TARGET_URLS_NEW_KMPARK)


# mapIdToWebInfo 동적 생성
parkType_high_mhp = {
    park_id: DEFAULT_WEB_INFO
    for park_id in dynamic_park_ids
}

parkType_high_mhp_opt = {
    park_id: DEFAULT_WEB_INFO
    for park_id in dynamic_park_ids
}

parkType_nice = {
    park_id: DEFAULT_WEB_INFO_NICE
    for park_id in dynamic_park_ids_nice
}

parkType_new_amano = {
    park_id: DEFAULT_WEB_INFO_NEW_AMANO
    for park_id in dynamic_park_ids_new_amano
}

parkType_new_kmpark = {
    park_id: DEFAULT_WEB_INFO_NEW_KMPARK
    for park_id in dynamic_park_ids_new_kmpark
}

parkType_grang_seoul = [Parks.GRANG_SEUOL]
parkType_kait_tower = [Parks.KAIT_TOWER]
parkType_arc_place = [Parks.ARC_PLACE]
parkType_center_square_new = [Parks.CENTER_SQUARE_NEW]
parkType_center_square = [Parks.CENTER_SQUARE]

park_type_aj_park = [
    Parks.AJ_NON_HYEN,
    19004,
    19540,
    19534,
    19860,
    29136,
    19271,
    19862,
    19810,
    19148,
    29184
]

park_type_old_aj = [
    Parks.GMG_TOWER,
    Parks.SUN_HWA_BUILDING,
    19070,
    19497,  # 롯데마트 영종도점
    19499,  # 롯데마트 고양점
    19505

]

park_type_etc = [
    Parks.HUMAX_VILLAGE,
    19427, #종로플레이스


]
park_type_aplus = [15740]
park_type_nice = [
    Parks.NICE_INGYE_CULTURE,
    Parks.NICE_KYUNGBOK_UNIVERSITY,
    Parks.NICE_GOYANG_GLOBAL_THEME_PLAZA,
    Parks.NICE_GURI_GALMAE_CENTRAL,
    Parks.NICE_WOLFE,
    Parks.NICE_DAEIL_BUILDING,
    Parks.NICE_DAEJEON_DUNSAN_CORE_TOWER,
    Parks.NICE_DAEJEON_WOORIDUL_PARK,
    Parks.NICE_DONGTAN_ACEK_CITY_TOWER,
    Parks.NICE_LOTTE_NESON,
    Parks.NICE_LOTTE_YEON_SU,
    Parks.NICE_LOTTE_POHANG,
    Parks.NICE_MAGOK_INTER_CITY_HOTEL,
    Parks.NICE_BUCHEON_SINEMAJON_BUILDING,
    Parks.NICE_SIHEUNG_SKYDREAM_CITY,
    Parks.NICE_ASAN_ONYANG_TOURIST_HOTEL,
    Parks.NICE_YANGJU_DREAM_WORLD,
    Parks.NICE_YEONGJONGDO_EUN_SQUARE,
    Parks.NICE_OSAN_GEOSEONG_GREEN,
    Parks.NICE_YONGIN_GRAND_PLAZA,
    Parks.NICE_UDEOK_BUILDING,
    Parks.NICE_JEONGJA_DONG,
    Parks.NICE_JONGNO_TOWER,
    Parks.NICE_CHEONGNA_COMPETITION_TOWER,
    Parks.NICE_HANAMS_S_BIZ_TOWER,
    Parks.NICE_CHEONGGYE_DOOSAN_WEVE_THE_ZENITH,
    # Parks.NICE_SAMWON_TOWER,
    Parks.NICE_HONGIK_YEMUN,
    Parks.NICE_DGB,
    Parks.NICE_DONGTAN_DONGYEON,
    19398,19402,19403,19404,19405,19514,19513,19512,19539
]

# 키의 갯수 주차권을 분류하기 위함
haveOneKey = [
    Parks.NAMSAN_SQUARE,
    Parks.PARK_M,
    Parks.GYEONG_BOK_GUNG,
    Parks.G_VALLY,
    Parks.DONGHWA_BUILDING,
    Parks.KIUM_NADEGI,
    Parks.DDMC,
    Parks.TWIN_CITY,
    Parks.RIVER_TOWER,
    Parks.GMG_TOWER,
    Parks.SINRA_STAY_G_TOWER,
    Parks.MILLENNIUM_SEOUL_HILTON,
    Parks.URIM_RODEO_SWEET,
    Parks.V_PLEX,
    Parks.NY_TOWER,
    Parks.EG_BUILDING,
    Parks.ORAKAI_DAEHAKRO,
    Parks.KOREANA_HOTEL
]

haveWeekKey = [
    Parks.DONGIL_TOWER,
    Parks.MOKDONG_ART,
    Parks.ECC,
    Parks.ECC_MONTH,
    Parks.WEST_GATE,
    Parks.HARIM_INTERNATIONAL
]

haveTwoKey = [
    Parks.Y_PLUS,
    Parks.SEOUL_GIROKWON,
    Parks.SK_MYEONGDONG,
    Parks.PODO_MALL,
    Parks.SAMSUNG_SERVICE_BUILDING,
    Parks.GRANG_SEUOL,
    Parks.KAIT_TOWER,
    Parks.ARC_PLACE,
    Parks.CENTER_SQUARE_NEW,
    Parks.CENTER_SQUARE,
    Parks.JS_HOTEL,
    Parks.KDB_LIFE,
    Parks.KANGDONG_HOMEPLUS
]

haveThreeKey = [
    # Parks.N_TOWER,
    Parks.JANG_AN_SPIZON,
    Parks.JAYANG_PALACE
]

haveFourKey = [
    Parks.YEOKSAM_BUILDING
]

haveFiveKey = [
    # Parks.HONG_MUN_KWAN
    Parks.SEOUL_TRAIN
]

parkTypeNoRequestMain = [
    Parks.GYEONG_BOK_GUNG,
    Parks.DONGHWA_BUILDING,
    Parks.KIUM_NADEGI,
    Parks.KDB_LIFE,
    Parks.KANGDONG_HOMEPLUS,
    Parks.SAMSUNG_SERVICE_BUILDING,
    Parks.MILLENNIUM_SEOUL_HILTON,
    Parks.NON_SQUARE,
    Parks.SUN_HWA_BUILDING,
    Parks.PODO_MALL,
    Parks.NC_GANG_NAM,
    Parks.FINE_AVENUE,19333
]

type_to_search_css = {
    AJ_PARK: "body > div.wrap > section > div > section > div:nth-child(2) > div > dl:nth-child(4) > dd",
    BLUE: "#divAjaxCarList > tr",
    DARAE: "#search_form > table > tbody > tr:nth-child(2) > td",
    GRANG_SEOUL: "#carList > table > tbody > tr > td:nth-child(2) > a",
    KAIT_TOWER: "body > table:nth-child(4) > tbody > tr:nth-child(3) > td:nth-child(2)",
    ARC_PLACE: "body > table:nth-child(4) > tbody > tr:nth-child(3) > td:nth-child(2)",
    GS: "#divAjaxCarList > tbody > tr",
    GS2: "#divAjaxCarList > tr",
    HIGH_MHP: "#divAjaxCarList > tr",
    HIGH_MHP_OPT: "#divAjaxCarList > tr",
    NICE_NEW: "#divAjaxCarList > tr",
    NEW_AMANO: "#modal-window > div > div > div.modal-text",
    NEW_KMPARK: "#modal-window > div > div > div.modal-text",
    HIGH_CITY: "#search_form > table > tbody > tr > td:nth-child(2) > table:nth-child(3) > tbody > tr:nth-child(2)",
    IP_TIME: "#DataGrid1 > tbody > tr:nth-child(2) > td:nth-child(1)",
    HIGH_CITY_2: "#search_form > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(2)",
    OLD_AJ: "body > table:nth-child(4) > tbody > tr:nth-child(3) > td:nth-child(2)"

}

mapToAgency = {
    HIGH_CITY: "input[type='hidden']",  # 차량번호 hidden input
    BLUE: "#carDetail > table:nth-child(1) > tbody > tr:nth-child(1) > td:nth-child(2)",
    DARAE: "#search_form > table > tbody > tr:nth-child(2) > td:nth-child(2)",
    I_PARKING: "#carList > tr > td:nth-child(2)",
    GS: "#divAjaxCarList > tbody > tr > td",
    GS2: "#divAjaxCarList > tr > td",
    HIGH_MHP: "#divAjaxCarList > tr > td",
    HIGH_MHP_OPT: "#divAjaxCarList > tr > td",
    NICE_NEW: "#divAjaxCarList > tr > td",
    NEW_AMANO: "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected > td.cellselected",
    NEW_KMPARK: "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected > td.cellselected",
    18973: "#tblList > tbody > tr > td:nth-child(2)",
    IP_TIME: "#DataGrid1 > tbody > tr:nth-child(2) > td:nth-child(1)",
    # IP_TIME: "#listSearch > table:nth-child(7) > tbody > tr:nth-child(2)",
    GRANG_SEOUL: "#carList > table > tbody > tr > td:nth-child(2) > a",
    KAIT_TOWER: "/html/body/table[2]/tbody/tr[3]/td[2]/text()[1]",
    ARC_PLACE: "/html/body/table[2]/tbody/tr[3]/td[2]/text()[1]",
    AJ_PARK: "body > div.wrap > section > div > section > div:nth-child(2) > div > dl:nth-child(4) > dd",
    HIGH_CITY_2: "#search_form > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(2)",
    OLD_AJ: "/html/body/table[2]/tbody/tr[3]/td[2]/text()[1]",
    Parks.ORAKAI_DAEHAKRO: "#search_form > table > tbody > tr > td:nth-child(2) > table:nth-child(3) > tbody > tr:nth-child(2) > td:nth-child(2)"
}

mapToHarinUrl = {
    HIGH_CITY: "/discount/discount_regist.asp",
    HIGH_CITY_2: "/discount/discount_regist.asp",
    BLUE: "/index.php/main/index",
    DARAE: "/discount/discount_regist.php",
    I_PARKING: "/html/home.html#!",
    GS: "/main",
    GS2: "/main",
    HIGH_MHP: "/main",
    HIGH_MHP_OPT: "/main",
    NICE_NEW: "/main",
    NEW_AMANO: "/discount/registration",
    NEW_KMPARK: "/discount/registration",
    IP_TIME: "/ListSearch.aspx",
    GRANG_SEOUL: "/ezTicket/carSearch",
    KAIT_TOWER: "/discount/carSearch.cs?userID=ppark&contextPath=",
    ARC_PLACE: "/discount/carSearch.cs?userID=ppark&contextPath=",
    AJ_PARK: "home.do",
    OLD_AJ: "/discount/carSearch.cs?userID=ppark&contextPath="
}

type_to_day_css = {
    IP_TIME: "#DataGrid1 > tbody > tr:nth-child(2) > td:nth-child(2)",
}


def get_park_type(park_id):


    if park_id in parkTypeHighCity:
        return HIGH_CITY
    elif park_id in parkTypeHighCity2:
        return HIGH_CITY_2
    elif park_id in parkTypeBlue:
        return BLUE
    elif park_id in parkTypeDarae:
        return DARAE
    elif park_id in parkTypeIparking:
        return I_PARKING
    elif park_id in parkTypeGs:
        return GS
    elif park_id in parkType_high_mhp_opt:
        return HIGH_MHP_OPT
    elif park_id in parkType_nice:
        return NICE_NEW
    elif park_id in parkType_new_amano:
        return NEW_AMANO
    elif park_id in parkType_new_kmpark:
        return NEW_KMPARK
    elif park_id in parkType_grang_seoul:
        return GRANG_SEOUL
    elif park_id in parkType_kait_tower:
        return KAIT_TOWER
    elif park_id in parkType_arc_place:
        return ARC_PLACE
    elif park_id in parkType_center_square:
        return CENTER_SQUARE
    elif park_id in parkType_center_square_new:
        return CENTER_SQUARE_NEW
    elif park_id in park_type_aj_park:
        return AJ_PARK
    elif park_id in park_type_etc:
        return ETC
    elif park_id in park_type_old_aj:
        return OLD_AJ
    elif park_id in park_type_nice:
        return NICE


    else:
        print(f"DEBUG: park_id {park_id} does not match any parkType.")
        return None
