"""Bu dosyayı mümkün olduğunca değiştirmeyin.
Dosyada yapılacak değişiklik DB_URI ile tanımlanmış kısımdır.
DB_URI veritabanının oluşturulacağı yeri gösterir.
DB_URI formatı şu şekildedir. postgresql://kullanıcı_ismi:şifre@localhost/veritabanının_ismi"""
import os

DEBUG = True
SECRET_KEY = os.urandom(24)
DB_URI = 'postgresql://postgres:admin@localhost/activity'
SQLALCHEMY_TRACK_MODIFICATIONS = False