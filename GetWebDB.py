def get_url():
    sql = "SELECT parkId, url FROM T_PARKING_WEB"
    # id, parkId, url, urlId, urlPw, state
    return sql

def get_IdPw():
    sql = " SELECT web.parkId, lot.garageName, web.urlId, web.urlPw FROM T_PARKING_WEB as web " \
          " JOIN T_PARKING_LOT as lot ON lot.id = web.parkId "

    return sql
