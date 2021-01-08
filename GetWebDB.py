def get_url(parkId):
    sql = "SELECT url FROM T_PARKING_WEB"
    # id, parkId, url, urlId, urlPw, state
    return sql

def get_IdPw(parkId):
    sql = "SELECT urlId, urlPw FROM T_PARKING_WEB"

    return sql
