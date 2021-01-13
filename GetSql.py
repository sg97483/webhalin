def get_sql(now_date, logger, is_park_test, testPark):
    logger.info("today is : " + now_date + "\n")
    sql = "SELECT pay.id, web.parkId, pay.agCarNumber, pay.totalTicketType, pay.createDate, pay.reservedStDtm FROM T_PARKING_WEB as web " \
          "JOIN T_PAYMENT_HISTORY as pay ON web.parkId = pay.parkId " \
          "AND cancelledYN IS NULL " \
          "AND (inCarCheck = 'N' OR actualInDtm IS NOT NULL) " \
          "AND reservedStDtm LIKE '" + now_date + "%' " \
          "AND reservedEdDtm LIKE '" + now_date + "%' " \
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

def get_garageName(parkId):
    sql = "SELECT garageName FROM T_PARKING_LOT WHERE id = '" + parkId

    return sql