# -*- coding: utf-8 -*-
import requests
import time
import pymysql
import datetime
import logging

import ChromeDriver
import Colors
import GetSql
import LimitLot
from park import ParkType, Parks
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

testPark = Parks.NICE_HONG_MUN_KWAN
is_park_test = False
is_no_db_test = False

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
    api_host = "http://cafe.wisemobile.kr:8080"
    params_get = "?msgType=parked&id=" + str(pid)
    url_push_fcm = api_host + "/fcm/sendFcmTest" + params_get

    headers = {'Content-Type': 'application/json', 'charset': 'UTF-8', 'Accept': '*/*'}

    try:
        response = requests.get(url_push_fcm, headers=headers)
        print(Colors.BLUE + "푸쉬 발송 완료 : " + str(response) + Colors.ENDC)
    except Exception as exPush:
        print(Colors.BLUE + "푸쉬 리퀘스트 에러 : " + exPush + Colors.ENDC)


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
    if is_no_db_test:
        tempTarget1 = ['0', '19208', '43라0120', '평일1일권', '2020-12-03 12:00:00', '202101040000']

        try:
            web_har_in(tempTarget1)
            break
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
        file_name = nowDate + "_" + nowTime + "_" + str(repeatCnt) + ".txt"

        file_url = newFolder + "\\" + file_name

        file_handler = logging.FileHandler(file_name, encoding="utf-8")
        streamHandler = logging.StreamHandler()
        logger.addHandler(file_handler)
        logger.addHandler(streamHandler)

        curs.execute(GetSql.get_sql(nowDate, logger, is_park_test, testPark))
        rows = curs.fetchall()

        logger.info("웹할인 체크 필요 개수 : " + str(len(rows)))

        for i in rows:
            print(i, sep='\n')

            try:
                targetTime = i[5][8:12]
                print("예정입차시간 - "+targetTime[0:2]+"시 "+targetTime[2:4]+"분")
                if(targetTime<nowTime):
                    print("예정입차시간 < 현재시간")
                    web_har_in(i)
                else:
                    print("입차시간이 아직 되지 않았음.")
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

    time.sleep(300)

    print("메크로 재시작")
