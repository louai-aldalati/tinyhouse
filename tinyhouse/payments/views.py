from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.db.models import Prefetch
from .models import Payment
from listings.models import TinyHouse
from reservations.models import Reservation

# Create your views here.
@login_required
def admin_payment_management(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'admin':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Yönetici İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # جلب كل المدفوعات مع ربط الحجوزات، وبيانات المُلاك والمستأجرين
    payments = (
        Payment.objects
        .select_related(
            'reservation__tiny_house__owner',
            'reservation__tenant'
        )
        .order_by('-payment_date')
    )

    context = {
        'payments': payments,
    }
    return render(request, 'payments/admin_payment_management.html', context)


@login_required
def owner_payment_management(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'owner':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Ev Sahibi İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # 1. احصل على كل الـ TinyHouse التي يملكها المستخدم
    houses = TinyHouse.objects.filter(owner=request.user)

    # 2. احصل على كل الـ Payment المرتبطة بحجوزات هذه البيوت
    payments = (
        Payment.objects
        .filter(reservation__tiny_house__in=houses)
        .select_related('reservation__tiny_house')
        .order_by('-payment_date')
    )

    # 3. اجمع تقرير الدخل شهرياً
    income_reports = (
        Payment.objects
        .filter(reservation__tiny_house__in=houses, payment_status='tamamlandi')
        .annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(
            total_reservations=Count('id'),
            total_revenue=Sum('amount')
        )
        .order_by('-month')
    )

    context = {
        'payments': payments,
        'income_reports': income_reports,
        # الرسائل (messages) تأتي تلقائياً إذا استخدمت django.contrib.messages
        # و'errors' يمكنك تمريرها من أي مكان تحتاجه
    }
    return render(request, 'payments/owner_payment_management.html', context)


@login_required
def tenant_make_payment(request, payment_id):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'tenant':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Kiracı İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # استرجاع سجل الدفع أو عرض 404
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        # معالجة بيانات الدفع من النموذج
        card_number = request.POST.get('card_number')
        expiry = request.POST.get('expiry')
        cvc = request.POST.get('cvc')

        errors = []
        if not card_number:
            errors.append('Kart numarası gerekli.')
        if not expiry:
            errors.append('Son kullanma tarihi gerekli.')
        if not cvc:
            errors.append('CVC gerekli.')

        if not errors:
            # هنا يمكنك استدعاء بوابة الدفع الحقيقية
            # مثلاً: response = gateway.charge(...)
            # ثم تحديث السجل بناءً على النتيجة:
            payment.payment_status = 'tamamlandi'
            payment.payment_date = timezone.now()
            payment.payment_method = 'kredi_karti'
            payment.transaction_id = 'TXN-' + str(payment.id)
            payment.gateway_response = {'approved': True}
            payment.save()

            messages.success(request, 'Ödeme işlemi başarılı.')
            return redirect('tenant_make_payment', payment_id=payment.id)

        # إذا وجدت أخطاء، تمريرها إلى القالب
        return render(request, 'payments/tenant_make_payment.html', {
            'payment': payment,
            'errors': errors,
        })

    # GET: عرض النموذج مع بيانات الدفع
    return render(request, 'payments/tenant_make_payment.html', {
        'payment': payment,
    })

