from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch,Count, Sum, Q
from django.db.models import OuterRef, Subquery
from django.contrib.auth.models import User
from listings.models import TinyHouse
from reservations.models import Reservation
from payments.models import Payment
from reviews.models import Review
from accounts.models import Profile
from django.contrib import messages

# Create your views here.
@login_required
def admin_dashboard(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'admin':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Yönetici İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    # إحصائيات عامة
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_reservations = Reservation.objects.count()
    total_revenue = (
        Payment.objects
        .filter(payment_status='tamamlandi')
        .aggregate(total=Sum('amount'))['total'] or 0
    )

    # قائمة المستخدمين مع أدوارهم وحالتهم
    users = (
        User.objects
        .select_related('profile')
        .all()
        .order_by('username')
    )

    # قائمة الحجوزات الأخيرة
    reservations = (
        Reservation.objects
        .select_related('tiny_house__owner', 'tenant')
        .order_by('-created_at')[:10]
    )

    # قائمة الدفعات الأخيرة
    payments = (
        Payment.objects
        .select_related('reservation')
        .order_by('-payment_date')[:10]
    )

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_reservations': total_reservations,
        'total_revenue': total_revenue,
        'users': users,
        'reservations': reservations,
        'payments': payments,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def owner_dashboard(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'owner':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Ev Sahibi İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    user = request.user

    # 1) جميع الإعلانات التي يملكها
    houses = TinyHouse.objects.filter(owner=user)

    # 2) إحصائيات البطاقات
    total_listings = houses.count()

    approved_reservations = Reservation.objects.filter(
        tiny_house__in=houses,
        reservation_status='onayli'
    ).count()

    pending_payment_reservations = Reservation.objects.filter(
        tiny_house__in=houses
    ).filter(
        ~Q(payment__payment_status='tamamlandi')  # الحجوزات التي ليس لها دفعة مكتملة
    ).distinct().count()

    incoming_reviews = Review.objects.filter(
        reservation__tiny_house__in=houses,
        is_active=True
    ).count()

    total_revenue = Payment.objects.filter(
        reservation__tiny_house__in=houses,
        payment_status='tamamlandi'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # 3) أحدث 5 حجوزات مع حالة الدفع
    recent_reservations = (
        Reservation.objects
        .filter(tiny_house__in=houses)
        .select_related('tiny_house')
        .prefetch_related('payment_set')
        .order_by('-created_at')[:5]
    )
    latest_payment_subquery = Payment.objects.filter(
    reservation=OuterRef('pk')
    ).order_by('-payment_date').values('payment_status')[:1]

    recent_reservations = (
    Reservation.objects
    .filter(tiny_house__in=houses)
    .annotate(latest_payment_status=Subquery(latest_payment_subquery))
    .order_by('-created_at')[:5]
    )
    
    
    

    context = {
        'total_listings': total_listings,
        'approved_reservations': approved_reservations,
        'pending_payment_reservations': pending_payment_reservations,
        'incoming_reviews': incoming_reviews,
        'total_revenue': total_revenue,
        'recent_reservations': recent_reservations,
    }
    return render(request, 'dashboard/owner_dashboard.html', context)


@login_required
def tenant_dashboard(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'tenant':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Kiracı İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # جلب قيم الفلاتر من الاستعلام GET
    search_query = request.GET.get('q', '').strip()
    location_filter = request.GET.get('location', '').strip()
    date_filter = request.GET.get('date', '').strip()

    # بداية بفلترة الإعلانات النشطة فقط
    houses = TinyHouse.objects.filter(is_active=True, tiny_house_status='onayli')

    # فلترة بالكلمة المفتاحية
    if search_query:
        houses = houses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # فلترة بالموقع
    if location_filter:
        houses = houses.filter(location__iexact=location_filter)

    # فلترة بالتواريخ
    import datetime
    today = datetime.date.today()
    if date_filter == 'today':
        houses = houses.filter(start_date__lte=today, end_date__gte=today)
    elif date_filter == 'weekend':
        weekend_start = today + datetime.timedelta((4 - today.weekday()) % 7)
        weekend_end = weekend_start + datetime.timedelta(days=2)
        houses = houses.filter(
            start_date__lte=weekend_end,
            end_date__gte=weekend_start
        )

    # Prefetch: لكل منزل، جلب الحجوزات مع التعليقات المرتبطة بها
    houses = houses.prefetch_related(
        Prefetch(
            'reservation_set',
            queryset=Reservation.objects.prefetch_related('review_set'),
            to_attr='prefetched_reservations'
        )
    )

    # إعلانات شائعة (أحدث 4)
    popular_houses = houses.order_by('-created_at')[:4]

    context = {
        'houses': houses,
        'popular_houses': popular_houses,
    }
    return render(request, 'dashboard/tenant_dashboard.html', context)
    
