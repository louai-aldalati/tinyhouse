-- =====================================
-- Veritabanı Tablo Ayarları
-- =====================================

-- reservations_reservation tablosuna yeni satır eklendiğinde oluşturulma zamanını otomatik ayarlayalım
ALTER TABLE reservations_reservation
  ALTER COLUMN created_at SET DEFAULT now();

-- payments_payment için oluşturulma zamanını varsayılan olarak "şimdi" ayarlıyoruz
ALTER TABLE payments_payment
  ALTER COLUMN created_at SET DEFAULT now();

-- ödeme kaydı oluşturulurken durumun "beklemede" olmasını sağlayalım
ALTER TABLE payments_payment
  ALTER COLUMN payment_status SET DEFAULT 'beklemede';

-- payments_payment tablosunda her transaction_id değerinin benzersiz olmasını sağlayan UNIQUE kısıtı
ALTER TABLE payments_payment
  ADD CONSTRAINT uq_transaction_id
  UNIQUE (transaction_id);

-- bildirimler tablosunda okunma durumunu false olarak varsayılan yapalım
ALTER TABLE notifications_notification
  ALTER COLUMN is_read SET DEFAULT false;

-- bildirim oluşturulma zamanını otomatik dolduralım
ALTER TABLE notifications_notification
  ALTER COLUMN created_at SET DEFAULT now();

-- rezervasyon kaydı oluşturulduğunda başlangıçta "beklemede" durumuna gelsin
ALTER TABLE reservations_reservation
  ALTER COLUMN reservation_status SET DEFAULT 'beklemede';

-- reviews_review tablosunda rating değerinin 1 ile 5 arasında olmasını sağlayan CHECK kısıtı
ALTER TABLE reviews_review
  ADD CONSTRAINT chk_rating_range
  CHECK (rating >= 1 AND rating <= 5);


-- =====================================
-- Tutar Hesaplama Fonksiyonu
-- =====================================

-- Gün sayısıyla gece başı ücretini çarparak toplam tutarı veren fonksiyon
DROP FUNCTION IF EXISTS fn_calculate_amount(INTEGER, NUMERIC);
CREATE OR REPLACE FUNCTION fn_calculate_amount(days INTEGER, price_per_night NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
  RETURN days * price_per_night;
END;
$$ LANGUAGE plpgsql;


-- =====================================
-- Rezervasyon Çakışma Kontrolü
-- =====================================

-- Aynı ev için çakışan tarih var mı diye bakıyoruz
DROP FUNCTION IF EXISTS fn_has_overlap(BIGINT, DATE, DATE);
CREATE OR REPLACE FUNCTION fn_has_overlap(h_id BIGINT, sd DATE, ed DATE)
RETURNS BOOLEAN AS $$
DECLARE
  cnt INTEGER;
BEGIN
  SELECT COUNT(*) INTO cnt
    FROM reservations_reservation
   WHERE tiny_house_id     = h_id
     AND reservation_status <> 'iptal'
     AND start_date        < ed
     AND end_date          > sd;
  RETURN cnt > 0;
END;
$$ LANGUAGE plpgsql;


-- =====================================
-- Rezervasyon Oluşturma Prosedürü
-- =====================================

-- Ev bilgilerini alıp, ödeme ve bildirim işlemlerini otomatik yapan prosedür
DROP PROCEDURE IF EXISTS sp_create_reservation(BIGINT, INTEGER, DATE, DATE);
CREATE OR REPLACE PROCEDURE sp_create_reservation(
  p_house_id   BIGINT,
  p_tenant_id  INTEGER,
  p_start_date DATE,
  p_end_date   DATE
)
LANGUAGE plpgsql
AS $$
DECLARE
  v_days      INTEGER;
  v_amount    NUMERIC;
  v_house     RECORD;
  v_res_id    INTEGER;
BEGIN
  -- önce evin fiyat ve sahibi gibi bilgilerini çek
  SELECT price_per_night, owner_id, title
    INTO v_house
    FROM listings_tinyhouse
   WHERE id = p_house_id;

  -- ardından rezervasyon süresini ve tutarı hesapla
  v_days   := (p_end_date - p_start_date);
  v_amount := fn_calculate_amount(v_days, v_house.price_per_night);

  -- rezervasyonu kaydet ve yeni satırın id'sini al
  INSERT INTO reservations_reservation (
    tiny_house_id, tenant_id, start_date, end_date, reservation_status
  ) VALUES (
    p_house_id, p_tenant_id, p_start_date, p_end_date, 'beklemede'
  )
  RETURNING id INTO v_res_id;

  -- ödeme kaydını "beklemede" olarak ekle
  INSERT INTO payments_payment (
    reservation_id, amount
  ) VALUES (
    v_res_id, v_amount
  );

  -- ev sahibine bildirim gönder
  INSERT INTO notifications_notification (
    user_id, title, message
  ) VALUES (
    v_house.owner_id,
    'Yeni Rezervasyon',
    CONCAT(
      (SELECT username FROM auth_user WHERE id = p_tenant_id),
      ' rezervasyon yaptı: ',
      p_start_date::TEXT, ' - ', p_end_date::TEXT,
      ' tarihleri arasında "', v_house.title,
      '". Tutar: ', v_amount::TEXT, '₺.'
    )
  );
END;
$$;


-- =====================================
-- Rezervasyon İptali Prosedürü
-- =====================================

-- Verilen rezervasyon id'sini iptal durumuna çevir
DROP PROCEDURE IF EXISTS sp_cancel_reservation(INTEGER);
CREATE OR REPLACE PROCEDURE sp_cancel_reservation(p_res_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE reservations_reservation
     SET reservation_status = 'iptal'
   WHERE id = p_res_id;
END;
$$;


-- =====================================
-- Ödeme Sonrası İşlem (Trigger)
-- =====================================

-- Ödeme tablosuna ekleme veya güncelleme olunca çalışır
DROP TRIGGER IF EXISTS tg_after_payment ON payments_payment;
DROP FUNCTION IF EXISTS trg_after_payment();

CREATE OR REPLACE FUNCTION trg_after_payment()
RETURNS TRIGGER AS $$
BEGIN
  -- ödeme tamamlandığında rezervasyonu onayla
  IF NEW.payment_status = 'tamamlandi' THEN
    UPDATE reservations_reservation
       SET reservation_status = 'onayli'
     WHERE id = NEW.reservation_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_after_payment
AFTER INSERT OR UPDATE ON payments_payment
FOR EACH ROW
WHEN (NEW.payment_status = 'tamamlandi')
EXECUTE FUNCTION trg_after_payment();


-- =====================================
-- Rezervasyon Öncesi Kontrol (Trigger)
-- =====================================

-- Rezervasyon eklenmeden önce tarih çakışmasını önle
DROP TRIGGER IF EXISTS tg_before_reservation ON reservations_reservation;
DROP FUNCTION IF EXISTS trg_before_reservation();

CREATE OR REPLACE FUNCTION trg_before_reservation()
RETURNS TRIGGER AS $$
BEGIN
  IF fn_has_overlap(NEW.tiny_house_id, NEW.start_date, NEW.end_date) THEN
    RAISE EXCEPTION 'Seçilen tarihler mevcut bir rezervasyonla çakışıyor.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_before_reservation
BEFORE INSERT ON reservations_reservation
FOR EACH ROW
EXECUTE FUNCTION trg_before_reservation();
