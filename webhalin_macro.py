# -*- coding: utf-8 -*-
import os

import requests
import time
import pymysql
import datetime
import logging

import ChromeDriver
import Colors
import GetSql
import LimitLot
from park import ParkType, Parks, ParkUtil
import Util

from agency import NewAmano, Iptime, Gs, HighCity, Iparking, AJpark, Darae, ArcPlace, Blue, HighMhpOpt, Etc, OldAJ, \
    Nice, NiceNew, AplusAsset, CenterSquare, NewKmpark

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

driver = ChromeDriver.get()
driver.implicitly_wait(3)
driver.maximize_window()

'''
# parkId: [id_name, pw_name, login_btn_xpath,
#         search_box_name, search_btn_xpath,
#         check_box,
#         
'''

testPark = 99999
is_park_test = False
is_no_db_test =False #False#True


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


def exec_web_har_in(park_type, target, chrome_driver, lotName=None):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    if park_type == AJpark:
        if AJpark.web_har_in(target,chrome_driver,lotName):
            logging_info(target)
            in_car_check_db(pid, park_id)
            push_fcm_in_car_check(pid)
    elif park_type == CenterSquare :
        if park_type.web_har_in(target):
            in_car_check_db(pid, park_id)
            push_fcm_in_car_check(pid)
            print("센터스퀘어 입차처리성공")
    elif park_type.web_har_in(target, chrome_driver):
        logging_info(target)
        in_car_check_db(pid, park_id)
        push_fcm_in_car_check(pid)
        print("입차처리성공")
    else:
        print("실패")


def web_har_in(target):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    park_type = ParkType.get_park_type(park_id)

    # 아마노코리아
    #if  park_type == ParkType.NEW_AMANO:
    #    exec_web_har_in(NewAmano, target, driver)
    #    return True

    # 나이스파크
    #elif park_type == ParkType.NICE_NEW:
    #   exec_web_har_in(NiceNew, target, driver)
    #   return True

    # 하이파킹
    #elif park_type == ParkType.HIGH_MHP_OPT:
    #    exec_web_har_in(HighMhpOpt, target, driver)
    #    return True

    if park_type == ParkType.HIGH_CITY:
        exec_web_har_in(HighCity, target, driver)
        print(f"park_id: {park_id}, park_type: {park_type}, expected: {ParkType.HIGH_CITY}")
        return True

    #아이파킹사이트(운영업체혼합)
    #elif park_type == ParkType.I_PARKING:
    #    exec_web_har_in(Iparking, target, driver)
    #    print(f"park_id: {park_id}, park_type: {park_type}, expected: {ParkType.I_PARKING}")
    #    return True

    # KMPARK 전용사이트
    #elif park_type == ParkType.NEW_KMPARK:
    #    exec_web_har_in(NewKmpark, target, driver)
    #    return True


    #elif park_type == ParkType.CENTER_SQUARE:
    #    exec_web_har_in(CenterSquare, target, driver)
    #    return True

    #if park_type == ParkType.IP_TIME:
    #    exec_web_har_in(Iptime, target, driver)
    #    return True


    #if park_type == ParkType.GS:
    #    exec_web_har_in(Gs, target, driver)
    #    print(f"park_id: {park_id}, park_type: {park_type}, expected: {ParkType.GS}")
    #    return True







    #elif park_type == ParkType.GS2:
    #    exec_web_har_in(Gs, target, driver)
    #    print(f"park_id: {park_id}, park_type: {park_type}, expected: {ParkType.GS2}")
    #    return True

    #elif park_type == ParkType.DARAE:
    #    exec_web_har_in(Darae, target, driver)
    #    return True

    #elif park_type == ParkType.BLUE:
    #    exec_web_har_in(Blue, target, driver)
    #    return True


    #elif park_type == ParkType.ETC:
    #    exec_web_har_in(Etc, target, driver)
    #    return True


    else:
        print(Colors.BLUE + "웹할인 페이지가 없는 주차장 입니다." + Colors.ENDC)


repeatCnt = 0



while True:
    conn = pymysql.connect(host='49.236.134.172', port=3306, user='root', password='#orange8398@@',
                           db='parkingpark',
                           charset='utf8')
    curs = conn.cursor()
    #test
    if is_no_db_test:
        tempTarget1 = ['0', '19430', '32가 6187 ', '평일1일권', '2021-11-29 08:00:00', '202111290800']
        tempTarget2 = ['0', '19430', '55하4461 ', '평일1일권', '2021-11-29 08:00:00', '202111290800']


        try:
            web_har_in(tempTarget1)
            web_har_in(tempTarget2)

            break
        except Exception as ex:
            print(Colors.RED + str(ex) + Colors.ENDC)
    else:
        repeatCnt += 1
        logger.info("반복 횟수 : " + str(repeatCnt))


        now = datetime.datetime.now()
        nowYM = now.strftime('%Y%m')
        nowDate = now.strftime('%Y%m%d')

        log_dir = './logs/' + nowYM

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        nowTime = now.strftime('%H%M')
        file_name = nowDate + "_" + nowTime + "_" + str(repeatCnt) + ".txt"

        file_url = log_dir + "\\" + file_name

        file_handler = logging.FileHandler(file_url, encoding="utf-8")
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
                print("예정 시간  - " + targetTime[0:2]+"시 "+targetTime[2:4]+"분")
                print("현재 시간  - " + nowTime[0:2]+"시 "+nowTime[2:4]+"분")
                # if(ParkUtil.timeCheck(nowTime, targetTime)):
                #     print("예정입차시간 < 현재시간")
                web_har_in(i)
                # else:
                #     print("입차시간이 아직 되지 않았음.")
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

        # 🔄 매 5회마다 크롬 드라이버 재시작
        if repeatCnt % 4 == 0:
            print("🔄 driver 재시작")
            try:
                driver.quit()
            except Exception as e:
                print(Colors.RED + f"드라이버 종료 중 오류: {e}" + Colors.ENDC)

            try:
                driver = ChromeDriver.get()
                driver.implicitly_wait(3)
                driver.maximize_window()
                print("✅ 드라이버 재시작 완료")
            except Exception as e:
                print(Colors.RED + f"드라이버 재생성 실패: {e}" + Colors.ENDC)

    time.sleep(600)

    print("메크로 재시작")
