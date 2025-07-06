from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Review
from reservations.models import Reservation
from notifications.models import Notification

# Create your views here.

@login_required
def admin_comments_and_ratings(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'admin':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Yönetici İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # 1) معالجة تغيير حالة التعليق (POST)
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        action = request.POST.get('action')  # "deactivate" أو "activate"
        try:
            review = Review.objects.get(id=review_id)
            owner = review.reservation.tiny_house.owner
            tenant = review.reservation.tenant

            if action == 'deactivate':
                review.is_active = False
                messages.success(request, f'Yorum #{review_id} pasife alındı.')

                # إشعار لصاحب المنزل
                Notification.objects.create(
                    user=owner,
                    title='Yorum pasifleştirildi',
                    message=(
                        f"'{review.reservation.tiny_house.title}' başlıklı ilanınızdaki "
                        f"#{review_id} numaralı yorum pasif hale getirildi."
                    )
                )
                # إشعار للمستأجر
                Notification.objects.create(
                    user=tenant,
                    title='Yorumunuz pasifleştirildi',
                    message=(
                        f"#{review_id} numaralı yorumunuz yönetici tarafından pasif hale getirildi."
                    )
                )

            elif action == 'activate':
                review.is_active = True
                messages.success(request, f'Yorum #{review_id} tekrar aktifleştirildi.')

                # إشعار لصاحب المنزل
                Notification.objects.create(
                    user=owner,
                    title='Yorum aktifleştirildi',
                    message=(
                        f"'{review.reservation.tiny_house.title}' başlıklı ilanınızdaki "
                        f"#{review_id} numaralı yorum tekrar aktif hale getirildi."
                    )
                )
                # إشعار للمستأجر
                Notification.objects.create(
                    user=tenant,
                    title='Yorumunuz aktifleştirildi',
                    message=(
                        f"#{review_id} numaralı yorumunuz yönetici tarafından tekrar aktif hale getirildi."
                    )
                )

            review.save()
        except Review.DoesNotExist:
            messages.error(request, 'Geçersiz yorum ID’si.')
        return redirect('admin_comments_and_ratings')

    # 2) فلترة البحث (GET)
    q = request.GET.get('q', '').strip()
    reviews = Review.objects.select_related(
        'reservation__tiny_house__owner',
        'reservation__tenant'
    )
    if q:
        reviews = reviews.filter(
            Q(comment__icontains=q) |
            Q(reservation__tenant__username__icontains=q) |
            Q(reservation__tiny_house__title__icontains=q)
        )
    reviews = reviews.order_by('-created_at')

    return render(request, 'reviews/admin_comments_and_ratings.html', {
        'reviews': reviews,
        'search_query': q,
    })

@login_required
def owner_comments_and_ratings(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'owner':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Ev Sahibi İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    user = request.user

    # 1) معالجة إرسال الرد
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        reply_text = request.POST.get('reply')
        try:
            review = Review.objects.get(
                id=review_id,
                reservation__tiny_house__owner=user
            )
            review.reply = reply_text
            review.save()
            
            tenant = review.reservation.tenant
            Notification.objects.create(
                user=tenant,
                title='Sahibinden cevap aldınız',
                message=f'"{reply_text}" ile rezervasyon #{review.reservation.id} için yorumunuza cevap verildi.',
            )
            messages.success(request, 'Cevabınız kaydedildi.')
        except Review.DoesNotExist:
            messages.error(request, 'Geçersiz yorum ID’si.')
        return redirect('owner_comments_and_ratings')

    # 2) جلب كل التعليقات النشطة المرتبطة بمنازل هذا المالك
    reviews = (
        Review.objects
        .filter(
            reservation__tiny_house__owner=user,
            is_active=True
        )
        .select_related('reservation__tiny_house', 'reservation__tenant')
        .order_by('-created_at')
    )

     # أسفل جمع التعليقات:
    star_range = range(1, 6)

    return render(request, 'reviews/owner_comments_and_ratings.html', {
        'reviews': reviews,
        'star_range': star_range,   # هنا
    })

@login_required
def tenant_comments_and_ratings(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'tenant':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Kiracı İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    user = request.user

    # 1) معالجة إرسال نموذج جديد
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        try:
            res = Reservation.objects.get(id=reservation_id, tenant=user)
            # نتأكد أنّ المستخدم فعلياً مستأجر لهذا الحجز
            Review.objects.create(
                reservation=res,
                rating=rating,
                comment=comment
            )
            owner = res.tiny_house.owner
            Notification.objects.create(
                user=owner,
                title='Yeni yorum ve değerlendirme',
                message=f'{user.username} kullanıcısı #{res.id} numaralı rezervasyon için yorum yaptı: "{comment}"',
            )
            messages.success(request, 'Yorumunuz başarıyla kaydedildi.')
        except Reservation.DoesNotExist:
            messages.error(request, 'Geçersiz rezervasyon.')
        return redirect('tenant_comments_and_ratings')

    # 2) الحجوزات التي أنهت الإقامة ولم يُكتب لها تقييم بعد
    reservations_to_review = Reservation.objects.filter(
        tenant=user,
        reservation_status='onayli'
    ).exclude(
        review__isnull=False
    ).select_related('tiny_house')

    # 3) التقييمات السابقة لهذا المستأجر
    past_reviews = Review.objects.filter(
        reservation__tenant=user,
        is_active=True
    ).select_related('reservation__tiny_house').order_by('-created_at')

    context = {
        'reservations_to_review': reservations_to_review,
        'past_reviews': past_reviews,
    }
    return render(request, 'reviews/tenant_comments_and_ratings.html', context)



