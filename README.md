Tiny House Rezervasyon ve Yönetim Sistemi

Table of Contents

Proje Tanımı

Projenin Amacı

Kapsam ve Kullanıcı Rolleri

3.1 Kiracı

3.2 Ev Sahibi

3.3 Admin

Sistem Gereksinimleri

Teknik Gereksinimler

Veritabanı Tasarımı

Kullanıcı Arayüzü Tasarımları

Kurulum (Installation)

Kullanım (Usage)

Katkıda Bulunma (Contributing)

Lisans (License)

Proje Tanımı

Bu proje, Tiny House konseptindeki evlerin kiralanabileceği entegre bir rezervasyon ve yönetim sistemi sunar. Kullanıcılar:

Tiny House ilanlarını inceleyebilir,

Uygun tarihleri seçerek rezervasyon yapabilir ve online ödeme gerçekleştirebilir,

Konaklama sonrası yorum ve puanlama ekleyebilir.
Ev sahipleri ise kendi ilanlarını oluşturup düzenleyebilir, rezervasyon taleplerini yönetebilir ve gelir raporları alabilir.

Projenin Amacı

Kiracı ve ev sahipleri arasında güvenli ve kullanıcı dostu bir rezervasyon platformu oluşturmak.

Evlerin müsaitlik durumunu ve fiyatlandırmayı güncel tutmak.

Kullanıcı yorum ve puanlama sistemi ile deneyimi iyileştirmek.

Online ödeme altyapısı ile mali süreçleri otomatikleştirmek.

Kapsam ve Kullanıcı Rolleri

Sistemde üç temel rol yer alır:

3.1 Kiracı

Kayıt/giriş yapabilir.

Aktif Tiny House ilanlarını listeleyip detay görüntüleyebilir.

Tarih seçerek rezervasyon yapabilir ve ödeme gerçekleştirebilir.

Yaptığı rezervasyonları iptal edebilir.

Kiraladığı evlere yorum ve puan ekleyebilir.

3.2 Ev Sahibi

İlan ekleme, düzenleme, pasife alma veya silme işlemleri yapabilir.

Fiyat ve uygunluk bilgilerini güncelleyebilir.

Gelen rezervasyon taleplerini kabul veya reddedebilir.

Kiracı yorumlarını görüntüleyebilir ve cevaplayabilir.

Gelir raporları ve ödeme geçmişine erişebilir.

3.3 Admin

Tüm kullanıcı hesaplarını yönetebilir (ekleme, düzenleme, pasif/aktif, silme).

Sistem genelindeki rezervasyon ve ödemeleri izleyebilir, gerektiğinde iptal edebilir.

Tiny House ilanlarını denetleyebilir ve uygun olmayan içerikleri kaldırabilir.

Sistemin raporları ve istatistiklerini (kullanıcı, rezervasyon, ödeme, yorum verileri) görüntüleyebilir.

Sistem Gereksinimleri

Veritabanı: PostgreSQL (veya MSSQL gibi ilişkisel veritabanı)

Backend: Django Framework (Python 3.10+)

Frontend: Django Templates (HTML/CSS/JavaScript)

Diğer: Django REST Framework, Bootstrap 5

Teknik Gereksinimler

Stored Procedures (en az 2 adet, örneğin sp_create_reservation, sp_cancel_reservation)

Functions (en az 2 adet, örneğin fn_calculate_amount, fn_has_overlap)

Triggers (en az 2 adet, örneğin tg_before_reservation, tg_after_payment)

Constraint Keys:

Primary Key, Foreign Key

Unique Constraint

Check Constraint (örneğin rating BETWEEN 1 AND 5)

Not Null Constraint

Normalizasyon: 1NF, 2NF, 3NF kurallarına uyum

Adlandırma Standardı: Model sınıfları için CamelCase, kolon/alan isimleri için snake_case

Veritabanı Tasarımı

ER Diyagramı: docs/ER-diagram.png

Tablolar:

Profile (kullanıcı profili)

TinyHouse (ev bilgileri)

TinyHouseImage (fotoğraflar)

Reservation (rezervasyon kayıtları)

Payment (ödeme detayları)

Notification (bildirimler)

Review (yorum ve puanlama)

SQL Scriptleri: sql/procedures/sp_create_reservation.sql, sql/functions/fn_calculate_amount.sql, vb.

Kullanıcı Arayüzü Tasarımları

Admin Panel: Dashboard, kullanıcı ve rezervasyon yönetimi, ilan denetimi, mali raporlar

Ev Sahibi Paneli: İlan listesi ve düzenleme, rezervasyon onay/reddetme, yorum yanıtları, gelir grafikleri

Kiracı Paneli: Ev arama/filtreleme, rezervasyon takvimi, ödeme ekranı, geçmiş rezervasyonlar, yorum ekleme

Statik Dosyalar: templates/, static/css/, static/js/

Kurulum (Installation)

# Repoyu klonlayın
git clone <repository-url>
cd <repository-folder>

# Sanal ortam oluşturun ve aktive edin
python3 -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows

# Gereksinimleri yükleyin
pip install -r requirements.txt

# Ortam değişkenlerini yapılandırın (.env)
cp .env.example .env
# .env içinde DATABASE_URL, SECRET_KEY vb. tanımlayın

# Veritabanı migrasyonlarını çalıştırın
python manage.py migrate

# Yönetici kullanıcısı oluşturun
python manage.py createsuperuser

# Sunucuyu başlatın
python manage.py runserver

Kullanım (Usage)

Tarayıcıda http://127.0.0.1:8000/ adresini açın.

Admin paneli: http://127.0.0.1:8000/admin/

Üye kaydı yapıp farklı rollerle sisteme giriş yaparak fonksiyonları test edebilirsiniz.

Katkıda Bulunma (Contributing)

Fork yapın.

Yeni bir branch oluşturun (git checkout -b feature/xyz).

Değişiklikleri commit edin (git commit -m "Add feature xyz").

Branch'inizi push edin (git push origin feature/xyz).

Pull request açın.

Lütfen kod standartlarına uyun ve test eklemeyi unutmayın.

Lisans (License)

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için LICENSE dosyasına bakınız.

