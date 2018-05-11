"""Asıl işlemlerin gerçekleştirildiği yerdir. App adında bir değişken oluşturulması gereklidir. Gerekli configurasyonlar
config dosyası iöçerisinden erişilerek gerçekleştirilecektir.
/ adlı dizinde bizim etkinlik sayfamıza ait olan html koyulacaktır. Şuanda geçici olarak html sayfası oluturulmuştur.
/login login.html sayfasının açılması sağlanır.Kullanıcının sisteme giriş yapması için oluşturulmuştur.
/index ile veritabanına kişi ekleme işlemi gerçekleştirilir. (Bu işlem doğru şekilde gerçekleşip gerçekleşmediğinin kontrolü için kullanılmıştır)
/iletisim Kullanıcının şikayet etmesi durumu için oluşturulmuş sayfadır. Bu sayfada kullanıcının koymuş olduğu ip adresi ve koyma saati gibi
bilgiler saklanacaktır. Anlaşılmayan yer olursa iletişim için metinmakcay@gmail.com adresine mail atabilirsiniz. :))
/ """
from flask import Flask, render_template, request, flash, redirect, url_for, session, abort
from .models import DBSession, Users, Communication, Aboutus, Interest, UserInterest
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from sqlalchemy.sql import select, update
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from config import SECRET_KEY
import socket
import time
import uuid

app = Flask(__name__)
app.config.from_object('config')
mail = Mail(app)
urlSafeSerializer = URLSafeTimedSerializer(SECRET_KEY)

@app.route('/index')
def index():
    if 'email' in session:
        return render_template("index.html")
    else:
        abort(404)

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
                        session['email'] = row['email']
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
def register():
    db = DBSession()
    interestList = db.execute("SELECT * FROM Interest")
    db.close()

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

                    gender = findGender(woman)
                    interest = request.form.getlist("ilgiAlan")
                    interest = deleteSlash(interest)
                    if len(interest) != 0:

                        db = DBSession()
                        user = Users(name=name, surname=surname, birtdate=birthdate, city=city, gender=gender,password=generate_password_hash(password,
                                        method='sha256'), email=email, publicId=str(uuid.uuid4()), validation=False)
                        db.add(user)

                        try:
                            db.commit()
                            addInterestUserTable(email, interest)
                            confirmEmail(email)
                        except IntegrityError:
                            db.rollback()
                        db.close()

                        return render_template('login.html')

    return render_template('register.html', interestList=interestList)

def findGender(woman):
    if woman == 'on':
        return 'F'
    else:
        return 'M'

def deleteSlash(interests):
    size = len(interests)
    for i in range(0, size):
        interests[i] = interests[i].replace('/','')

    return interests

def addInterestUserTable(email, interests):
    db = DBSession()
    s = select([Users]).where(Users.email == email)
    result = db.execute(s)

    for row in result:
        for interest in interests:
            userInterest = UserInterest(row['userId'], interest)
            db.add(userInterest)
    db.commit()

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

@app.route('/hakkımızda', methods=['GET'])
def hakkımızda():
    db = DBSession()
    all_admin = db.execute("SELECT * FROM Aboutus")
    db.close()

    return render_template("hakkımızda.html", all_admin=all_admin)

@app.route('/iletisim', methods=['POST', 'GET'])
def iletisim():

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