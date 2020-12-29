# -*- coding: utf-8 -*-
from park import Parks

# 주차장 별 비교해야 될 셀럭터
HIGH_CITY = 20
AMANO = 21
BLUE = 22
DARAE = 23
I_PARKING = 24
GS = 25
IP_TIME = 26
GRANG_SEOUL = 27
OLD_AJ = 28
AJ_PARK = 29
HIGH_CITY_2 = 30
ETC = 31
NICE = 32

# 주차장 타입별 주차장들
parkTypeHighCity = [
    15313,
    Parks.PLATINUM,
    13007,
    15644,
    11917,
    18958,
    15437,
    15008,
    14994,
    12904,
    11349,
    Parks.ALPHA_DOM_TOWER,
    Parks.SC_BANK,
    Parks.SIGNATURE_TOWER,
    Parks.DDMC,
    Parks.TWIN_CITY,
    Parks.HSBC,
    Parks.CITY_PLAZA,
    Parks.CITY_PLAZA_2,
    Parks.NAMSAN_TOWER,
    Parks.CENTER_PLACE,
    Parks.HANWHA_BUILDING,
    Parks.LOTTE_L7,
    Parks.FAST_FIVE_TOWER,
    Parks.CENTRAL_PLACE,
    Parks.WEWORK_TOWER,
    Parks.JUMP_MILAN,
    Parks.TAEPYEONGRO_BUILDING,
    Parks.RIVER_TOWER,
    Parks.TS_ONE,
    Parks.KTB_BUILDING,
    Parks.W_SQARE,
    Parks.DGB_FINANCE_CENTER,
    Parks.PAN_GYO_ALPHARIUM_TOWER,
    Parks.CENTRAL_TOWER,
    Parks.KI_TOWER,
    Parks.JEIL_OPISTEL,
    Parks.SUSONG_SQAURE,
    Parks.ULGI_TWIN_TOWER,
    Parks.GANG_NAM_L7,
    Parks.COSMO_TOWER,
    Parks.ORAKAI_SWEETS,
    Parks.YANGWOO_DRAMA_CITY,
    Parks.EG_BUILDING,
    Parks.O_TWO_TOWER,
    Parks.ORANGE_CENTER,
    Parks.MOL_OF_K,
    Parks.CENTERMARK_HOTEL,
    Parks.KTNG_TOWER,
    Parks.MUNJUNG_PLAZA,
    Parks.KOREANA_HOTEL,
    Parks.HILL_STATE_ECO_MAGOKNARU,
    Parks.ING_ORANGE_TOWER,
    Parks.KTNG_SUWON,
    Parks.GANG_NAM_BUILDING,
    Parks.YANGJAE_GONGYEONG,
    Parks.DONGSAN_GONGYEONG,
    Parks.SHIN_NON_HYUN_W_TOWER,
    Parks.D_TOWER,
    Parks.BANPO_DONG_GONGYONG,
    Parks.SUWON_STATION_MARKET,
    Parks.GRAND_CENTRAL,
    Parks.MI_SEONG_BUILDING,
    Parks.NH_GWANG_MYEONG,
    Parks.YEOK_SAM_ECHERE,
    Parks.HAEUNDAE_IPARK
]

parkTypeHighCity2 = [
    Parks.MERITZ_FIRE,
    Parks.ORAKAI_DAEHAKRO
]

parkTypeAmano = [
    16239,
    Parks.Y_PLUS,
    Parks.PARK_M,
    Parks.PARK_M_NIGHT,
    Parks.ECC,
    Parks.PACIFIC_TOWER,
    Parks.SEOUL_GIROKWON,
    Parks.N_TOWER,
    Parks.SK_MYEONGDONG,
    Parks.PODO_MALL,
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
    Parks.ACE_TOWER,
    Parks.JAYANG_PALACE,
    Parks.NICE_HONG_MUN_KWAN,
    Parks.CHUNGJEONGNO_HOUSE,
    Parks.OMOK_BRIDGE,
    Parks.MAGOK_RUMA_2,
    Parks.NON_SQUARE,
    Parks.JEONGAN_BUILDING,
    Parks.GWANG_HWA_MUN_S_TOWER,
    Parks.MDM_TOWER_DANG_SAN,
    Parks.HANA_TOOJA_BUILDING,
    # Parks.KUN_KUK_BUILDING,
    Parks.STATE_TOWER_NAMSAN,
    Parks.SEOGYO_DONG_NADAEJI,
    Parks.KUN_KUK_MIDDLE,
    Parks.GS_GUN_GUK_BUILDING,
    Parks.GAM_SIN_DAE,
    Parks.NC_GANG_NAM,
    Parks.JONG_RO_THE_K,
    Parks.HAP_JEONG_STATION_YOUTH_HOUSE,
    Parks.LOTTE_CITY_HOTEL_MYEONG_DONG,
    Parks.GANG_NAM_FINANCE,
    Parks.GRACE_TOWER,
    Parks.FINE_AVENUE
]

parkTypeBlue = [
    4588,
    19082,
    18967,
    Parks.KIUM_NADEGI,
    Parks.SAMSUNG_SERVICE_BUILDING,
    Parks.URBANIEL_HAN_GANG,
    Parks.MILLENNIUM_SEOUL_HILTON,
    Parks.URIM_RODEO_SWEET,
    Parks.FRYDIUM_BUILDING,
    Parks.HOTEL_SUNSHINE
]

parkTypeDarae = [
    28864
]

parkTypeIparking = [
    18966,
    Parks.AUTOWAY_TOWER,
    Parks.NUN_SQUARE,
    Parks.RAMIAN_YONGSAN_THE_CENTRAL,
    Parks.BUILDING_94,
    Parks.CONCORDIAN_BUILDING,
    Parks.OUR_W_TOER,
    Parks.DIAT_CENTRAL,
    Parks.BIT_FLEX,
    Parks.YEOUIDO_NH_CAPITAL,
    Parks.ISU_GONG_YONG
]

parkTypeGs = [
    Parks.FINANCE_TOWER,
    Parks.HI_INSADONG,
    19136,
    Parks.DMC_S_CITY,
    Parks.DMCC,
    Parks.MEGABOX_SUNGSU,
    Parks.NONHYEON_BUILDING,
    Parks.ERE_BUILDING,
    Parks.KDB_LIFE,
    Parks.PARK_BUILDING,
    Parks.URBANIEL_CHEN_HO,
    Parks.SANGBONG_DUOTRIS,
    Parks.MODERN_GYEDONG_BUILDING,
    Parks.MERCURE_AMBASSADOR,
    Parks.MAGOK_SPRINGTOWER,
    Parks.GANGDONG_HOMEPLUS
]

parkType_ip_time = [
    Parks.E_WHA_APM,
    Parks.SAMSUNG_SEOUL_MEDICAL_CENTER,
    Parks.SEOUL_SQAURE,
    Parks.V_PLEX
]

parkType_grang_seoul = [Parks.GRANG_SEUOL]

park_type_aj_park = [
    Parks.AJ_EULJIRO_3,
    Parks.AJ_JONGRO,
    Parks.AJ_T_MARK,
    Parks.AJ_JNS,
    Parks.AJ_MDM,
    Parks.AJ_MYUNG_DONG,
    Parks.AJ_GONG_DUK,
    Parks.AJ_MUGYO,
    Parks.AJ_SEOUL_GARDEN,
    Parks.AJ_USIN,
    Parks.AJ_NON_HYEN,
    Parks.AJ_HAB_JONG,
    Parks.AJ_DONG_MYO,
    Parks.AJ_GANG_NAM,
    Parks.AJ_MUNJUNG_PRAVIDA,
    Parks.AJ_MR_HOMZ,
    Parks.AJ_SINDUK,
    Parks.HONGDAE_EILEX,
    Parks.NONHYEON_WELLSTONE,
    Parks.AJ_BANGBE,
    Parks.AJ_HOUSE_DIBIZ,
    Parks.AJ_EWHA,
    Parks.AJ_HONG_IK_SPORTS_SPA,
    Parks.AJ_GUWOL_CENTRAL
]

park_type_old_aj = [
    Parks.GMG_TOWER,
    Parks.SUN_HWA_BUILDING
]

park_type_etc = [
    Parks.WESTERN_853,
    Parks.DREAM_TOWER_NIGHT,
    Parks.DREAM_TOWER_HOLIDAY,
    Parks.DIAT_GALLERY_2
]

park_type_nice = [
    # Parks.NICE_KB_BUPYEONG_PLAZA,
    # Parks.NICE_INGYE_CULTURE,
    # Parks.NICE_KYUNGBOK_UNIVERSITY,
    # Parks.NICE_GOYANG_GLOBAL_THEME_PLAZA,
    # Parks.NICE_GURI_GALMAE_CENTRAL,
    # Parks.NICE_GIMPO_WORLD_AVENUE,
    # Parks.NICE_WOLFE,
    # Parks.NICE_DAEIL_BUILDING,
    # Parks.NICE_DAEJEON_DUNSAN_CORE_TOWER,
    # Parks.NICE_DAEJEON_WOORIDUL_PARK,
    # Parks.NICE_DONGTAN_ACEK_CITY_TOWER,
    # Parks.NICE_LOTTE_NESON,
    # Parks.NICE_LOTTE_YEON_SU,
    # Parks.NICE_LOTTE_POHANG,
    # Parks.NICE_MAGOK_INTER_CITY_HOTEL,
    # Parks.NICE_MOKPO_TERMINAL,
    # Parks.NICE_BUCHEON_SINEMAJON_BUILDING,
    # Parks.NICE_SEOSOMUN_CITY_SQUARE,
    # Parks.NICE_SIHEUNG_SKYDREAM_CITY,
    # Parks.NICE_ASAN_ONYANG_TOURIST_HOTEL,
    # Parks.NICE_YANGJU_DREAM_WORLD,
    # Parks.NICE_YEONGJONGDO_EUN_SQUARE,
    # Parks.NICE_OSAN_GEOSEONG_GREEN,
    # Parks.NICE_YONGIN_GRAND_PLAZA,
    # Parks.NICE_UDEOK_BUILDING,
    # Parks.NICE_JEONGJA_DONG,
    # Parks.NICE_JONGNO_TOWER,
    # Parks.NICE_JUNG_GU_JUNGDONG_BUILDING,
    # Parks.NICE_CHEONAN_DOUBLE_EUPHRAZA,
    # Parks.NICE_CHEONGNA_HONGIK,
    # Parks.NICE_CHEONGNA_COMPETITION_TOWER,
    # Parks.NICE_HANAMS_S_BIZ_TOWER,
    # Parks.NICE_HAPPY_TOWER,
    # Parks.NICE_CHEONGGYE_DOOSAN_WEVE_THE_ZENITH,
    # Parks.NICE_SAMWON_TOWER,
    # Parks.NICE_HONGIK_YEMUN,
    # Parks.NICE_DGB,
    # Parks.NICE_DONGTAN_DONGYEON
]

# 키의 갯수 주차권을 분류하기 위함
haveOneKey = [
    Parks.PLATINUM,
    Parks.NAMSAN_SQUARE,
    Parks.K_SQUARE,
    Parks.PARK_M,
    Parks.GYEONG_BOK_GUNG,
    Parks.G_VALLY,
    Parks.DONGHWA_BUILDING,
    Parks.URBAN_PLACE_HOTEL,
    Parks.MAJESTA,
    Parks.ICON_YEOKSAM,
    Parks.FINANCE_TOWER,
    Parks.HI_INSADONG,
    Parks.SI_TOWER,
    Parks.ARK_PLACE,
    Parks.PACIFIC_TOWER,
    Parks.ALPHA_DOM_TOWER,
    Parks.KIUM_NADEGI,
    Parks.DMC_S_CITY,
    Parks.SC_BANK,
    Parks.DDMC,
    Parks.DMCC,
    Parks.TWIN_CITY,
    Parks.HSBC,
    Parks.CITY_PLAZA,
    Parks.CITY_PLAZA_2,
    Parks.AUTOWAY_TOWER,
    Parks.CENTER_PLACE,
    Parks.LOTTE_L7,
    Parks.MEGABOX_SUNGSU,
    Parks.FAST_FIVE_TOWER,
    Parks.GOLDEN_TOWER,
    Parks.E_WHA_APM,
    Parks.CENTRAL_PLACE,
    # Parks.KTB_BUILDING,
    Parks.JUMP_MILAN,
    Parks.TAEPYEONGRO_BUILDING,
    Parks.NONHYEON_BUILDING,
    Parks.RIVER_TOWER,
    Parks.GMG_TOWER,
    Parks.URBANIEL_HAN_GANG,
    Parks.SAMSUNG_SEOUL_MEDICAL_CENTER,
    Parks.W_SQARE,
    Parks.PAN_GYO_ALPHARIUM_TOWER,
    Parks.ERE_BUILDING,
    Parks.KI_TOWER,
    Parks.SINRA_STAY_G_TOWER,
    Parks.MILLENNIUM_SEOUL_HILTON,
    Parks.SEOUL_SQAURE,
    Parks.ULGI_TWIN_TOWER,
    Parks.URIM_RODEO_SWEET,
    Parks.GANG_NAM_L7,
    Parks.V_PLEX,
    Parks.COSMO_TOWER,
    Parks.NY_TOWER,
    Parks.MERITZ_FIRE,
    Parks.ORAKAI_SWEETS,
    Parks.YANGWOO_DRAMA_CITY,
    Parks.EG_BUILDING,
    Parks.O_TWO_TOWER,
    Parks.ORANGE_CENTER,
    Parks.ORAKAI_DAEHAKRO,
    Parks.MOL_OF_K,
    Parks.FRYDIUM_BUILDING,
    Parks.CENTERMARK_HOTEL,
    Parks.KOREANA_HOTEL
]

haveWeekKey = [
    Parks.DONGIL_TOWER,
    Parks.ECC,
    Parks.ECC_MONTH,
    Parks.WEST_GATE,
    Parks.HANWHA_BUILDING,
    Parks.TS_ONE,
    Parks.HARIM_INTERNATIONAL
]

haveTwoKey = [
    Parks.WISE_PARK,
    Parks.T_TOWER,
    Parks.Y_PLUS,
    Parks.SEOUL_GIROKWON,
    Parks.NUN_SQUARE,
    Parks.SK_MYEONGDONG,
    Parks.PODO_MALL,
    Parks.SAMSUNG_SERVICE_BUILDING,
    Parks.GRANG_SEUOL,
    Parks.JS_HOTEL,
    Parks.KDB_LIFE,
    Parks.BUILDING_94,
    Parks.AJ_MUNJUNG_PRAVIDA
]

haveThreeKey = [
    Parks.AIA,
    Parks.GUUI_WELLTZ,
    Parks.ECHO_TERRACE,
    Parks.WISE_TOWER,
    # Parks.N_TOWER,
    Parks.SIGNATURE_TOWER,
    Parks.NAMSAN_TOWER,
    Parks.WEWORK_TOWER,
    Parks.RAMIAN_YONGSAN_THE_CENTRAL,
    Parks.DGB_FINANCE_CENTER,
    Parks.CENTRAL_TOWER,
    Parks.JANG_AN_SPIZON,
    Parks.JEIL_OPISTEL,
    Parks.SUSONG_SQAURE,
    Parks.AJ_MR_HOMZ,
    Parks.JAYANG_PALACE,
    Parks.CHUNGJEONGNO_HOUSE
]

haveFourKey = [
    Parks.YEOKSAM_BUILDING
]

haveFiveKey = [
    # Parks.HONG_MUN_KWAN
]

parkTypeNoRequestMain = [
    Parks.GYEONG_BOK_GUNG,
    Parks.URBAN_PLACE_HOTEL,
    Parks.FINANCE_TOWER,
    Parks.HI_INSADONG,
    Parks.DONGHWA_BUILDING,
    Parks.KIUM_NADEGI,
    Parks.DMC_S_CITY,
    Parks.DMCC,
    Parks.SI_TOWER,
    Parks.NONHYEON_BUILDING,
    Parks.ERE_BUILDING,
    Parks.KDB_LIFE,
    Parks.SAMSUNG_SERVICE_BUILDING,
    Parks.MEGABOX_SUNGSU,
    Parks.MILLENNIUM_SEOUL_HILTON,
    Parks.PARK_BUILDING,
    Parks.URBANIEL_HAN_GANG,
    Parks.URBANIEL_CHEN_HO,
    Parks.NON_SQUARE,
    Parks.MODERN_GYEDONG_BUILDING,
    Parks.SUN_HWA_BUILDING,
    Parks.PODO_MALL,
    Parks.MERCURE_AMBASSADOR,
    Parks.HOTEL_SUNSHINE,
    Parks.GS_GUN_GUK_BUILDING,
    Parks.NC_GANG_NAM,
    Parks.FINE_AVENUE,
]

type_to_search_css = {
    AJ_PARK: "body > div.wrap > section > div > section > div:nth-child(2) > div > dl:nth-child(4) > dd",
    AMANO: "#modal-window > div > div > div.modal-text",
    BLUE: "#divAjaxCarList > tr",
    DARAE: "#search_form > table > tbody > tr:nth-child(2) > td",
    GRANG_SEOUL: "#carList > table > tbody > tr > td:nth-child(2) > a",
    GS: "#divAjaxCarList > tbody > tr",
    HIGH_CITY: "#search_form > table > tbody > tr > td:nth-child(2) > table:nth-child(3) > tbody > tr:nth-child(2)",
    IP_TIME: "#DataGrid1 > tbody > tr:nth-child(2) > td:nth-child(1)",
    HIGH_CITY_2: "#search_form > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(2)",
    OLD_AJ: "body > table:nth-child(4) > tbody > tr:nth-child(3) > td:nth-child(2)"
}

mapToAgency = {
    HIGH_CITY: "#search_form > table > tbody > tr > td:nth-child(2) > table:nth-child(3) > tbody > tr:nth-child(2) > "
               "td:nth-child(2)",
    AMANO: "#gridMst > div.objbox > table > tbody > tr.ev_dhx_skyblue.rowselected > td.cellselected",
    BLUE: "#carDetail > table:nth-child(1) > tbody > tr:nth-child(1) > td:nth-child(2)",
    DARAE: "#search_form > table > tbody > tr:nth-child(2) > td:nth-child(2)",
    I_PARKING: "#carList > tr > td:nth-child(2)",
    GS: "#divAjaxCarList > tbody > tr > td",
    Parks.T_TOWER: "#tblList > tbody > tr > td:nth-child(2)",
    IP_TIME: "#DataGrid1 > tbody > tr:nth-child(2) > td:nth-child(1)",
    # IP_TIME: "#listSearch > table:nth-child(7) > tbody > tr:nth-child(2)",
    GRANG_SEOUL: "#carList > table > tbody > tr > td:nth-child(2) > a",
    AJ_PARK: "body > div.wrap > section > div > section > div:nth-child(2) > div > dl:nth-child(4) > dd",
    HIGH_CITY_2: "#search_form > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(2)",
    OLD_AJ: "/html/body/table[2]/tbody/tr[3]/td[2]/text()[1]",
    Parks.ORAKAI_DAEHAKRO: "#search_form > table > tbody > tr > td:nth-child(2) > table:nth-child(3) > tbody > tr:nth-child(2) > td:nth-child(2)"
}

mapToHarinUrl = {
    HIGH_CITY: "/discount/discount_regist.asp",
    HIGH_CITY_2: "/discount/discount_regist.asp",
    AMANO: "/discount/registration",
    BLUE: "/index.php/main/index",
    DARAE: "/discount/discount_regist.php",
    I_PARKING: "/html/home.html#!",
    GS: "/main",
    IP_TIME: "/ListSearch.aspx",
    GRANG_SEOUL: "/ezTicket/carSearch",
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
    elif park_id in parkTypeAmano:
        return AMANO
    elif park_id in parkTypeBlue:
        return BLUE
    elif park_id in parkTypeDarae:
        return DARAE
    elif park_id in parkTypeIparking:
        return I_PARKING
    elif park_id in parkTypeGs:
        return GS
    elif park_id in parkType_ip_time:
        return IP_TIME
    elif park_id in parkType_grang_seoul:
        return GRANG_SEOUL
    elif park_id in park_type_aj_park:
        return AJ_PARK
    elif park_id in park_type_etc:
        return ETC
    elif park_id in park_type_old_aj:
        return OLD_AJ
    elif park_id in park_type_nice:
        return NICE
