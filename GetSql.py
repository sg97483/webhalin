import datetime

def get_sql(now_date, logger, is_park_test, testPark):
    logger.info("today is : " + now_date + "\n")

    now = datetime.datetime.now()
    current_hour = now.hour
    current_time = now.strftime('%H%M')  # 현재 시간 HHMM 포맷

    if current_hour < 4:
        # 새벽 4시 이전이면 전날 데이터 포함
        prev_date = (now - datetime.timedelta(days=1)).strftime('%Y%m%d')
        sql = (
            "SELECT pay.id, web.parkId, pay.agCarNumber, pay.totalTicketType, pay.createDate, pay.reservedStDtm "
            "FROM T_PARKING_WEB as web "
            "JOIN T_PAYMENT_HISTORY as pay ON web.parkId = pay.parkId "
            "AND cancelledYN IS NULL "
            "AND inCarCheck = 'N' "
            "AND ( "
            "    (reservedStDtm LIKE '{today}%' AND reservedEdDtm LIKE '{today}%') "
            "    OR "
            "    (reservedStDtm LIKE '{prev}%' AND reservedEdDtm LIKE '{prev}%' AND inCarCheck = 'N') "
            ") "
            "AND TotalTicketType NOT LIKE '월주차%' "
            "AND TotalTicketType NOT LIKE '월연장%' "
            "AND TotalTicketType NOT LIKE '%자동결제%' "
            "AND actualOutDtm IS NULL "
            "AND agHp = 0 "
        ).format(today=now_date, prev=prev_date)

    else:
        # 기본 쿼리 (오늘 날짜 예약건만 조회)
        sql = (
            "SELECT pay.id, web.parkId, pay.agCarNumber, pay.totalTicketType, pay.createDate, pay.reservedStDtm "
            "FROM T_PARKING_WEB as web "
            "JOIN T_PAYMENT_HISTORY as pay ON web.parkId = pay.parkId "
            "AND cancelledYN IS NULL "
            "AND inCarCheck = 'N' "
            "AND reservedStDtm LIKE '{today}%' "
            "AND reservedEdDtm LIKE '{today}%' "
            "AND TotalTicketType NOT LIKE '월주차%' "
            "AND TotalTicketType NOT LIKE '월연장%' "
            "AND TotalTicketType NOT LIKE '%자동결제%' "
            "AND actualOutDtm IS NULL "
            "AND agHp = 0 "
        ).format(today=now_date)

        # 💡 현재 시간이 오후 1시 이전이면, reservedStDtm이 현재 시간 이하인 데이터만 조회
        if current_hour < 13:
            #sql += " AND SUBSTRING(reservedStDtm, 9, 4) <= '{current_time}' ".format(current_time=current_time)
            sql += " AND SUBSTRING(reservedStDtm, 9, 4) <= '1159' "

        # ✅ 심야/야간 제외 조건 (08:00~15:59 사이만)
        if 8 <= current_hour < 16:
            logger.info("현재 시간은 08~16시 사이입니다. 심야/야간권 제외 필터 적용됨.")
            sql += " AND TotalTicketType NOT LIKE '%심야%' "
            sql += " AND TotalTicketType NOT LIKE '%야간%' "

    # 테스트 주차장 필터
    if is_park_test:
        sql += " AND parkId IN ('" + str(testPark) + "') "

    sql += " ORDER BY reservedStDtm ASC;"

    return sql


def get_garageName(parkId):
    sql = "SELECT garageName FROM T_PARKING_LOT WHERE id = '" + str(parkId) + "'"

    return sql