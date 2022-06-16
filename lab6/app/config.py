import os

SECRET_KEY = '23d3b6f20c9f30401fada81ee601b7a172ba104e6b1316075a48af58ea871f8f'
MYSQL_USER = 'std_1684_lab6'
MYSQL_HOST = 'std-mysql.ist.mospolytech.ru'
MYSQL_DATABASE = 'std_1684_lab6'
MYSQL_PASSWORD = 'Gg9772891'
MYSQL_PORT = '3306'
ADMIN_ROLE_ID = 2

SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')
