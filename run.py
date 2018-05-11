"""Çalıştırılma işlemi bu dosya ile sağlanacaktır."""
import app.models           # Veritabanı bağlantısı için model dosyası yükleniyor.
from app import app         # Bir üst dizin olan app klasörünün içerisindeki app değişkenine erişiliyor.

app.run()                   # App.run ile uygulama çalıştırılıyor.