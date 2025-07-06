from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages


from listings.models import TinyHouse
from reservations.models import Reservation
from payments.models import Payment
from reviews.models import Review
# Create your views here.
@login_required
def admin_statistics_and_reporting(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'admin':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Yönetici İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    today = timezone.localdate()
    first_of_month = today.replace(day=1)
    first_of_prev_month = (first_of_month - timedelta(days=1)).replace(day=1)

    # — المستخدمون كما قبل —
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    new_users_this_month = User.objects.filter(date_joined__date__gte=first_of_month).count()

    # — اتجاه الحجوزات كما قبل —
    current_reservations = Reservation.objects.filter(
        created_at__date__gte=first_of_month,
        created_at__date__lte=today
    ).count()
    prev_reservations = Reservation.objects.filter(
        created_at__date__gte=first_of_prev_month,
        created_at__date__lt=first_of_month
    ).count()
    reservation_trend = round((current_reservations - prev_reservations) / prev_reservations * 100) if prev_reservations else 0
    reservation_trend_abs = abs(reservation_trend)
    trend_up = reservation_trend >= 0

    # — توزيع المدفوعات كما قبل —
    payment_dist_qs = (
        Payment.objects
        .values('payment_status')
        .annotate(count=Count('id'))
    )
    payment_labels = [item['payment_status'] for item in payment_dist_qs]
    payment_counts = [item['count'] for item in payment_dist_qs]

    # — اتجاه الحجوزات الشهري (آخر 6 أشهر) كما قبل —
    labels_months = []
    data_reservation = []
    for i in range(5, -1, -1):
        month = (first_of_month - timedelta(days=30*i)).replace(day=1)
        labels_months.append(month.strftime('%b %Y'))
        data_reservation.append(
            Reservation.objects.filter(
                created_at__year=month.year,
                created_at__month=month.month
            ).count()
        )

    # — عدد التعليقات الشهرية (آخر 6 أشهر) —
    labels_reviews = []
    data_reviews = []
    for i in range(5, -1, -1):
        month = (first_of_month - timedelta(days=30*i)).replace(day=1)
        labels_reviews.append(month.strftime('%b %Y'))
        data_reviews.append(
            Review.objects.filter(
                created_at__year=month.year,
                created_at__month=month.month
            ).count()
        )

    # — حالة المحتوى (الإعلانات النشطة مقابل غير النشطة) —
    active_listings = TinyHouse.objects.filter(is_active=True).count()
    inactive_listings = TinyHouse.objects.filter(is_active=False).count()
    content_labels = ['Aktif', 'Pasif']
    content_counts = [active_listings, inactive_listings]

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_this_month': new_users_this_month,
        'reservation_trend_abs': reservation_trend_abs,
        'trend_up': trend_up,

        'payment_labels_json': json.dumps(payment_labels),
        'payment_counts_json': json.dumps(payment_counts),
        'reservation_trend_labels_json': json.dumps(labels_months),
        'reservation_trend_data_json': json.dumps(data_reservation),

        'review_labels_json': json.dumps(labels_reviews),
        'review_data_json': json.dumps(data_reviews),
        'content_labels_json': json.dumps(content_labels),
        'content_counts_json': json.dumps(content_counts),
    }
    return render(request, 'reports/admin_statistics_and_reporting.html', context)