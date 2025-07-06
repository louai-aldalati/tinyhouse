from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0013_auto_20250613_1216'),
    ]

    operations = [
        # 1) ضبط DEFAULT للحقل reservation_status على مستوى الجدول
        migrations.AlterField(
            model_name='reservation',
            name='reservation_status',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('beklemede', 'beklemede'),
                    ('onayli',   'onayli'),
                    ('iptal',    'iptal'),
                ],
                default='beklemede',
            ),
        ),

        # 2) إعادة إنشاء الدوال والإجراءات والـ triggers الصحيحة:
        migrations.RunSQL(
            sql="""\
-- إسقاط النسخ القديمة أولاً
DROP TRIGGER IF EXISTS tg_before_reservation ON reservations_reservation;
DROP FUNCTION IF EXISTS trg_before_reservation();

DROP TRIGGER IF EXISTS tg_after_payment ON payments_payment;
DROP FUNCTION IF EXISTS trg_after_payment();

DROP PROCEDURE IF EXISTS sp_create_reservation(BIGINT, INTEGER, DATE, DATE);
DROP PROCEDURE IF EXISTS sp_cancel_reservation(INTEGER);

DROP FUNCTION IF EXISTS fn_has_overlap(BIGINT, DATE, DATE);
DROP FUNCTION IF EXISTS fn_calculate_amount(INTEGER, NUMERIC);

-- دالة حساب المبلغ
CREATE OR REPLACE FUNCTION fn_calculate_amount(days INTEGER, price_per_night NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
  RETURN days * price_per_night;
END;
$$ LANGUAGE plpgsql;

-- دالة التحقق من التداخل
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

-- إجراء إنشاء الحجز + الدفع + الإشعار
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
  -- جلب بيانات البيت من الجدول الصحيح
  SELECT price_per_night, owner_id, title
    INTO v_house
    FROM listings_tinyhouse
   WHERE id = p_house_id;

  -- حساب الأيام والمبلغ
  v_days   := (p_end_date - p_start_date);
  v_amount := fn_calculate_amount(v_days, v_house.price_per_night);

  -- إنشاء الحجز مع تحديد الحالة
  INSERT INTO reservations_reservation (
    tiny_house_id, tenant_id, start_date, end_date, reservation_status
  ) VALUES (
    p_house_id, p_tenant_id, p_start_date, p_end_date, 'beklemede'
  )
  RETURNING id INTO v_res_id;

  -- إنشاء سجل الدفع
  INSERT INTO payments_payment (
    reservation_id, amount
  ) VALUES (
    v_res_id, v_amount
  );

  -- إنشاء التنبيه
  INSERT INTO notifications_notification (
    user_id, title, message
  ) VALUES (
    v_house.owner_id,
    'Yeni Rezervasyon',
    CONCAT(
      (SELECT username FROM auth_user WHERE id = p_tenant_id),
      ' adlı kullanıcı, ',
      p_start_date::TEXT, ' ile ', p_end_date::TEXT,
      ' tarihleri arasında \"', v_house.title,
      '\" eviniz için rezervasyon yaptı. Toplam tutar: ',
      v_amount::TEXT, '₺.'
    )
  );
END;
$$;

-- إجراء إلغاء الحجز
CREATE OR REPLACE PROCEDURE sp_cancel_reservation(p_res_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE reservations_reservation
     SET reservation_status = 'iptal'
   WHERE id = p_res_id;
END;
$$;

-- Trigger بعد الدفع
CREATE OR REPLACE FUNCTION trg_after_payment()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE reservations_reservation
     SET reservation_status = 'onaylandı'
   WHERE id = NEW.reservation_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_after_payment
AFTER INSERT ON payments_payment
FOR EACH ROW
EXECUTE FUNCTION trg_after_payment();

-- Trigger قبل إنشاء الحجز
CREATE OR REPLACE FUNCTION trg_before_reservation()
RETURNS TRIGGER AS $$
BEGIN
  IF fn_has_overlap(NEW.tiny_house_id, NEW.start_date, NEW.end_date) THEN
    RAISE EXCEPTION 'Seçilen tarihler, mevcut bir rezervasyonla çakışıyor.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_before_reservation
BEFORE INSERT ON reservations_reservation
FOR EACH ROW
EXECUTE FUNCTION trg_before_reservation();
""",
            reverse_sql="""\
-- لا حاجة لعكس هذه الإجراءات: سنكتفي بإسقاطها
DROP TRIGGER IF EXISTS tg_before_reservation ON reservations_reservation;
DROP FUNCTION IF EXISTS trg_before_reservation();

DROP TRIGGER IF EXISTS tg_after_payment ON payments_payment;
DROP FUNCTION IF EXISTS trg_after_payment();

DROP PROCEDURE IF EXISTS sp_create_reservation(BIGINT, INTEGER, DATE, DATE);
DROP PROCEDURE IF EXISTS sp_cancel_reservation(INTEGER);

DROP FUNCTION IF EXISTS fn_has_overlap(BIGINT, DATE, DATE);
DROP FUNCTION IF EXISTS fn_calculate_amount(INTEGER, NUMERIC);
""",
        ),
    ]
