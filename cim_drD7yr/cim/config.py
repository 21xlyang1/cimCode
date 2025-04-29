# 数据库的配置信息
HOSTNAME = '103.242.3.44'
PORT = '3306'
USERNAME = 'king'
PASSWORD = r'123king'
DATABASE = 'cim_db'

DB_UPI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"
SQLALCHEMY_DATABASE_URI = DB_UPI

SECRET_KEY = 'sdhukiaad'
