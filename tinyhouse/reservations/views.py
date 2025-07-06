from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.contrib import messages
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import json, datetime
from .models import Reservation
from listings.models import TinyHouse
from payments.models import Payment
from notifications.models import Notification
from django.contrib.auth import get_user_model
from .forms import ReservationDatesForm  # new form for validation

User = get_user_model()

STATUS_CHOICES = [
    ('beklemede', 'beklemede'),
    ('onayli',   'onayli'),
    ('iptal',    'iptal'),
]


# Create your views here.
@login_required
def admin_reservation_management(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'admin':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Yönetici İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # معالجة زر الإلغاء من لوحة المشرف
    if request.method == 'POST' and 'admin_cancel_id' in request.POST:
        res_id = request.POST.get('admin_cancel_id')
        try:
            res = Reservation.objects.get(pk=res_id)
            owner = res.tiny_house.owner
            tenant = res.tenant

            # تحقق من الحالة قبل الإلغاء
            if res.reservation_status == 'iptal':
                messages.warning(request, f"Rezervasyon #{res_id} zaten iptal edilmiş.")
            elif res.reservation_status == 'tamamlandi':
                messages.warning(request, f"Rezervasyon #{res_id} tamamlandı ve iptal edilemez.")
            else:
                res.reservation_status = 'iptal'
                res.save()
                # إلغاء الدفع المرتبط إن وجد
                Payment.objects.filter(reservation=res).update(payment_status='iptal')
                messages.success(request, f"Rezervasyon #{res_id} iptal edildi.")

                # إشعار لصاحب المنزل
                Notification.objects.create(
                    user=owner,
                    title='Rezervasyon iptal edildi',
                    message=(
                        f"Rezervasyon #{res_id} '{res.tiny_house.title}' iptal edildi."
                    )
                )
                # إشعار للمستأجر
                Notification.objects.create(
                    user=tenant,
                    title='Rezervasyonunuz iptal edildi',
                    message=(
                        f"Rezervasyonunuz #{res_id} '{res.tiny_house.title}' yönetici tarafından iptal edildi."
                    )
                )
        except Reservation.DoesNotExist:
            messages.error(request, 'Rezervasyon bulunamadı.')
        return redirect('admin_reservation_management')

    # معالجة زر الموافقة من لوحة المشرف
    if request.method == 'POST' and 'admin_agree_id' in request.POST:
        res_id = request.POST.get('admin_agree_id')
        try:
            res = Reservation.objects.get(pk=res_id)
            owner = res.tiny_house.owner
            tenant = res.tenant

            # تحقق من الحالة قبل الموافقة
            if res.reservation_status == 'onayli':
                messages.warning(request, f"Rezervasyon #{res_id} zaten onaylanmış.")
            else:
                res.reservation_status = 'onayli'
                res.save()
                messages.success(request, f"Rezervasyon #{res_id} onaylandı.")

                # إشعار لصاحب المنزل
                Notification.objects.create(
                    user=owner,
                    title='Rezervasyon onaylandı',
                    message=(
                        f"Rezervasyon #{res_id} '{res.tiny_house.title}' onaylandı."
                    )
                )
                # إشعار للمستأجر
                Notification.objects.create(
                    user=tenant,
                    title='Rezervasyonunuz onaylandı',
                    message=(
                        f"Rezervasyonunuz #{res_id} '{res.tiny_house.title}' yönetici tarafından onaylandı."
                    )
                )
        except Reservation.DoesNotExist:
            messages.error(request, 'Rezervasyon bulunamadı.')
        return redirect('admin_reservation_management')

    # جلب كل الحجوزات
    reservations = (
        Reservation.objects
        .select_related('tiny_house', 'tenant', 'tiny_house__owner')
        .all()
    )
    # إعداد قائمة مع المبلغ الكلّي وحقل صاحب البيت
    reservations_list = []
    for res in reservations:
        nights = (res.end_date - res.start_date).days
        total_amount = nights * res.tiny_house.price_per_night
        reservations_list.append({
            'id': res.id,
            'owner': res.tiny_house.owner,
            'tenant': res.tenant,
            'house': res.tiny_house,
            'start_date': res.start_date,
            'end_date': res.end_date,
            'total_amount': total_amount,
            'reservation_status': res.get_reservation_status_display(),
            'payment': getattr(res.payment_set.first(), 'payment_status', None),
            'payment_id': getattr(res.payment_set.first(), 'id', None),
        })

    context = {
        'reservations_list': reservations_list,
    }
    return render(request, 'reservations/admin_reservation_management.html', context)


@login_required
def owner_reservation_management(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'owner':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Ev Sahibi İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    user = request.user

    # معالجة أزرار القبول والرفض والدفع
    if request.method == 'POST':
        # قبول الحجز
        if 'approve_id' in request.POST:
            res_id = request.POST.get('approve_id')
            try:
                res = Reservation.objects.get(pk=res_id, tiny_house__owner=user)
                res.reservation_status = 'onayli'
                res.save()
                # إنشاء إشعار للمستأجر
                Notification.objects.create(
                    user=res.tenant,
                    title='Rezervasyon Onaylandı',
                    message=f"Rezervasyonunuz #{res.id} onaylandı"
                )
                messages.success(request, 'Rezervasyon kabul edildi.')
            except Reservation.DoesNotExist:
                messages.error(request, 'Rezervasyon bulunamadı veya yetkiniz yok.')

        # رفض الحجز
        if 'reject_id' in request.POST:
            res_id = request.POST.get('reject_id')
            try:
                res = Reservation.objects.get(pk=res_id, tiny_house__owner=user)
                res.reservation_status = 'iptal'
                res.save()
                Payment.objects.filter(reservation=res).update(payment_status='iptal')
                # إنشاء إشعار للمستأجر
                Notification.objects.create(
                    user=res.tenant,
                    title='Rezervasyon İptal Edildi',
                    message=f"Rezervasyonunuz #{res.id} iptal edildi"
                )
                messages.success(request, 'Rezervasyon ve ödeme iptal edildi.')
            except Reservation.DoesNotExist:
                messages.error(request, 'Rezervasyon bulunamadı veya yetkiniz yok.')

        # تأكيد الدفع
        if 'paid_id' in request.POST:
            pay_id = request.POST.get('paid_id')
            try:
                pay = Payment.objects.get(pk=pay_id, reservation__tiny_house__owner=user)
                pay.payment_status = 'tamamlandi'
                pay.payment_date = timezone.now()
                pay.payment_method = 'cash'
                pay.save()
                # إنشاء إشعار للمستأجر
                Notification.objects.create(
                    user=pay.reservation.tenant,
                    title='Ödeme Tamamlandı',
                    message=f"Ödemeniz #{pay.id} tamamlandı"
                )
                messages.success(request, 'Ödeme durumu tamamlandı olarak güncellendi.')
            except Payment.DoesNotExist:
                messages.error(request, 'Ödeme kaydı bulunamadı veya yetkiniz yok.')

        return redirect('owner_reservation_management')

    # 1) طلبات الحجز الجديدة (status = 'beklemede')
    qs_requests = (
        Reservation.objects
        .filter(tiny_house__owner=user, reservation_status='beklemede')
        .select_related('tiny_house', 'tenant')
    )
    reservation_requests = []
    for res in qs_requests:
        nights = (res.end_date - res.start_date).days
        res.total_amount = nights * res.tiny_house.price_per_night
        reservation_requests.append(res)

    # 2) حجوزات مُوافق عليها وتنتظر الدفع
    payments_waiting = (
        Payment.objects
        .filter(
            reservation__tiny_house__owner=user,
            reservation__reservation_status='onayli',
            payment_status='beklemede'
        )
        .select_related('reservation__tiny_house', 'reservation__tenant')
    )

    # 3) حجوزات مُكتملة الدفع
    payments_completed = (
        Payment.objects
        .filter(
            reservation__tiny_house__owner=user,
            payment_status='tamamlandi'
        )
        .select_related('reservation__tiny_house', 'reservation__tenant')
    )

    # 4) حجوزات مُلغاة
    qs_cancelled = (
        Reservation.objects
        .filter(tiny_house__owner=user, reservation_status='iptal')
        .select_related('tiny_house', 'tenant')
    )
    cancelled_reservations = []
    for res in qs_cancelled:
        nights = (res.end_date - res.start_date).days
        res.total_amount = nights * res.tiny_house.price_per_night
        cancelled_reservations.append(res)

    context = {
        'reservation_requests':     reservation_requests,
        'payments_waiting':         payments_waiting,
        'payments_completed':       payments_completed,
        'cancelled_reservations':   cancelled_reservations,
    }
    return render(request, 'reservations/owner_reservation_management.html', context)


@login_required
def tenant_make_reservation(request, house_id):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'tenant':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Kiracı İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية

    house = get_object_or_404(TinyHouse, id=house_id)
    errors = []
    amount = None

    # تجهيز أحداث التقويم
    availability = [{
        'title': 'Müsait',
        'start': house.start_date.isoformat(),
        'end': (house.end_date + datetime.timedelta(days=1)).isoformat(),
        'allDay': True,
        'color': '#28a745',
    }]

    reservations = Reservation.objects.filter(tiny_house=house) \
        .exclude(reservation_status='iptal')

    reserved_events = [{
        'title': 'Müsait Değil',
        'start': r.start_date.isoformat(),
        'end': (r.end_date + datetime.timedelta(days=1)).isoformat(),
        'allDay': True,
        'color': '#dc3545',
    } for r in reservations]

    calendar_events = availability + reserved_events
    calendar_events_json = json.dumps(calendar_events, cls=DjangoJSONEncoder)

    if request.method == 'POST':
        form = ReservationDatesForm(request.POST)
        if not form.is_valid():
            errors = form.errors.get('__all__', [])
        else:
            sd = form.cleaned_data['start_date']
            ed = form.cleaned_data['end_date']
            # التحقق من ضمن فترة توفر المنزل
            if sd < house.start_date or ed > house.end_date:
                errors.append(
                    f'Tarihler {house.start_date} ile {house.end_date} aralığında olmalıdır.'
                )
            # التحقق من التداخل مع حجوزات قائمة
            overlap = Reservation.objects.filter(
                tiny_house=house,
                start_date__lt=ed,
                end_date__gt=sd
            ).exclude(reservation_status='iptal').exists()
            if overlap:
                errors.append('Seçilen tarihler, mevcut bir rezervasyonla çakışıyor.')

            if not errors:
                days = (ed - sd).days
                amount = days * house.price_per_night

                if request.POST.get('action') == 'reserve':
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "CALL sp_create_reservation(%s, %s, %s, %s)",
                                [house.id, request.user.id, sd, ed]
                            )
                    except Exception as e:
                        messages.error(request, str(e))
                    else:
                        messages.success(
                            request,
                            f'Rezervasyon Başarıyla Oluşturuldu. Toplam Tutar: {amount}₺'
                        )
                        return redirect('tenant_my_reservations')
    else:
        form = ReservationDatesForm()

    context = {
        'house': house,
        'errors': errors,
        'amount': amount,
        'calendar_events_json': calendar_events_json,
        'form': form,
    }
    return render(request, 'reservations/tenant_make_reservation.html', context)



@login_required
def tenant_my_reservations(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'tenant':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Kiracı İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية

    tenant = request.user

    # ———— معالجة إلغاء الحجز ودفعه ————
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'cancel':
            reservation_id = request.POST.get('reservation_id')
            # جلب الكائن للتحقق من الصلاحيات فقط
            reservation = get_object_or_404(Reservation, id=reservation_id, tenant=tenant)

            # استدعاء الإجراء المخزن لإلغاء الحجز
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_cancel_reservation(%s);", [reservation_id])

            # تحديث حالة الدفع يدوياً
            payment = Payment.objects.filter(reservation=reservation).first()
            if payment:
                payment.payment_status = 'iptal'
                payment.save()

            # إنشاء الإشعار
            owner = reservation.tiny_house.owner
            Notification.objects.create(
                user=owner,
                title='Rezervasyon iptal edildi',
                message=f'{tenant.username} kullanıcısı #{reservation.id} numaralı rezervasyonu iptal etti.',
            )

            messages.success(request, 'Rezervasyon başarıyla iptal edildi.')
            return redirect('tenant_my_reservations')

        if action == 'pay':
            reservation_id = request.POST.get('reservation_id')
            reservation = get_object_or_404(Reservation, id=reservation_id, tenant=tenant)

            # تحقق من أن حالة الحجز 'onayli'
            if reservation.reservation_status != 'onayli':
                messages.error(request, 'Bu rezervasyon için ödeme yapılamaz. Rezervasyon onaylı olmalıdır.')
                return redirect('tenant_my_reservations')

            # ———— هنا نُعرِّف payment قبل استخدامه ————
            payment = Payment.objects.filter(reservation=reservation).first()
            if not payment:
                # إذا لم يوجد Payment مسبقاً، أنشئ واحداً جديداً
                payment = Payment.objects.create(
                    reservation=reservation,
                    # هنا حط الخصائص الضرورية مثل amount أو تاريخ الإنشاء...
                )

            messages.success(request, 'Ödeme işlemi başlatıldı. Lütfen ödeme sağlayıcısına yönlendiriliyorsunuz.')
            return redirect('tenant_make_payment', payment.id)

    # ———— منطق جلب الحجوزات للعرض ————
    reservations = (
        Reservation.objects
        .filter(tenant=tenant)
        .select_related('tiny_house', 'tiny_house__owner')
        .order_by('-created_at')
    )

    unpaid_reservations = []
    paid_reservations = []
    cancelled_reservations = []

    for reservation in reservations:
        payment = Payment.objects.filter(reservation=reservation).first()
        if reservation.reservation_status == 'iptal':
            cancelled_reservations.append((reservation, payment))
        elif payment and payment.payment_status == 'tamamlandi':
            paid_reservations.append((reservation, payment))
        else:
            unpaid_reservations.append((reservation, payment))

    context = {
        'unpaid_reservations': unpaid_reservations,
        'paid_reservations': paid_reservations,
        'cancelled_reservations': cancelled_reservations,
        'errors': [],
    }
    return render(request, 'reservations/tenant_my_reservations.html', context)


