# -*- coding: utf-8 -*-
import pymysql

import Colors
import GetWebDB

conn = pymysql.connect(host='49.236.134.172', port=3306, user='root', password='#orange8398@@',
                               db='parkingpark',
                               charset='utf8')
curs = conn.cursor()


curs.execute(GetWebDB.get_url())
rows = curs.fetchall()
mapIdToUrl = {}
for i in rows:
    try:
        mapIdToUrl[int(i[0])] = i[1]

    except Exception as ex:
        print(Colors.RED + str(ex) + Colors.ENDC)


curs.execute(GetWebDB.get_IdPw())
rows = curs.fetchall()
lotOptionList = {}
for i in rows:
    lotOptionList[int(i[0])] = [str(i[1]), str(i[2]), str(i[3])]


NON = 0
DONGIL_TOWER = 15313
PLATINUM = 12130
NAMSAN_SQUARE = 13007
WISE_PARK = 15644
T_TOWER = 16239
Y_PLUS = 19028
PARK_M = 19121
PARK_M_NIGHT = 19124
K_SQUARE = 11917
ECC = 12050
GYEONG_BOK_GUNG = 4588
AIA = 18958
G_VALLY = 28864
DONGHWA_BUILDING = 19082
URBAN_PLACE_HOTEL = 18967
MAJESTA = 18966
GUUI_WELLTZ = 15437
ICON_YEOKSAM = 15008
ECHO_TERRACE = 14994
WISE_TOWER = 12904
FINANCE_TOWER = 12539
HI_INSADONG = 19166
SI_TOWER = 19136
ARK_PLACE = 11349
PACIFIC_TOWER = 19151
SEOUL_GIROKWON = 19128
ALPHA_DOM_TOWER = 19089
N_TOWER = 19077
KIUM_NADEGI = 19063
DMC_S_CITY = 19044
SC_BANK = 12750
SIGNATURE_TOWER = 12951
DDMC = 15619
DMCC = 15639
TWIN_CITY = 16003
HSBC = 16184
CITY_PLAZA = 18956
CITY_PLAZA_2 = 18970
AUTOWAY_TOWER = 15309
NUN_SQUARE = 12929
NAMSAN_TOWER = 16175
SK_MYEONGDONG = 14618
PODO_MALL = 11558
CENTER_PLACE = 16210
WEST_GATE = 18913
HANWHA_BUILDING = 18972
LOTTE_L7 = 19038
MEGABOX_SUNGSU = 19168
TWIN_TREE = 12868
FAST_FIVE_TOWER = 16170
E_WHA_APM = 18959
SAMSUNG_SERVICE_BUILDING = 19048
GOLDEN_TOWER = 18577
CENTRAL_PLACE = 12997
WEWORK_TOWER = 19086
GRANG_SEUOL = 12872
JUMP_MILAN = 11367
TAEPYEONGRO_BUILDING = 19090
NONHYEON_BUILDING = 11290
RIVER_TOWER = 20863
JS_HOTEL = 19155
ECC_MONTH = 19119
URBANIEL_HAN_GANG = 19056
TS_ONE = 18981
KTB_BUILDING = 16360
SAMSUNG_SEOUL_MEDICAL_CENTER = 18963
RAMIAN_YONGSAN_THE_CENTRAL = 19138
W_SQARE = 12183
DGB_FINANCE_CENTER = 18971
PAN_GYO_ALPHARIUM_TOWER = 18996
ERE_BUILDING = 19100
CENTRAL_TOWER = 16215
JANG_AN_SPIZON = 19110
JIN_YANG_BUILDING = 19000
KDB_LIFE = 45655
KI_TOWER = 19091
YEOKSAM_BUILDING = 19173
HARIM_INTERNATIONAL = 19029
SINRA_STAY_G_TOWER = 18936
JEIL_OPISTEL = 18969
MILLENNIUM_SEOUL_HILTON = 14541
SEOUL_SQAURE = 12903
SUSONG_SQAURE = 19087
ULGI_TWIN_TOWER = 19174
BUILDING_94 = 18957
AJ_EULJIRO_3 = 19139  # AJ파크 을지로3가점
AJ_JONGRO = 19140  # AJ파크 종로관훈점
AJ_T_MARK = 19141  # AJ파크 티마크그랜드호텔점
AJ_JNS = 19142  # AJ파크 영등포 JNS빌딩점
AJ_MDM = 19143  # AJ파크 MDM타워점
AJ_MYUNG_DONG = 19145  # AJ파크 교원명동빌딩점
AJ_GONG_DUK = 19146  # AJ파크 공덕효성해링턴스퀘어점
AJ_MUGYO = 19147  # AJ파크 무교동점
AJ_SEOUL_GARDEN = 19148  # AJ파크 서울가든호텔점
AJ_USIN = 19149  # AJ파크 우신빌딩점
AJ_NON_HYEN = 19156  # AJ파크 논현점
AJ_HAB_JONG = 19157  # AJ파크 합정역점
AJ_DONG_MYO = 19158  # AJ파크 동묘점
AJ_GANG_NAM = 19162  # AJ파크 강남점
AJ_AMSA = 19221 # AJ파크 암사점
URIM_RODEO_SWEET = 45009
AJ_MUNJUNG_PRAVIDA = 19160  # 문정프라비다점
GANG_NAM_L7 = 19004
AJ_MR_HOMZ = 19161
V_PLEX = 18964
COSMO_TOWER = 12184
NY_TOWER = 19190
ACE_TOWER = 16209
MERITZ_FIRE = 19198
ORAKAI_SWEETS = 12766
YANGWOO_DRAMA_CITY = 19073
EG_BUILDING = 19194
O_TWO_TOWER = 19083
ORANGE_CENTER = 19197
JAYANG_PALACE = 19193
ORAKAI_DAEHAKRO = 19181
NICE_HONG_MUN_KWAN = 19208
WESTERN_853 = 18999
MOL_OF_K = 18997
FRYDIUM_BUILDING = 19203
CHUNGJEONGNO_HOUSE = 19191
OMOK_BRIDGE = 19235
GMG_TOWER = 19071
AJ_SINDUK = 19230
CONCORDIAN_BUILDING = 12806
CENTERMARK_HOTEL = 14588
HOTEL_SUNSHINE = 19202
PARK_BUILDING = 19180
KTNG_TOWER = 19084
MUNJUNG_PLAZA = 19022
HONGDAE_EILEX = 19159
MAGOK_RUMA_2 = 19234
OUR_W_TOER = 18968
NONHYEON_WELLSTONE = 19215
DIAT_CENTRAL = 19183
BIT_FLEX = 19241
URBANIEL_CHEN_HO = 19196
KOREANA_HOTEL = 19248
NON_SQUARE = 19247
AJ_BANGBE = 19219
AJ_HOUSE_DIBIZ = 19218
AJ_EWHA = 19212
JEONGAN_BUILDING = 19267
GWANG_HWA_MUN_S_TOWER = 19250
SANGBONG_DUOTRIS = 19240
MDM_TOWER_DANG_SAN = 19239
MODERN_GYEDONG_BUILDING = 12749
SUN_HWA_BUILDING = 16173
HILL_STATE_ECO_MAGOKNARU = 19272
ING_ORANGE_TOWER = 19085
KTNG_SUWON = 22982
GANG_NAM_BUILDING = 19271
MERCURE_AMBASSADOR = 19199
HANA_TOOJA_BUILDING = 19040
# NICE_KUN_KUK_BUILDING = 19206
STATE_TOWER_NAMSAN = 19258
DREAM_TOWER_NIGHT = 18930
DREAM_TOWER_HOLIDAY = 19120
SEOGYO_DONG_NADAEJI = 19238
KUN_KUK_MIDDLE = 19210
AJ_HONG_IK_SPORTS_SPA = 19226
YEOUIDO_NH_CAPITAL = 12532
YANGJAE_GONGYEONG = 19321
DONGSAN_GONGYEONG = 19276
DIAT_GALLERY_2 = 19171
HUMAX_VILLAGE = 19195
SHIN_NON_HYUN_W_TOWER = 12124
D_TOWER = 19325
BANPO_DONG_GONGYONG = 19273
GS_GUN_GUK_BUILDING = 19331
ISU_GONG_YONG = 19236
GAM_SIN_DAE = 19209
AJ_GUWOL_CENTRAL = 16434
NC_GANG_NAM = 19334
JONG_RO_THE_K = 2810
SUWON_STATION_MARKET = 19324
GRAND_CENTRAL = 19364
HAP_JEONG_STATION_YOUTH_HOUSE = 19328
LOTTE_CITY_HOTEL_MYEONG_DONG = 19336
GANG_NAM_FINANCE = 18945
GRACE_TOWER = 45304
MI_SEONG_BUILDING = 19266
NH_GWANG_MYEONG = 19329
FINE_AVENUE = 16212
YEOK_SAM_ECHERE = 19374
HAEUNDAE_IPARK = 19396
MAGOK_SPRINGTOWER = 19081
GANGDONG_HOMEPLUS = 19243
DONGSIN_CHURCH = 16096
URIM_TWIN_PARK = 19397
NEWYORK_PLAZA = 45010
THE_PRIME_TOWER = 16001
SONGPA_BUILDING = 12373
KB_TOWER = 19400

NICE_LOTTECASTLE_PRESIDENT = 19207 # 19207 롯데캐슬프레지던트(상가) 주차장
NICE_KB_BUPYEONG_PLAZA = 19280  # 19280	KB금융 부평프라자	10
NICE_INGYE_CULTURE = 19281  # 19281	경기문화재단 인계동사무소	10
NICE_KYUNGBOK_UNIVERSITY = 19282  # 19282	경복대학교 산학협력관	10
NICE_GOYANG_GLOBAL_THEME_PLAZA = 19283  # 19283	고양 글로벌테마프라자 주차장	10
NICE_GURI_GALMAE_CENTRAL = 19284  # 19284	구리 갈매중앙파크타워	10
NICE_WOLFE = 19286  # 19286	나이스파크 월피점	10
NICE_DAEIL_BUILDING = 19287  # 19287	대일빌딩 주차장	10
NICE_DAEJEON_DUNSAN_CORE_TOWER = 19288  # 19288	대전 둔산코어타워	10
NICE_DAEJEON_WOORIDUL_PARK = 19289  # 19289	대전 우리들공원	10
NICE_DONGTAN_ACEK_CITY_TOWER = 19290  # 19290	동탄 에이스케이시티타워 1주차장(지하)	10
NICE_LOTTE_NESON = 19291  # 19291	롯데슈퍼 내손점	10
NICE_LOTTE_YEON_SU = 19292  # 19292	롯데슈퍼 연수점	10
NICE_LOTTE_POHANG = 19293  # 19293	롯데슈퍼 포항점	10
NICE_MAGOK_INTER_CITY_HOTEL = 19294  # 19294	마곡 인터시티 서울호텔	10
NICE_MOKPO_TERMINAL = 19295  # 19295	목포버스터미널 주차장	10
NICE_BUCHEON_SINEMAJON_BUILDING = 19296  # 19296	부천 시네마존빌딩	10
NICE_SEOSOMUN_CITY_SQUARE = 19297  # 19297	서소문 시티스퀘어	10
NICE_SIHEUNG_SKYDREAM_CITY = 19298  # 19298	시흥 스카이드림씨티	10
NICE_ASAN_ONYANG_TOURIST_HOTEL = 19299  # 19299	아산 온양관광호텔	10
NICE_YANGJU_DREAM_WORLD = 19300  # 19300	양주드림월드	10
NICE_YEONGJONGDO_EUN_SQUARE = 19301  # 19301	영종도 이은스퀘어	10
NICE_OSAN_GEOSEONG_GREEN = 19302  # 19302	오산 거성그린주차장	10
NICE_YONGIN_GRAND_PLAZA = 19303  # 19303	용인그랜드프라자	10
NICE_UDEOK_BUILDING = 19304  # 19304	우덕빌딩 주차장	10
NICE_JEONGJA_DONG = 19305  # 19305	정자동 나이스 주차장	10
NICE_JONGNO_TOWER = 19306  # 19306	종로타워 주차장	10
NICE_JUNG_GU_JUNGDONG_BUILDING = 19307  # 19307	중구 정동빌딩주차장	10
NICE_CHEONGNA_HONGIK = 19309  # 19309	청라 홍익파크	10
NICE_CHEONGNA_COMPETITION_TOWER = 19310  # 19310	청라경연타워 주차장	10
NICE_HANAMS_S_BIZ_TOWER = 19311  # 19311	하남에스비비즈타워	0
NICE_CHEONGGYE_DOOSAN_WEVE_THE_ZENITH = 19326  # 19326	청계천 두산위브더제니스	10
NICE_SAMWON_TOWER = 19330  # 19330	삼원타워주차장	10
NICE_HONGIK_YEMUN = 19338  # 19338	홍익대예문관(비알엘리텔)	10
NICE_DGB = 19362  # 19362	DGB금융센터 주차장	10
NICE_DONGTAN_DONGYEON = 19363  # 19363	동탄 동연주차빌딩	10


