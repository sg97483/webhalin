# -*- coding: utf-8 -*-
import requests
import time
import pymysql
import datetime
import logging

import ChromeDriver
import Colors
import LimitLot
import ParkType
import Parks
import Util

from agency import Iptime, Gs, HighCity, Iparking, AJpark, Darae, Amano, Blue, Etc, OldAJ, GrangSeoul, Nice

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

driver = ChromeDriver.get()
driver.implicitly_wait(3)

'''
# parkId: [id_name, pw_name, login_btn_xpath,
#         search_box_name, search_btn_xpath,
#         check_box,
#         
'''

testPark = Parks.DONGSAN_GONGYEONG
is_park_test = True
is_no_db_test = False


# is_part_test = True


def get_sql(now_date):
    valid_lots = [
        '16239', '18904', '18901', '12868', '18913', '15683', '18937', '18936', '15313', '45674', '11558', '18970',
        '18956', '16175', '16184', '20863', '15437', '16001', '18969', '18972', '18973', '18971', '18964', '15740',
        '12845', '12936', '12903', '18996', '18997', '12313', '11367', '19004', '12951', '18995', '4588', '18991',
        '70004', '70005', '70006', '19030', '19029', '19031', '16170', '19028', '19038', '12872', '19020', '19017',
        '19010', '19044', '18967', '12750', '19047', '16105', '15619', '19048', '19056', '19063', '19061', '2810',
        '16209', '19066', '19064', '19065', '19070', '19071', '19077', '19078', '19081', '19080', '28864', '15644',
        '18930', '11349', '16210', '19084', '19082', '13825', '16360', '19087', '19083', '45655', '12806', '19040',
        '15591', '19000', '12997', '11917', '12124', '12184', '13007', '19091', '15008', '19043', '15160', '16003',
        '19090', '18577', '16173', '22982', '19086', '12904', '16215', '19085', '18981', '18999', '12817', '19101',
        '19111', '19112', '14506', '14994', '12130', '19089', '12050', '19119', '70008', '70009', '70010', '19120',
        '19121', '18966', '18957', '15309', '12532', '12749', '19116', '19124', '19125', '12929', '19128', '35546',
        '19126', '14541', '19110', '19131', '19100', '16096', '12539', '45009', '12183', '19136', '18963', '18959',
        '19138', '19151',
        '11290', '15639', '19155', '18968', '45304', '19166', '19168', '14618', '19172', '19170', '19171', '18958',
        '19173', '19174',
        '19139', '19140', '19141', '19142', '19143', '19145', '19146', '19147', '19148', '19149', '19156', '19157',
        '19158', '19162',
        '19160',
        '19180', '19183', '19181', '19182', '19188', '19189', '19190',
        '19198',
        '12766',
        '19073', '19194', '19197', '19193',
        '19208', '19203', '19191', '19235',
        '19230', '14588', '19202', '19022', '19159', '19234',
        '19215', '19241', '19196', '19248', '19247',
        '19219', '19218', '19212', '19267', '19250', '19240', '19239', '19161', '19272', '19271',
        '19199', '19206', '19258',
        # 여기서부터 나이스파크
        '19280', '19281', '19282', '19283', '19284', '19285', '19286', '19287', '19288', '19289', '19290',
        '19291', '19292', '19293', '19294', '19295', '19296', '19297', '19298', '19299', '19300',
        '19301', '19302', '19303', '19304', '19305', '19306', '19307', '19308', '19309', '19310',
        '19311', '19312',
        # 나이스 신규현장 끝
        '19238', '19210', '19226', '19321', '19276'
    ]

    str_lots = ", ".join(valid_lots)
    parking_lot_range = "(" + str_lots + ")"

    logger.info("today is : " + now_date + "\n")
    sql = "SELECT id, parkId, agCarNumber, totalTicketType FROM T_PAYMENT_HISTORY WHERE " \
          "parkId IN " + parking_lot_range + " " \
          "AND cancelledYN IS NULL " \
          "AND (inCarCheck = 'N' OR actualInDtm IS NOT NULL) " \
          "AND reservedStDtm LIKE '" + now_date + "%' " \
          "AND TotalTicketType NOT LIKE '월주차%' " \
          "AND TotalTicketType NOT LIKE '월연장%' " \
          "AND TotalTicketType NOT LIKE '%자동결제%' " \
          "AND actualOutDtm IS NULL " \
          "AND agHp = 0 "

    if is_park_test:
        sql += "AND parkId IN ('" + str(testPark) + "') "

    sql += "ORDER BY actualInDtm DESC, parkId DESC;"
    # "ORDER BY actualInDtm ASC, parkId ASC;"
    # "ORDER BY actualInDtm DESC, parkId DESC;"
    # "AND parkId IN ('" + str(testPark) + "') " \
    return sql


# WebHarIn page Login info
parkName = 0
webHarInId = 1
webHarInPw = 2
webHarInType = 3

# WebHarIn page components info
inputId = 0
inputPw = 1
btnLogin = 2
inputSearch = 3
btnSearch = 4
btnItem = 5
methodHarIn1 = 6
methodHarIn2 = 7
methodHarIn3 = 8
methodHarInFunc = 9
# btnLogOut = 10

connParkId = []


def logging_info(target):
    log_pid = target[0]
    log_park_id = Util.all_trim(target[1])
    log_car_number = Util.all_trim(target[2])
    log_ticket_name = target[3]

    log_info = "pid : " + str(log_pid) + " \n" + \
               "parkId : " + str(log_park_id) + "\n" + \
               "oriCarNum : " + log_car_number + "\n" + \
               "ticketName : " + log_ticket_name

    logger.info(log_info)


def in_car_check_db(pid, park_id):
    sql_in_car_check = "UPDATE T_PAYMENT_HISTORY SET inCarCheck = 'Y', agHp = 1 WHERE id ='" + str(pid) + "'"
    curs.execute(sql_in_car_check)
    conn.commit()
    logger.info(" 할인 되었습니다. / \"" + Parks.mapIdToUrl[park_id] + "\"")
    logger.info("\n")


def push_fcm_in_car_check(pid):
    # print(Colors.BLUE + "푸쉬 발송 테스트 : " + str(pid) + Colors.ENDC)
    api_host = "http://cafe.wisemobile.kr:8080"
    params_get = "?msgType=parked&id=" + str(pid)
    url_push_fcm = api_host + "/fcm/sendFcmTest" + params_get

    headers = {'Content-Type': 'application/json', 'charset': 'UTF-8', 'Accept': '*/*'}

    try:
        response = requests.get(url_push_fcm, headers=headers)
    except Exception as exPush:
        print(Colors.BLUE + "푸쉬 리퀘스트 에러 : " + exPush + Colors.ENDC)

    print(Colors.BLUE + "푸쉬 발송 완료 : " + str(response) + Colors.ENDC)


def exec_web_har_in(park_type, target, chrome_driver):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))

    if park_type.web_har_in(target, chrome_driver):
        logging_info(target)
        in_car_check_db(pid, park_id)
        push_fcm_in_car_check(pid)
    else:
        print("실패")


def web_har_in(target):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    park_type = ParkType.get_park_type(park_id)

    if park_type == ParkType.HIGH_CITY or park_type == ParkType.HIGH_CITY_2:
        exec_web_har_in(HighCity, target, driver)
        return True

    elif park_type == ParkType.AMANO:
        exec_web_har_in(Amano, target, driver)
        return True

    elif park_type == ParkType.GS:
        exec_web_har_in(Gs, target, driver)
        return True

    elif park_type == ParkType.I_PARKING:
        exec_web_har_in(Iparking, target, driver)
        return True

    elif park_type == ParkType.DARAE:
        exec_web_har_in(Darae, target, driver)
        return True

    elif park_type == ParkType.BLUE:
        exec_web_har_in(Blue, target, driver)
        return True

    elif park_type == ParkType.IP_TIME:
        exec_web_har_in(Iptime, target, driver)
        return True

    elif park_type == ParkType.AJ_PARK:
        exec_web_har_in(AJpark, target, driver)
        return True

    elif park_type == ParkType.ETC:
        exec_web_har_in(Etc, target, driver)
        return True

    elif park_type == ParkType.OLD_AJ:
        exec_web_har_in(OldAJ, target, driver)
        return True

    elif park_type == ParkType.GRANG_SEOUL:
        exec_web_har_in(GrangSeoul, target, driver)
        return True

    elif park_type == ParkType.NICE:
        exec_web_har_in(Nice, target, driver)
        return True

    elif park_id == Parks.GRANG_SEUOL:
        exec_web_har_in(GrangSeoul, target, driver)
        return True

    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)


repeatCnt = 0

while True:
    # if is_part_test:
    #     print(Colors.BLUE + "퓌쉬 테스트 시작" + Colors.ENDC)
    #     pid = 235564
    #     push_fcm_in_car_check(pid)

    if is_no_db_test:
        # pid, park_id
        # id, parkId, agCarNumber, totalTicketType
        tempTarget1 = ['0', '18913', '47보9363', '평일1일권']
        tempTarget2 = ['0', '18577', '296루7472', '평일1일권']

        try:
            web_har_in(tempTarget1)
            web_har_in(tempTarget2)
        except Exception as ex:
            print(Colors.RED + str(ex) + Colors.ENDC)
    else:
        repeatCnt += 1
        logger.info("반복 횟수 : " + str(repeatCnt))

        conn = pymysql.connect(host='49.236.134.172', port=3306, user='root', password='#orange8398@@',
                               db='parkingpark',
                               charset='utf8')
        curs = conn.cursor()

        now = datetime.datetime.now()

        nowDate = now.strftime('%Y%m%d')
        newFolder = 'C:/Users/wisemobile5/Desktop/WEBHALIN/' + nowDate

        nowTime = now.strftime('%H%M')
        file_name = nowDate + "_" + nowTime + "_" + str(repeatCnt) + ".py"

        file_url = newFolder + "\\" + file_name

        # logging.basicConfig(file_name= file_url', file_name)

        file_handler = logging.FileHandler(file_name, encoding="utf-8")
        streamHandler = logging.StreamHandler()
        logger.addHandler(file_handler)
        logger.addHandler(streamHandler)

        curs.execute(get_sql(nowDate))
        rows = curs.fetchall()

        logger.info("웹할인 체크 필요 개수 : " + str(len(rows)))

        for i in rows:
            print(i, sep='\n')

            try:
                web_har_in(i)
            except Exception as ex:
                print(Colors.RED + str(ex) + Colors.ENDC)

        print("웹할인 체크 필요 개수 : " + str(len(rows)))
        print(Colors.GREEN + "메크로 일시정지" + Colors.ENDC)

        logger.removeHandler(streamHandler)
        logger.removeHandler(file_handler)

        conn.close()

        if not is_park_test:
            try:
                LimitLot.do_limit_lot(driver)
            except Exception as ex:
                print(Colors.RED + str(ex) + Colors.ENDC)

    time.sleep(1000)

    print("메크로 재시작")
