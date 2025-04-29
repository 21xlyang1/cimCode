import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sdhukiaad'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://king:123king@103.242.3.44:3306/cim_db?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
