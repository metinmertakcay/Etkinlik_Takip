"""Asıl işlemlerin gerçekleştirildiği yerdir. App adında bir değişken oluşturulması gereklidir. Gerekli configurasyonlar
config dosyası iöçerisinden erişilerek gerçekleştirilecektir.
/ adlı dizinde bizim etkinlik sayfamıza ait olan html koyulacaktır. Şuanda geçici olarak html sayfası oluturulmuştur.
/login login.html sayfasının açılması sağlanır.Kullanıcının sisteme giriş yapması için oluşturulmuştur.
/index ile veritabanına kişi ekleme işlemi gerçekleştirilir. (Bu işlem doğru şekilde gerçekleşip gerçekleşmediğinin kontrolü için kullanılmıştır)
/iletisim Kullanıcının şikayet etmesi durumu için oluşturulmuş sayfadır. Bu sayfada kullanıcının koymuş olduğu ip adresi ve koyma saati gibi
bilgiler saklanacaktır. Anlaşılmayan yer olursa iletişim için metinmakcay@gmail.com adresine mail atabilirsiniz. :))
/ """
import os
from flask import Flask, render_template, request, flash, redirect, url_for, session, abort
from .models import DBSession, Users, Communication, Aboutus, Interest, UserInterest, Yorum,Sikayet
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from sqlalchemy.sql import select, update, insert
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
    slider = db.execute('SELECT * FROM etkinlik e,etkinlik_resim er, "etkinlikResim" r WHERE tarih > CURRENT_TIMESTAMP AND e.e_id=er.e_id AND er.resim_id=r.etk_resim_id AND "banlanmısMı" = 0 order by "yıldızPuanToplamı" DESC, "yıldızVerenSayısı" DESC limit 3')
    if request.method == 'POST':
        kategori = request.form.get("inputGroupSelect01")
        tarih2 = request.form.get("inputGroupSelect02")
        yer = request.form.get("inputGroupSelect03")
        db = DBSession()
        items2 = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE ' + kategori + ' özellik_id=9  and tarih>=current_date  AND etkinlik.e_id = etkinlik_özellik.e_id AND "banlanmısMı"=0 AND etkinlik.e_id = etkinlik_resim.e_id AND ' + yer + ' etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id ' + tarih2 + ' order by etkinlik.e_id asc')
        list = []
        for i in items2:
            list.append(i)
        return render_template("search_liste_görüntüleme.html", items2=list)
    else:
        return render_template('home.html', items=items, items2=items2, tarih=tarih, itemler=zip(tarih, items), slider=slider)

@app.route('/home',methods=['POST','GET'])
def sample_proute():

    if session.get('userid') is None:
        return redirect("/")
    db = DBSession()
    items = db.execute('SELECT * FROM etkinlik,etkinlik_özellik,"etkinlikTipi" where özellik_id=9 and etkinlik.e_id=etkinlik_özellik.e_id and etkinlik."etklinlikTipi"="etkinlikTipi".tip_id order by "yıldızPuanToplamı" DESC, etkinlik.e_id asc limit 5')
    tarih = db.execute('SELECT * FROM etkinlik,etkinlik_özellik,"etkinlikTipi" where özellik_id=1 and etkinlik.e_id=etkinlik_özellik.e_id and etkinlik."etklinlikTipi"="etkinlikTipi".tip_id order by "yıldızPuanToplamı" DESC, etkinlik.e_id asc limit 5')
    items2 = db.execute('SELECT * FROM etkinlik order by "yıldızPuanToplamı" DESC limit 5')
    userid = request.form.get("userid")
    slider = db.execute('SELECT * FROM etkinlik e,etkinlik_resim er, "etkinlikResim" r WHERE tarih > CURRENT_TIMESTAMP AND e.e_id=er.e_id AND er.resim_id=r.etk_resim_id AND "banlanmısMı" = 0 order by "yıldızPuanToplamı" DESC, "yıldızVerenSayısı" DESC limit 3')

    if request.method == 'POST':
        kategori = request.form.get("inputGroupSelect01")
        tarih2 = request.form.get("inputGroupSelect02")
        yer = request.form.get("inputGroupSelect03")
        db = DBSession()
        items2 = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE ' + kategori  + ' özellik_id=9 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND ' +yer + ' etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id ' + tarih2 + ' order by etkinlik.e_id asc')
        return render_template("profil_search_liste_görüntüleme.html", items2=items2 ,userid=userid)
    else:
        return render_template('profil_home.html', items=items , items2 = items2,tarih=tarih,itemler=zip(tarih,items),email=session['email'], id=session.get('userid'), slider=slider)

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
def forget(token, error=None):
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
            error = "Şifreniz başarıyla değiştirilmiştir."
            return render_template('login.html', error=error)
        else:
            error = "Uyuşmayan şifre!!!"

    return render_template('forget.html', token=token, error=error)

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
                        session['userid'] = row['userid']
                        session['email'] = row['email']
                        return redirect("/home")
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
        image = request.form.get("image")

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
                                        method='sha256'), email=email, publicid=str(uuid.uuid4()), validation=False,image=image)
                        db.add(user)

                        try:
                            db.commit()
                            addInterestUserTable(email, interest)
                            confirmEmail(email)
                            error = "Email onayı için mail yollanmıştır"
                        except IntegrityError:
                            db.rollback()
                            error = None
                        db.close()

                        return render_template('login.html', error=error)

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
        id = row[0]
        for i in range(0, len(interests)):
            data = UserInterest(id, interests[i])
            db.add(data)
    db.commit()
    db.close()

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
    print('Hata1')
    stmt = update(Users).where(Users.email == email).values(validation=True)
    db.execute(stmt)
    db.commit()
    db.close()
    return redirect('/Login')


@app.route('/hakkımızda', methods=['GET'])
def hakkımızda():
    db = DBSession()
    all_admin = db.execute("SELECT * FROM Aboutus")
    db.close()

    return render_template("hakkımızda.html", all_admin=all_admin)

@app.route('/phakkımızda', methods=['GET'])
def phakkımızda():
    db = DBSession()
    all_admin = db.execute("SELECT * FROM Aboutus")
    db.close()

    return render_template("profil_hakkımızda.html", all_admin=all_admin, id=session.get('userid'))

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

@app.route('/piletisim', methods=['POST', 'GET'])
def piletisim():

    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        ipaddress = socket.gethostbyname(socket.gethostname())
        pushdate = time.strftime('%Y-%m-%d %H:%M:%S')

        save_user_message(name, email, phone, message, ipaddress, pushdate)

    return render_template("profil_iletisim.html", id=session.get('userid'))

def save_user_message(name, email, phone, message, ipaddress, pushdate):
    db = DBSession()
    communication = Communication(name=name, email=email, phone=phone, message=message, ipaddress=ipaddress, pushdate=pushdate)
    db.add(communication)
    db.commit()
    db.close()

@app.route('/sikayet', methods=['GET'])
def route_sikayet():
    if session.get('userid') is not 4:
        return "Sadece Admin Giriş Yapabilir"
    db = DBSession()
    items = db.execute('SELECT * FROM sikayet, users, etkinlik, "etkinlikTipi" where sikayet.k_id=users.userid and etkinlik.e_id = sikayet.e_id and "etkinlikTipi".tip_id=etkinlik."etklinlikTipi"')
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

@app.route('/ysil/<int:id>/<int:etk>', methods=['GET'])
def route_yorumsil(id,etk):
    if session.get('userid') is not 4:
        return "Sadece Admin Giriş Yapabilir"
    db = DBSession()
    db.execute('Delete from yorum where yorum_id=' + str(id) + ';')
    db.commit()
    db.close()

    return  redirect("/petkinlik/" + str(etk))

@app.route('/cikar/<int:id>/<int:skt>', methods=['GET'])
def route_cikar(id,skt):
    if session.get('userid') is not 4:
        return "Sadece Admin Giriş Yapabilir"
    db = DBSession()
    db.execute('update etkinlik set "banlanmısMı"=1 where e_id=' + str(id) + ';');
    db.commit()
    db.close()
    db = DBSession()
    db.execute('UPDATE sikayet SET deger = 1 WHERE sikayet_id=' + str(skt) + ';')
    db.commit()
    db.close()

    return  redirect("/banli/"+str(id));

@app.route('/banli/<int:id>', methods=['GET'])
def route_banli(id):
    return  render_template("banli.html",id=id);

@app.route('/pbanli/<int:id>', methods=['GET'])
def route_pbanli(id):
    if session.get('userid') is None:
        return redirect("/banli/"+ str(id))
    return  render_template("pbanli.html",email=session['email'],id=id);

@app.route('/ara', methods=['POST','GET'])
def route_ara():
    if session.get('userid') is None:
        return redirect("/")

    if request.form.get('button2', None) == "ara":
            aranan = request.form.get("name")
            db = DBSession()
            items = db.execute("select * from users where name ilike '%"+ aranan +"%'" + " or surname ilike '%" + aranan + "%'"  + " or city ilike '%" + aranan + "%'" + " or email ilike '%" + aranan + "%'")
            db.commit()
            db.close()
            return render_template("kisiler.html",items=items,email = session['email']);
    return  render_template("profilara.html");

@app.route('/etara', methods=['POST','GET'])
def route_etara():

    if request.form.get('button2', None) == "ara":
            aranan = request.form.get("name")
            etkinlikAdı = ' "etkinlikAdı" '
            etkinlikAciklamasi = ' "etkinlikAcıklaması" '
            db = DBSession()
            items = db.execute("select * from etkinlik where" + etkinlikAdı + " ilike '%"+ aranan +"%'" + " or " + etkinlikAciklamasi + "ilike '%" + aranan + "%'")
            db.commit()
            db.close()
            return render_template("etkinlikler.html",items=items);
    return  render_template("etara.html");

@app.route('/petara', methods=['POST','GET'])
def route_petara():
    if session.get('userid') is None:
        return redirect("/etara")

    if request.form.get('button2', None) == "ara":
            aranan = request.form.get("name")
            etkinlikAdı = ' "etkinlikAdı" '
            etkinlikAciklamasi = ' "etkinlikAcıklaması" '
            db = DBSession()
            items = db.execute("select * from etkinlik where" + etkinlikAdı + " ilike '%"+ aranan +"%'" + " or " + etkinlikAciklamasi + "ilike '%" + aranan + "%'")
            db.commit()
            db.close()
            return render_template("profil_etkinlikler.html",items=items);
    return  render_template("profil_etara.html");

@app.route('/bankaldir/<int:id>', methods=['GET'])
def route_bankaldir(id):
    if session.get('userid') is not 4:
        return "Sadece Admin Giriş Yapabilir"
    db = DBSession()
    db.execute('update etkinlik set "banlanmısMı"=0 where e_id=' + str(id) + ';');
    db.commit()
    db.close()
    return redirect("/petkinlik/" + str(id));


@app.route('/sikayet/<int:deger>', methods=['GET'])
def route_sikayet1(deger):
    if session.get('userid') is not 4:
        return "Sadece Admin Giriş Yapabilir"
    db = DBSession()

    if(deger == 2):
        items = db.execute('SELECT * FROM sikayet, users, etkinlik, "etkinlikTipi" where sikayet.k_id=users.userid and etkinlik.e_id = sikayet.e_id and "etkinlikTipi".tip_id=etkinlik."etklinlikTipi" and deger=' + str(deger) + 'and "sikayetTarihi">current_date-3');
        print("Murat")
    else:
        items = db.execute('select * from sikayet, users, etkinlik, "etkinlikTipi" where sikayet.k_id=users.userid and etkinlik.e_id = sikayet.e_id and "etkinlikTipi".tip_id=etkinlik."etklinlikTipi" and deger=' + str(deger) + '')
        print("Murat2")
    db.close()

    return render_template("admin_bildirim.html", items=items)

@app.route('/liste/<int:id>', methods=['GET'])
def route_liste(id):
    db = DBSession()

    items = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE "etklinlikTipi" = ' + str(id) + ' AND özellik_id=9 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.tarih >= current_date  AND etkinlik.e_id = etkinlik_resim.e_id  AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    tarih = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE "etklinlikTipi" = ' + str(id) + ' AND özellik_id=1 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.tarih >= current_date  AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    db.close()

    return render_template("liste_görüntüleme.html", items=items,tarih=tarih,items2=zip(tarih,items))

@app.route('/pliste/<int:id>', methods=['GET'])
def route_pliste(id):
    if session.get('userid') is None:
        return redirect("/liste/" + str(id))
    db = DBSession()
    items = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE "etklinlikTipi" = ' + str(id) + ' AND özellik_id=9 AND etkinlik.e_id = etkinlik_özellik.e_id  and tarih>=current_date  AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    tarih = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE "etklinlikTipi" = ' + str(id) + ' AND özellik_id=1 AND etkinlik.e_id = etkinlik_özellik.e_id  AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    db.close()

    return render_template("profil_liste_görüntüleme.html", items=items,tarih=tarih,items2=zip(tarih,items),email=session['email'],id=session.get('userid'))

@app.route('/liste', methods=['GET'])
def route_list():
    env = jinja2.Environment()
    env.globals.update(zip=zip)
    db = DBSession()
    items = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE özellik_id=9  and tarih>=current_date  AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    tarih = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE özellik_id=1 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')

    return render_template("liste_görüntüleme.html", items=items,tarih=tarih,items2=zip(tarih,items))

@app.route('/pliste', methods=['GET'])
def route_plist():
    if session.get('userid') is None:
        return redirect("/liste")
    env = jinja2.Environment()
    env.globals.update(zip=zip)
    db = DBSession()
    items = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE özellik_id=9  and tarih>=current_date  AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')
    tarih = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE özellik_id=1 AND etkinlik.e_id = etkinlik_özellik.e_id AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id order by etkinlik.e_id asc')

    return render_template("profil_liste_görüntüleme.html", items=items,tarih=tarih,items2=zip(tarih,items),email=session['email'],id=session.get('userid'))

@app.route('/etkinlik/<int:id>', methods=['GET'])
def route_etkinlik(id):
    db = DBSession()
    items = db.execute('SELECT * FROM etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    tarih = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=1 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    yer = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=7 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    sehir = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=9 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    ucret = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=3 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    harita = db.execute('SELECT * FROM etkinlik_özellik,etkinlik,etkinlik_resim,"etkinlikResim" WHERE etkinlik.e_id = ' + str(id) + ' AND etkinlik.e_id=etkinlik_özellik.e_id AND özellik_id=10 AND etkinlik.e_id = etkinlik_resim.e_id AND etkinlik_resim.resim_id = "etkinlikResim".etk_resim_id')
    yorum = db.execute('SELECT * FROM yorum,etkinlik,users WHERE yorum.e_id=etkinlik.e_id and etkinlik.e_id= ' + str(id) + ' AND users.userid = yorum.k_id')
    db.close()

    return render_template("etkinlikDuvarı.html",items = items,tarih=tarih,yer = yer , sehir = sehir , ucret = ucret,harita =harita,yorum=yorum)



APP_ROOT = os.path.dirname(os.path.abspath(__file__))
@app.route('/profil/<int:id>', methods=['GET', 'POST'])
def route_profil(id):
    db = DBSession()
    users = db.execute('SELECT * FROM users WHERE users.userid = ' + str(id))
    ilgiAlanlari = db.execute('SELECT * FROM userinterest,interest WHERE userinterest.userid = ' + str(id) + ' AND userinterest.interestid=interest.id')
    yorumlar = db.execute('SELECT * FROM yorum,etkinlik,users WHERE yorum.k_id= ' + str(id) + 'AND etkinlik.e_id=yorum.e_id AND users.userid='+ str(id)+'order by yorum."yorumTarihi"')

    if session.get('userid') is None:
        return render_template("profile_without_login.html",users=users, ilgiAlanlari=ilgiAlanlari, yorumlar=yorumlar)

    if ( session.get('userid') != id):
        print(session.get('userid'))
        return  render_template("othersProfile.html", users=users, ilgiAlanlari=ilgiAlanlari, yorumlar=yorumlar, id=session.get('userid'))
    else:
        target = os.path.join(APP_ROOT, "static/images/")
        if not os.path.isdir(target):
            os.mkdir(target)

        for file in request.files.getlist("image"):
            filename = file.filename
            destination = "/".join([target, filename])
            file.save(destination)


            #xx = users.query.filter(users.userid == str(id)).first()
            #imageValue = admin.image
            #imageValue["image"] = str(filename)
            #xx.image
            #db.session.commit()
            #db.close


            db.execute('UPDATE users SET image = \''+filename+'\' WHERE users.userid = '+str(id))
            db.commit()
            users = db.execute('SELECT * FROM users WHERE users.userid = ' + str(id))
            db.close
        return render_template("profile.html", users=users, ilgiAlanlari=ilgiAlanlari, yorumlar=yorumlar, id=session.get('userid'))



@app.route('/petkinlik/<int:id>', methods=['POST','GET'])
def route_petkinlik(id):
    if session.get('userid') is None:
        return redirect("/etkinlik/"+ str(id))

    if request.form.get('button', None) == "yorum":
            k_id = session['userid']
            yorum = request.form.get("yorum")
            pushdate = time.strftime('%Y-%m-%d %H:%M:%S')
            save_yorum(k_id, id, yorum, pushdate)

    if request.form.get('button2', None) == "sikayet":
            eden_k_id = session['userid']
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
    yorum = db.execute('SELECT * FROM yorum,etkinlik,users WHERE yorum.e_id=etkinlik.e_id and etkinlik.e_id= ' + str(id) + ' AND users.userid = yorum.k_id order by yorum."yorumTarihi"')
    db.close()

    return render_template("profil_etkinlikDuvarı.html",items = items,tarih=tarih,yer = yer , sehir = sehir , ucret = ucret,harita =harita,yorum=yorum,email=session['email'],id=session.get('userid'))

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