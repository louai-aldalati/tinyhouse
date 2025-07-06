<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <title>Tiny House Rezervasyon ve Yönetim Sistemi</title>
</head>
<body>

  <!-- Başlık -->
  <h1 align="center">Tiny House Rezervasyon ve Yönetim Sistemi</h1>

  <!-- İçindekiler -->
  <h2>Table of Contents</h2>
  <ol>
    <li><a href="#proje-tanimi">Proje Tanımı</a></li>
    <li><a href="#projenin-amaci">Projenin Amacı</a></li>
    <li><a href="#kapsam-ve-kullanici-rolleri">Kapsam ve Kullanıcı Rolleri</a>
      <ol>
        <li><a href="#kiraci">3.1 Kiracı</a></li>
        <li><a href="#ev-sahibi">3.2 Ev Sahibi</a></li>
        <li><a href="#admin">3.3 Admin</a></li>
      </ol>
    </li>
    <li><a href="#sistem-gereksinimleri">Sistem Gereksinimleri</a></li>
    <li><a href="#teknik-gereksinimler">Teknik Gereksinimler</a></li>
    <li><a href="#veritabani-tasarimi">Veritabanı Tasarımı</a></li>
    <li><a href="#kullanici-arayuzu-tasarimlari">Kullanıcı Arayüzü Tasarımları</a></li>
    <li><a href="#kurulum-installation">Kurulum (Installation)</a></li>
    <li><a href="#kullanim-usage">Kullanım (Usage)</a></li>
    <li><a href="#katkida-bulunma-contributing">Katkıda Bulunma (Contributing)</a></li>
    <li><a href="#lisans-license">Lisans (License)</a></li>
  </ol>

  <hr>

  <!-- 1. Proje Tanımı -->
  <h2 id="proje-tanimi">Proje Tanımı</h2>
  <p>Bu proje, Tiny House konseptindeki evlerin kiralanabileceği entegre bir rezervasyon ve yönetim sistemi sunar. Kullanıcılar:</p>
  <ul>
    <li>Tiny House ilanlarını inceleyebilir,</li>
    <li>Uygun tarihleri seçerek rezervasyon yapabilir ve online ödeme gerçekleştirebilir,</li>
    <li>Konaklama sonrası yorum ve puanlama ekleyebilir.</li>
  </ul>
  <p>Ev sahipleri ise kendi ilanlarını oluşturup düzenleyebilir, rezervasyon taleplerini yönetebilir ve gelir raporları alabilir.</p>

  <hr>

  <!-- 2. Projenin Amacı -->
  <h2 id="projenin-amaci">Projenin Amacı</h2>
  <ul>
    <li>Kiracı ve ev sahipleri arasında güvenli ve kullanıcı dostu bir rezervasyon platformu oluşturmak.</li>
    <li>Evlerin müsaitlik durumunu ve fiyatlandırmayı güncel tutmak.</li>
    <li>Kullanıcı yorum ve puanlama sistemi ile deneyimi iyileştirmek.</li>
    <li>Online ödeme altyapısı ile mali süreçleri otomatikleştirmek.</li>
  </ul>

  <hr>

  <!-- 3. Kapsam ve Kullanıcı Rolleri -->
  <h2 id="kapsam-ve-kullanici-rolleri">Kapsam ve Kullanıcı Rolleri</h2>
  <p>Sistemde üç temel rol yer alır:</p>

  <h3 id="kiraci">3.1 Kiracı</h3>
  <ul>
    <li>Kayıt/giriş yapabilir.</li>
    <li>Aktif Tiny House ilanlarını listeleyip detay görüntüleyebilir.</li>
    <li>Tarih seçerek rezervasyon yapabilir ve ödeme gerçekleştirebilir.</li>
    <li>Yaptığı rezervasyonları iptal edebilir.</li>
    <li>Kiraladığı evlere yorum ve puan ekleyebilir.</li>
  </ul>

  <h3 id="ev-sahibi">3.2 Ev Sahibi</h3>
  <ul>
    <li>İlan ekleme, düzenleme, pasife alma veya silme işlemleri yapabilir.</li>
    <li>Fiyat ve uygunluk bilgilerini güncelleyebilir.</li>
    <li>Gelen rezervasyon taleplerini kabul veya reddedebilir.</li>
    <li>Kiracı yorumlarını görüntüleyebilir ve cevaplayabilir.</li>
    <li>Gelir raporları ve ödeme geçmişine erişebilir.</li>
  </ul>

  <h3 id="admin">3.3 Admin</h3>
  <ul>
    <li>Tüm kullanıcı hesaplarını yönetebilir (ekleme, düzenleme, pasif/aktif, silme).</li>
    <li>Sistem genelindeki rezervasyon ve ödemeleri izleyebilir, gerektiğinde iptal edebilir.</li>
    <li>Tiny House ilanlarını denetleyebilir ve uygun olmayan içerikleri kaldırabilir.</li>
    <li>Sistemin raporları ve istatistiklerini (kullanıcı, rezervasyon, ödeme, yorum verileri) görüntüleyebilir.</li>
  </ul>

  <hr>

  <!-- 4. Sistem Gereksinimleri -->
  <h2 id="sistem-gereksinimleri">Sistem Gereksinimleri</h2>
  <ul>
    <li><strong>Veritabanı:</strong> PostgreSQL (veya MSSQL gibi ilişkisel veritabanı)</li>
    <li><strong>Backend:</strong> Django Framework (Python 3.10+)</li>
    <li><strong>Frontend:</strong> Django Templates (HTML/CSS/JavaScript)</li>
    <li><strong>Diğer:</strong> Django REST Framework, Bootstrap 5</li>
  </ul>

  <hr>

  <!-- 5. Teknik Gereksinimler -->
  <h2 id="teknik-gereksinimler">Teknik Gereksinimler</h2>
  <ul>
    <li><strong>Stored Procedures:</strong> en az 2 adet (örneğin sp_create_reservation, sp_cancel_reservation)</li>
    <li><strong>Functions:</strong> en az 2 adet (örneğin fn_calculate_amount, fn_has_overlap)</li>
    <li><strong>Triggers:</strong> en az 2 adet (örneğin tg_before_reservation, tg_after_payment)</li>
    <li><strong>Constraint Keys:</strong>
      <ul>
        <li>Primary Key, Foreign Key</li>
        <li>Unique Constraint</li>
        <li>Check Constraint (örneğin rating BETWEEN 1 AND 5)</li>
        <li>Not Null Constraint</li>
      </ul>
    </li>
    <li><strong>Normalizasyon:</strong> 1NF, 2NF, 3NF kurallarına uyum</li>
    <li><strong>Adlandırma Standardı:</strong> Model sınıfları için CamelCase, kolon/alan isimleri için snake_case</li>
  </ul>

  <hr>

  <!-- 6. Veritabanı Tasarımı -->
  <h2 id="veritabani-tasarimi">Veritabanı Tasarımı</h2>
  <p><strong>ER Diyagramı:</strong> <a href="docs/ER-diagram.png">docs/ER-diagram.png</a></p>
  <p><strong>Tablolar:</strong></p>
  <ul>
    <li>Profile (kullanıcı profili)</li>
    <li>TinyHouse (ev bilgileri)</li>
    <li>TinyHouseImage (fotoğraflar)</li>
    <li>Reservation (rezervasyon kayıtları)</li>
    <li>Payment (ödeme detayları)</li>
    <li>Notification (bildirimler)</li>
    <li>Review (yorum ve puanlama)</li>
  </ul>
  <p><strong>SQL Scriptleri:</strong> sql/procedures/sp_create_reservation.sql, sql/functions/fn_calculate_amount.sql, vb.</p>

  <hr>

  <!-- 7. Kullanıcı Arayüzü Tasarımları -->
  <h2 id="kullanici-arayuzu-tasarimlari">Kullanıcı Arayüzü Tasarımları</h2>
  <p><strong>Admin Panel:</strong> Dashboard, kullanıcı ve rezervasyon yönetimi, ilan denetimi, mali raporlar</p>
  <p><strong>Ev Sahibi Paneli:</strong> İlan listesi ve düzenleme, rezervasyon onay/reddetme, yorum yanıtları, gelir grafikleri</p>
  <p><strong>Kiracı Paneli:</strong> Ev arama/filtreleme, rezervasyon takvimi, ödeme ekranı, geçmiş rezervasyonlar, yorum ekleme</p>
  <p><strong>Statik Dosyalar:</strong> templates/, static/css/, static/js/</p>

  <hr>

  <!-- 8. Kurulum (Installation) -->
  <h2 id="kurulum-installation">Kurulum (Installation)</h2>
  <pre><code>
# Repoyu klonlayın
git clone &lt;repository-url&gt;
cd &lt;repository-folder&gt;

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
  </code></pre>

  <hr>

  <!-- 9. Kullanım (Usage) -->
  <h2 id="kullanim-usage">Kullanım (Usage)</h2>
  <p>Tarayıcıda <a href="http://127.0.0.1:8000/">http://127.0.0.1:8000/</a> adresini açın.</p>
  <p>Admin paneli: <a href="http://127.0.0.1:8000/admin/">http://127.0.0.1:8000/admin/</a></p>
  <p>Üye kaydı yapıp farklı rollerle sisteme giriş yaparak fonksiyonları test edebilirsiniz.</p>

  <hr>

  <!-- 10. Katkıda Bulunma (Contributing) -->
  <h2 id="katkida-bulunma-contributing">Katkıda Bulunma (Contributing)</h2>
  <ol>
    <li>Fork yapın.</li>
    <li>Yeni bir branch oluşturun (<code>git checkout -b feature/xyz</code>).</li>
    <li>Değişiklikleri commit edin (<code>git commit -m "Add feature xyz"</code>).</li>
    <li>Branch'inizi push edin (<code>git push origin feature/xyz</code>).</li>
    <li>Pull request açın.</li>
  </ol>
  <p>Lütfen kod standartlarına uyun ve test eklemeyi unutmayın.</p>

  <hr>

  <!-- 11. Lisans (License) -->
  <h2 id="lisans-license">Lisans (License)</h2>
  <p>Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için <a href="LICENSE">LICENSE</a> dosyasına bakınız.</p>

</body>
</html>
