"""Bu dosyayı mümkün olduğunca değiştirmeyin.
Dosyada yapılacak değişiklik DB_URI ile tanımlanmış kısımdır.
DB_URI veritabanının oluşturulacağı yeri gösterir.
DB_URI formatı şu şekildedir. postgresql://kullanıcı_ismi:şifre@localhost/veritabanının_ismi"""
import os

DEBUG = True
SECRET_KEY = os.urandom(24)
DB_URI = 'postgresql://postgres:admin@localhost/activity_db1'
SQLALCHEMY_TRACK_MODIFICATIONS = False
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'modul.etkinlik@gmail.com'
MAIL_PASSWORD = 'etkinlik1996'