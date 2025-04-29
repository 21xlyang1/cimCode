import pymysql

# 数据库配置信息
HOSTNAME = '103.242.3.44'
PORT = 3306
USERNAME = 'king'
PASSWORD = '123king'
DATABASE = 'cim_db'

def get_rtsp_url_by_id(rtsp_id):
    connection = pymysql.connect(
        host=HOSTNAME,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE,
        charset='utf8mb4'
    )

    try:
        with connection.cursor() as cursor:
            sql = "SELECT rtsp_url FROM rtsp WHERE rtspId = %s"
            cursor.execute(sql, (rtsp_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
    finally:
        connection.close()

# 示例：查询 ID 为 23 的 rtsp_url
rtsp_url = get_rtsp_url_by_id(23)
print(f"RTSP URL for ID 23: {rtsp_url}")
