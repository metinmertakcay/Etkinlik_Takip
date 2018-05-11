"""Asıl işlemlerin gerçekleştirildiği yerdir. App adında bir değişken oluşturulması gereklidir. Gerekli configurasyonlar
config dosyası iöçerisinden erişilerek gerçekleştirilecektir.
/ adlı dizinde bizim etkinlik sayfamıza ait olan html koyulacaktır. Şuanda geçici olarak html sayfası oluturulmuştur.
/login login.html sayfasının açılması sağlanır.Kullanıcının sisteme giriş yapması için oluşturulmuştur.
/index ile veritabanına kişi ekleme işlemi gerçekleştirilir. (Bu işlem doğru şekilde gerçekleşip gerçekleşmediğinin kontrolü için kullanılmıştır)
/iletisim Kullanıcının şikayet etmesi durumu için oluşturulmuş sayfadır. Bu sayfada kullanıcının koymuş olduğu ip adresi ve koyma saati gibi
bilgiler saklanacaktır. Anlaşılmayan yer olursa iletişim için metinmakcay@gmail.com adresine mail atabilirsiniz. :))
/ """
from config import SECRET_KEY
from flask import Flask, render_template, request, flash, redirect, url_for, g
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from .models import DBSession, Users, Communication, Aboutus, Interest, UserInterest
from sqlalchemy.sql import text
import socket
import time
import uuid
from sqlalchemy.sql import select, update
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from functools import wraps
import datetime
import jwt

app = Flask(__name__)
app.config.from_object('config')

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'modul.etkinlik@gmail.com',
    MAIL_PASSWORD = 'etkinlik1996',
))

mail = Mail(app)
urlSafeSerializer = URLSafeTimedSerializer(SECRET_KEY)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if tokenv == None:
            return redirect(url_for('routeLogin'))
        try:
            data = jwt.decode(token, SECRET_KEY)
            db = DBSession()
            user = select([Users]).where(Users.publicId == data)
            result = db.execute(user)
        except:
            return redirect(url_for('routeLogin'))

        return f(result, *args, **kwargs)
    return decorated

token = None

@app.route('/index')
@token_required
def index():
    return render_template("index.html")

@app.route('/')
def sample_route():
    return render_template('home.html')

@app.route('/emailGonder',methods=['POST','GET'])
def emailGonder(error=None):
    if request.method == 'POST':
        email = request.form.get('email')

        db = DBSession()
        s = select([Users]).where(Users.email == email)
        result = db.execute(s)

        for user in result:
            sendMailforPasswordChanging(email)
            error = 'Şifre değişimi için mail adresinize mesaj atılmıştır.'
            return render_template('login.html', error=error)
        else:
            error = "Böyle bir mail adresi bulunmamaktadır."
            return render_template('emailGonder.html', error=error)
    return render_template('emailGonder.html', error=error)

def sendMailforPasswordChanging(email):
    token = urlSafeSerializer.dumps(email, salt='email-confirm')
    message = Message('Change Password', sender="modul.etkinlik@gmail.com", recipients=[email])
    link = url_for('forget',token=token,_external=True)
    message.body = 'Your link is {}'.format(link)
    mail.send(message)

@app.route('/forget/<token>', methods=['GET','POST'])
def forget(token):
    if request.method == 'POST':
        try:
            email = urlSafeSerializer.loads(token, salt='email-confirm', max_age=3600)
        except SignatureExpired:
            return "<h1>Token is expired<h1>"
        password = request.form.get('password')
        passwordAgain = request.form.get('passwordAgain')

        db = DBSession()
        if password == passwordAgain:
            stmt = update(Users).where(Users.email == email).values(password=generate_password_hash(password))
            db.execute(stmt)
            db.commit()
            return redirect(url_for('routeLogin'))
    return render_template('forget.html', token=token)

@app.route('/Login', methods=['GET','POST'])
def routeLogin(error=None):

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = DBSession()
        s = select([Users]).where(Users.email == email)
        result = db.execute(s)

        if not(password):
            error = None
        else:
            for row in result:
                if check_password_hash(row['password'], password):
                    if row['validation'] == True:
                        token = jwt.encode({'publicId' : row['publicId'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},SECRET_KEY)
                        return "<h1>Başarıyla giriş yapılmıştır<h1>"
                    else:
                        error = "Geçerli bir email adresi değildir!"
                        return render_template('login.html', error=error)
                else:
                    if password and email:
                        error = "Hatalı mail adresi veya şifre"
                        return render_template('login.html', error=error)
    return render_template('login.html', error=error)

@app.route('/register',methods=['POST','GET'])
def route_register():
    db = DBSession()
    interestList = db.execute("SELECT * FROM Interest")

    if request.method == 'POST':
        name = request.form.get("isim")
        surname = request.form.get("soyisim")
        birthdate = request.form.get("tarih")
        email = request.form.get("email")
        emailAgain = request.form.get("emailTekrar")
        password = request.form.get("sifre")
        passwordAgain = request.form.get("sifreTekrar")

        if email == emailAgain and password == passwordAgain:
            city = request.form.get("sehir")
            if city != 'Tüm Yerler':
                woman = request.form.get("kadin")
                man = request.form.get("erkek")
                if woman == 'on' or man == 'on':
                    if woman == 'on':
                        gender = 'F'
                    else:
                        gender = 'M'
                    interest = request.form.getlist("ilgiAlan")
                    interest = deleteSlash(interest)
                    if len(interest) != 0:
                        db = DBSession()
                        user = Users(name=name, surname=surname, birtdate=birthdate, city=city, gender=gender,
                                    password=generate_password_hash(password, method='sha256'), email=email, publicId=str(uuid.uuid4()), validation=False)
                        db.add(user)

                        try:
                            db.commit()
                            addInterest(email, interest)
                            confirmEmail(email)
                        except IntegrityError:
                            db.rollback()
                        db.close()
                        return render_template('login.html')

    return render_template('register.html', interestList=interestList)

def confirmEmail(email):
    token = urlSafeSerializer.dumps(email, salt='email-confirm')
    message = Message('Confirm Email', sender="modul.etkinlik@gmail.com", recipients=[email])
    link = url_for('confirm_email',token=token,_external=True)
    message.body = 'Your link is {}'.format(link)
    mail.send(message)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = urlSafeSerializer.loads(token,salt='email-confirm',max_age=3600)
    except SignatureExpired:
        return "<h1>Token is expired<h1>"
    db = DBSession()
    stmt = update(Users).where(Users.email == email).values(validation=True)
    db.execute(stmt)
    db.commit()
    return render_template('login.html')

def deleteSlash(interests):
    for i in range(0, len(interests)):
        interests[i] = interests[i].replace('/','')

    return interests

def addInterest(email, interests):
    db = DBSession()

    s = select([Users]).where(Users.email == email)
    result = db.execute(s)
    for row in result:
        for i in interests:
            userinterest = UserInterest(row['userId'], i)
            db.add(userinterest)
    db.commit()

@app.route('/hakkımızda', methods=['GET'])
def route_hakkımızda():
    db = DBSession()
    all_admin = db.execute("SELECT * FROM Aboutus")
    return render_template("hakkımızda.html", all_admin=all_admin)

@app.route('/iletisim', methods=['POST', 'GET'])
def route_iletisim():

    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        ipaddress = socket.gethostbyname(socket.gethostname())
        pushdate = time.strftime('%Y-%m-%d %H:%M:%S')

        save_user_message(name, email, phone, message, ipaddress, pushdate)
    return render_template("iletisim.html")

def save_user_message(name, email, phone, message, ipaddress, pushdate):
    db = DBSession()
    communication = Communication(name=name, email=email, phone=phone, message=message, ipaddress=ipaddress, pushdate=pushdate)

    db.add(communication)
    db.commit()
    db.close()





"""
Hakkımızda kısmında çalıştırılmış olan kod parçası
db = DBSession()

    x = Aboutus('Aslıhan', 'Ilgaz', '/static/img/murat.jpg', '1996 doğumlu, Yıldız Teknik Üniversitesi 3. sınıf öğrencisidir', 'https://www.facebook.com/profile.php?id=100000290109058', 'https://twitter.com/llneverdie', 'https://www.linkedin.com/in/asl%C4%B1han-ilgaz-38a909122/')
    db.add(x)

    x = Aboutus('Metin Mert', 'Akçay', '/static/img/metin.jpeg', '1996 doğumlu, Yıldız Teknik Üniversitesi 3. sınıf öğrencisidir', 'https://www.facebook.com/metinmert.akcay', '#', 'https://www.linkedin.com/in/metin-mert-ak%C3%A7ay-25120715a/')
    db.add(x)

    x = Aboutus('Murat', 'Seymen', '/static/img/murat.jpg', '1996 doğumlu, Yıldız Teknik Üniversitesi 3. sınıf öğrencisidir', 'https://www.facebook.com/murat.seymen.35', '#', 'https://www.linkedin.com/in/murat-seymen-886720159/')
    db.add(x)

    db.commit()
    db.close()
"""

"""
İlgi alanlarının oluşturulması
db = DBSession()

    interestList = ["Spor", "Bilgisayar", "Siyaset", "Yiyecek", "Yolculuk", "El Sanatları", "Sağlık", "Haberleşme", "Teknoloji", "Hayvanlar Alemi", "Bahçe", "Fotoğrafçılık", "Moda", "Müzik", "Sinema", "Kitap", "Sergi"]
    for interest in interestList:
        print(interest)
        interestName = Interest(interestName=interest)
        db.add(interestName)

    db.commit()
    db.close()
"""