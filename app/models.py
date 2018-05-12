"""Veri tabanıı ile ilgili tanımlamaların yapıldığı sınıftır.
class sınıfIsmi(Base) ile veritabanı tablosu oluşturulabilir.
__tablename__ = tabloIsmi ile birlikte eğer tablo yok ise oluşturulur, varsa sadece bağlantı sağlanır.
Ger kalan işlemler postgresql de olduğu gibi veri tabanı kolonlarının oluşturulma işlemi gerçekleştirilir.
NOT: User adı ile belirtilmiş olan veritabnı tablosunda çeşitli değişiklikler yapışacaktır. Communication sınıfına bakarak işlemlerinizi yapabilirsiniz."""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from config import DB_URI
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

class Etkinlik(Base):
    __tablename__ = 'etkinlik'

    e_id = Column(Integer, primary_key=True, autoincrement = True)
    etklinlikTipi = Column(String(30), nullable=False)
    etkinlikAdı = Column(String(100), nullable=False)
    etkinlikAcıklaması = Column(String(1000), nullable=False)
    iletisimBilgileri = Column(String(200))
    yıldızPuanToplamı = Column(Integer, nullable=False)
    yıldızVerenSayısı = Column(Integer, nullable=False)
    banlanmısMı = Column(Integer, default=0, nullable=False)
    tarih = Column(DateTime, nullable=False)
    yayınlayan = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            'e_id': self.e_id,
            'etklinlikTipi': self.etklinlikTipi,
            'etkinlikAdı': self.etkinlikAdı,
            'etkinlikAcıklaması': self.etkinlikAcıklaması,
            'iletisimBilgileri': self.iletisimBilgileri,
            'yıldızPuanToplamı': self.yıldızPuanToplamı,
            'yıldızVerenSayısı': self.yıldızVerenSayısı,
            'banlanmısMı': self.banlanmısMı,
            'tarih': self.tarih,
            'yayınlayan': self.yayınlayan
        }

class EtkinlikResim(Base):
    __tablename__ = 'etkinlikResim'

    etk_resim_id = Column(Integer, primary_key=True, autoincrement = True)
    etkinlikBilgi = Column(String(60), nullable=False)

    def to_dict(self):
        return {
            'etk_resim_id': self.etk_resim_id,
            'etkinlikBilgi': self.etkinlikBilgi
        }

class EtkinlikTipi(Base):
    __tablename__ = 'etkinlikTipi'

    tip_id = Column(Integer, primary_key=True)
    tipAdı = Column(String(30), nullable=False)

    def to_dict(self):
        return {
            'tip_id': self.tip_id,
            'tipAdı': self.tipAdı
        }

class Özellik(Base):
    __tablename__ = 'özellik'

    özellik_id = Column(Integer, primary_key=True)
    özellikBilgi = Column(String(30), nullable=False)

    def to_dict(self):
        return {
            'özellik_id': self.özellik_id,
            'özellikBilgi': self.özellikBilgi
        }

class Sikayet(Base):
    __tablename__ = 'sikayet'

    sikayet_id = Column(Integer, primary_key=True, autoincrement = True)
    sikayet_eden_id = Column(Integer, ForeignKey("kullanıcı.k_id", onupdate='CASCADE', ondelete='CASCADE'))
    k_id = Column(Integer, ForeignKey("kullanıcı.k_id", onupdate='CASCADE', ondelete='CASCADE'))
    e_id = Column(Integer, ForeignKey("etkinlik.e_id", onupdate='CASCADE', ondelete='CASCADE'))
    sikayetMetni = Column(String(200), nullable=False)
    sikayetTarihi = Column(DateTime, nullable=False)
    deger = Column(Integer)

    def __init__(self, sikayet_eden_id, k_id, e_id, sikayetMetni, sikayetTarihi,deger):
        self.sikayet_eden_id = sikayet_eden_id
        self.k_id = k_id
        self.e_id = e_id
        self.sikayetMetni = sikayetMetni
        self.sikayetTarihi = sikayetTarihi
        self.deger = deger

    def to_dict(self):
        return {
            'sikayet_id': self.sikayet_id,
            'sikayet_eden_id': self.sikayet_eden_id,
            'k_id': self.k_id,
            'e_id': self.e_id,
            'sikayetBaslık': self.sikayetBaslık,
            'sikayetTarihi': self.sikayetTarihi
        }

class Yorum(Base):
    __tablename__ = 'yorum'

    yorum_id = Column(Integer, primary_key=True, autoincrement=True)
    k_id = Column(Integer, ForeignKey("kullanıcı.k_id", onupdate='CASCADE', ondelete='CASCADE'))
    e_id = Column(Integer, ForeignKey("etkinlik.e_id", onupdate='CASCADE', ondelete='CASCADE'))
    yorumMetni = Column(String(30), nullable=False)
    yorumTarihi = Column(DateTime, nullable=False)

    def __init__(self, k_id, e_id, yorumMetni, yorumTarihi):
        self.k_id = k_id
        self.e_id = e_id
        self.yorumMetni = yorumMetni
        self.yorumTarihi = yorumTarihi

    def to_dict(self):
        return {
            'yorum_id': self.yorum_id,
            'k_id': self.k_id,
            'e_id': self.e_id,
            'yorumMetni': self.yorumMetni,
            'yorumTarihi': self.sikayetTarihi
        }

class EtkinlikÖzellik(Base):
    __tablename__ = 'etkinlik_özellik'

    id = Column(Integer, primary_key=True, autoincrement = True)
    e_id = Column(Integer, ForeignKey("etkinlik.e_id", onupdate='CASCADE', ondelete='CASCADE'))
    özellik_id = Column(Integer, ForeignKey("özellik.özellik_id", onupdate='CASCADE', ondelete='CASCADE'))
    bilgi = Column(String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'e_id': self.e_id,
            'özellik_id': self.özellik_id,
            'bilgi': self.bilgi
        }

class EtkinlikResimleri(Base):
    __tablename__ = 'etkinlik_resim'

    id = Column(Integer, primary_key=True)
    resim_id = Column(Integer, ForeignKey("etkinlikResim.etk_resim_id", onupdate='CASCADE', ondelete='CASCADE'))
    e_id = Column(Integer, ForeignKey("etkinlik.e_id", onupdate='CASCADE', ondelete='CASCADE'))

    def to_dict(self):
        return {
            'id': self.id,
            'resim_id': self.resim_id,
            'e_id': self.e_id
        }

class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mail = Column(String(40), nullable=False)
    password = Column(String(100), nullable=False)

    def __init__(self, mail, password):
        self.mail = mail
        self.password = password

    def to_dict(self):
        return{
            'id': self.id,
            'mail': self.mail,
            'password': self.password
        }

# local veritabanı
engine = create_engine(DB_URI)

# tablolar veritabanına kaydedildi.
Base.metadata.create_all(engine)

# Database session oluşturucu oluşturuldu
DBSession = sessionmaker(engine)