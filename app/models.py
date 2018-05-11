"""Veri tabanıı ile ilgili tanımlamaların yapıldığı sınıftır.
class sınıfIsmi(Base) ile veritabanı tablosu oluşturulabilir.
__tablename__ = tabloIsmi ile birlikte eğer tablo yok ise oluşturulur, varsa sadece bağlantı sağlanır.
Ger kalan işlemler postgresql de olduğu gibi veri tabanı kolonlarının oluşturulma işlemi gerçekleştirilir.
NOT: User adı ile belirtilmiş olan veritabnı tablosunda çeşitli değişiklikler yapışacaktır. Communication sınıfına bakarak işlemlerinizi yapabilirsiniz."""
from config import DB_URI
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.types import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from uuid import uuid4
from time import time


Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    userId = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    surname = Column(String(20), nullable=False)
    birtdate = Column(DateTime)
    city = Column(String(14), nullable=False)
    gender = Column(String(1), nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(40), unique=True)
    publicId = Column(String(50), unique=True)
    validation = Column(Boolean, nullable=False)

    def __init__(self, name, surname, birtdate, city, gender, password, email, publicId, validation):
        self.name = name
        self.surname = surname
        self.birtdate = birtdate
        self.city = city
        self.gender = gender
        self.password = password
        self.email = email
        self.publicId = publicId
        self.validation = validation

    def to_dict(self):
        return {
            'userId' : self.userId,
            'name' : self.name,
            'surname' : self.surname,
            'birtdate' : self.birtdate,
            'city' : self.city,
            'gender' : self.gender,
            'password' : self.password,
            'email' : self.email,
            'publicId' : self.publicId,
            'validation' : self.validation
        }

class UserInterest(Base):
    __tablename__ = 'userinterest'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    interestId = Column(Integer)

    def __init__(self, userId, interestId):
        self.userId = userId
        self.interestId = interestId

    def to_dict(self):
        return{
            'id' : self.id,
            'userId' : self.userId,
            'interestId' : self.interestId
        }

class Communication(Base):
    __tablename__ = 'communication'

    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String(30), nullable = False)
    email = Column(String(50), nullable = False)
    phone = Column(String(11), nullable = False)
    message = Column(String(400), nullable = False)
    ipaddress = Column(String(15), nullable=False)
    pushdate = Column(DateTime, nullable=False)

    def __init__(self, name, email, phone, message, ipaddress, pushdate):
        self.name = name
        self.email = email
        self.phone = phone
        self.message = message
        self.ipaddress = ipaddress
        self.pushdate = pushdate

    def to_dict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'email' : self.email,
            'phone' : self.phone,
            'message' : self.message,
            'ipaddress' : self.ipaddress,
            'pushdate' : self.pushdate
        }

class Aboutus(Base):
    __tablename__ = 'aboutus'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable = False)
    surname = Column(String(20), nullable=False)
    image = Column(String(100), nullable=False)
    about = Column(String(200), nullable=False)
    facebook = Column(String(100))
    twitter = Column(String(100))
    linkedin = Column(String(100))

    def __init__(self, name, surname, image, about, facebook, twitter, linkedin):
        self.name = name
        self.surname = surname
        self.image = image
        self.about = about
        self.facebook = facebook
        self.twitter = twitter
        self.linkedin = linkedin

    def to_dict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'surname' : self.surname,
            'image' : self.image,
            'about' : self.about,
            'facebook' : self.facebook,
            'twitter' : self.twitter,
            'linkedin' : self.linkedin
        }

class Interest(Base):
    __tablename__ = 'interest'

    id = Column(Integer, primary_key=True, autoincrement=True)
    interestName = Column(String(20), nullable=False)

    def __init__(self, interestName):
        self.interestName = interestName

    def to_dict(self):
        return {
            'id' : self.id,
            'interestName' : self.interestName
        }

# local veritabanı
engine = create_engine(DB_URI)

# tablolar veritabanına kaydedildi.
Base.metadata.create_all(engine)

# Database session oluşturucu oluşturuldu
DBSession = sessionmaker(engine)