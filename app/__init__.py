"""Asıl işlemlerin gerçekleştirildiği yerdir. App adında bir değişken oluşturulması gereklidir. Gerekli configurasyonlar
config dosyası iöçerisinden erişilerek gerçekleştirilecektir.
/ adlı dizinde bizim etkinlik sayfamıza ait olan html koyulacaktır. Şuanda geçici olarak html sayfası oluturulmuştur.
/login login.html sayfasının açılması sağlanır.Kullanıcının sisteme giriş yapması için oluşturulmuştur.
/index ile veritabanına kişi ekleme işlemi gerçekleştirilir. (Bu işlem doğru şekilde gerçekleşip gerçekleşmediğinin kontrolü için kullanılmıştır)
/iletisim Kullanıcının şikayet etmesi durumu için oluşturulmuş sayfadır. Bu sayfada kullanıcının koymuş olduğu ip adresi ve koyma saati gibi
bilgiler saklanacaktır. Anlaşılmayan yer olursa iletişim için metinmakcay@gmail.com adresine mail atabilirsiniz. :))
/ """
from flask import Flask, render_template, request, flash, redirect, url_for, session, abort
from .models import DBSession, Users, Communication, Aboutus, Interest, UserInterest, Yorum,Sikayet
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from sqlalchemy.sql import select, update
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from config import SECRET_KEY
# noinspection PyUnresolvedReferences
import psycopg2
import jinja2
import socket
import time
import uuid

app = Flask(__name__)
app.config.from_object('config')
mail = Mail(app)
urlSafeSerializer = URLSafeTimedSerializer(SECRET_KEY)

@app.route('/',methods=['POST','GET'])
def sample_route():
    db = DBSession()
    items = db.execute(
        'SELECT * FROM etkinlik, etkinlik_özellik, "etkinlikTipi" where özellik_id=9 and etkinlik.e_id=etkinlik_özellik.e_id and etkinlik."etklinlikTipi"="etkinlikTipi".tip_id order by "yıldızPuanToplamı" DESC, etkinlik.e_id asc limit 5')
    tarih = db.execute(
        'SELECT * FROM etkinlik, etkinlik_özellik, "etkinlikTipi" where özellik_id=1 and etkinlik.e_id=etkinlik_özellik.e_id and etkinlik."etklinlikTipi"="etkinlikTipi".tip_id order by "yıldızPuanToplamı" DESC, etkinlik.e_id asc limit 5')
    items2 = db.execute('SELECT * FROM etkinlik order by "yıldızPuanToplamı" DESC limit 5')
    if request.method == 'POST':
        kategori = request.form.get("inputGroupSelect01")
        tarih2 = request.form.get("inputGroupSelect02")
        yer = request.form.get("inputGroupSelect03")
        db = DBSession()
        items2 = db.execute(
            'SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE ' + kategori + ' özellik_id=9 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND ' + yer + ' etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id ' + tarih2 + ' order by etkinlik.e_id asc')
        return render_template("search_liste_görüntüleme.html", items2=items2)
    else:
        return render_template('home.html', items=items, items2=items2, tarih=tarih, itemler=zip(tarih, items))

@app.route('/home',methods=['POST','GET'])
def sample_proute():
    db = DBSession()
    items = db.execute('SELECT * FROM etkinlik,etkinlik_özellik,"etkinlikTipi" where özellik_id=9 and etkinlik.e_id=etkinlik_özellik.e_id and etkinlik."etklinlikTipi"="etkinlikTipi".tip_id order by "yıldızPuanToplamı" DESC, etkinlik.e_id asc limit 5')
    tarih = db.execute('SELECT * FROM etkinlik,etkinlik_özellik,"etkinlikTipi" where özellik_id=1 and etkinlik.e_id=etkinlik_özellik.e_id and etkinlik."etklinlikTipi"="etkinlikTipi".tip_id order by "yıldızPuanToplamı" DESC, etkinlik.e_id asc limit 5')
    items2 = db.execute('SELECT * FROM etkinlik order by "yıldızPuanToplamı" DESC limit 5')
    if request.method == 'POST':
        kategori = request.form.get("inputGroupSelect01")
        tarih2 = request.form.get("inputGroupSelect02")
        yer = request.form.get("inputGroupSelect03")
        db = DBSession()
        items2 = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE ' + kategori  + ' özellik_id=9 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND ' +yer + ' etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id ' + tarih2 + ' order by etkinlik.e_id asc')
        return render_template("profil_search_liste_görüntüleme.html", items2=items2)
    else:
        return render_template('profil_home.html', items=items , items2 = items2,tarih=tarih,itemler=zip(tarih,items))


@app.route('/send_email',methods=['POST','GET'])
def send_email(error=None):
    if request.method == 'POST':
        email = request.form.get('email')

        db = DBSession()
        s = select([Users]).where(Users.email == email)
        result = db.execute(s)
        db.close()

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
            abort(404)

        password = request.form.get('password')
        passwordAgain = request.form.get('passwordAgain')

        db = DBSession()
        if password == passwordAgain:
            stmt = update(Users).where(Users.email == email).values(password=generate_password_hash(password))
            db.execute(stmt)
            db.commit()
            db.close()

            return redirect(url_for('login'))

    return render_template('forget.html', token=token)

@app.route('/Login', methods=['GET','POST'])
def login(error=None):

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = DBSession()
        s = select([Users]).where(Users.email == email)
        result = db.execute(s)
        db.close()

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


@app.route('/sikayet', methods=['GET'])
def route_sikayet():
    db = DBSession()
    items = db.execute('SELECT * FROM sikayet, users, etkinlik, "etkinlikTipi" where sikayet.k_id=users."userId" and etkinlik.e_id = sikayet.e_id and "etkinlikTipi".tip_id=etkinlik."etklinlikTipi"')
    db.close()

    return render_template("admin_bildirim.html", items=items)

@app.route('/cozum2/<int:id>', methods=['GET'])
def route_cozum2(id):
    db = DBSession()
    db.execute('UPDATE sikayet SET deger = 2 WHERE sikayet_id=' + str(id) + ';')
    db.commit()
    db.close()

    return  redirect("/sikayet/0")

@app.route('/cozum1/<int:id>', methods=['GET'])
def route_cozum1(id):

    db = DBSession()
    db.execute('UPDATE sikayet SET deger = 1 WHERE sikayet_id=' + str(id) + ';')
    db.commit()
    db.close()

    return  redirect("/sikayet/0")

@app.route('/sikayet/<int:deger>', methods=['GET'])
def route_sikayet1(deger):
    db = DBSession()

    if(id == 2):
        items = db.execute('SELECT * FROM sikayet, users, etkinlik, "etkinlikTipi" where sikayet.k_id=users."userId" and etkinlik.e_id = sikayet.e_id and "etkinlikTipi".tip_id=etkinlik."etklinlikTipi" and deger=' + str(deger) + 'and "sikayetTarihi"<current_date +3');
    else:
        items = db.execute('select * from sikayet, users, etkinlik, "etkinlikTipi" where sikayet.k_id=users."userId" and etkinlik.e_id = sikayet.e_id and "etkinlikTipi".tip_id=etkinlik."etklinlikTipi" and deger=' + str(deger) + '')
    db.close()

    return render_template("admin_bildirim.html", items=items)

@app.route('/liste/<int:id>', methods=['GET'])
def route_liste(id):
    db = DBSession()

    items = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE "etklinlikTipi" = ' + str(id) + ' AND özellik_id=9 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    tarih = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE "etklinlikTipi" = ' + str(id) + ' AND özellik_id=1 AND etkinlik.e_id = etkinlik_özellik.e_id  AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    db.close()

    return render_template("liste_görüntüleme.html", items=items,tarih=tarih,items2=zip(tarih,items))

@app.route('/pliste/<int:id>', methods=['GET'])
def route_pliste(id):
    db = DBSession()

    items = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE "etklinlikTipi" = ' + str(id) + ' AND özellik_id=9 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    tarih = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE "etklinlikTipi" = ' + str(id) + ' AND özellik_id=1 AND etkinlik.e_id = etkinlik_özellik.e_id  AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    db.close()

    return render_template("profil_liste_görüntüleme.html", items=items,tarih=tarih,items2=zip(tarih,items))

@app.route('/liste', methods=['GET'])
def route_list():
    env = jinja2.Environment()
    env.globals.update(zip=zip)
    db = DBSession()
    items = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE özellik_id=9 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    tarih = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE özellik_id=1 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')

    return render_template("liste_görüntüleme.html", items=items,tarih=tarih,items2=zip(tarih,items))

@app.route('/pliste', methods=['GET'])
def route_plist():
    env = jinja2.Environment()
    env.globals.update(zip=zip)
    db = DBSession()
    items = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE özellik_id=9 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    tarih = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE özellik_id=1 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')

    return render_template("profil_liste_görüntüleme.html", items=items,tarih=tarih,items2=zip(tarih,items))

@app.route('/etkinlik/<int:id>', methods=['GET'])
def route_etkinlik(id):
    db = DBSession()
    items = db.execute('SELECT * FROM etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    tarih = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=1 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    yer = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=7 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    sehir = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=9 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    ucret = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=3 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    harita = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=10 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    yorum = db.execute('SELECT * FROM yorum,etkinlik,users WHERE yorum.e_id=etkinlik.e_id and etkinlik.e_id= ' + str(id) + ' AND users."userId" = yorum.k_id')
    db.close()

    return render_template("etkinlikDuvarı.html",items = items,tarih=tarih,yer = yer , sehir = sehir , ucret = ucret,harita =harita,yorum=yorum)

@app.route('/petkinlik/<int:id>', methods=['POST','GET'])
def route_petkinlik(id):
    if request.form.get('button', None) == "yorum":
            k_id = request.form.get("k_id")
            yorum = request.form.get("yorum")
            pushdate = time.strftime('%Y-%m-%d %H:%M:%S')
            save_yorum(k_id, id, yorum, pushdate)

    if request.form.get('button2', None) == "sikayet":
            eden_k_id = request.form.get("eden_k_id")
            sikayet_k_id = request.form.get("sikayet_k_id")
            etkinlik_e_id = request.form.get("etkinlik_e_id")
            metin = request.form.get("metin")
            pushdate = time.strftime('%Y-%m-%d %H:%M:%S')
            save_sikayet(eden_k_id, sikayet_k_id, etkinlik_e_id, metin, pushdate)

    db = DBSession()
    items = db.execute('SELECT * FROM etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    tarih = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=1 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    yer = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=7 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    sehir = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=9 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    ucret = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=3 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    harita = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=10 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    yorum = db.execute('SELECT * FROM yorum,etkinlik,users WHERE yorum.e_id=etkinlik.e_id and etkinlik.e_id= ' + str(id) + ' AND users."userId"= yorum.k_id')
    db.close()

    return render_template("profil_etkinlikDuvarı.html",items = items,tarih=tarih,yer = yer , sehir = sehir , ucret = ucret,harita =harita,yorum=yorum)

def save_yorum(k_id, e_id, message ,pushdate):
    db = DBSession()
    yorum = Yorum(k_id=k_id, e_id=e_id, yorumMetni=message, yorumTarihi=pushdate)
    db.add(yorum)
    db.commit()
    db.close()

def save_sikayet(eden_k_id, sikayet_k_id, etkinlik_e_id, metin, pushdate):
    db = DBSession()
    sikayet = Sikayet(sikayet_eden_id=eden_k_id, k_id=sikayet_k_id, e_id=etkinlik_e_id, sikayetMetni=metin, sikayetTarihi=pushdate,deger=0)
    db.add(sikayet)
    db.commit()
    db.close()