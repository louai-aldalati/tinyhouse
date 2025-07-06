from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from decimal import Decimal
from .models import TinyHouse, TinyHouseImage
from django.core.serializers.json import DjangoJSONEncoder
import json
import datetime

from django.contrib.auth.models import User
from accounts.models import  Profile
from reservations.models import Reservation
from notifications.models import Notification

# Create your views here.
@login_required
def admin_listing_management(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'admin':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Yönetici İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # Handle status updates
    if request.method == 'POST':
        action = request.POST.get('action')
        ilan_id = request.POST.get('ilan_id')
        try:
            ilan = TinyHouse.objects.get(pk=ilan_id)

            # تحديد النصوص الخاصة بالإشعار بالتركية
            if action == 'onayla':
                ilan.tiny_house_status = 'onayli'
                notif_title = 'İlanınız onaylandı'
                notif_message = f"'{ilan.title}' başlıklı ilanınız yönetici tarafından onaylandı."
            elif action == 'reddet':
                ilan.tiny_house_status = 'iptal'
                notif_title = 'İlanınız reddedildi'
                notif_message = f"'{ilan.title}' başlıklı ilanınız yönetici tarafından reddedildi."
            elif action == 'geri_onay':
                ilan.tiny_house_status = 'onayli'
                notif_title = 'İlanınız yeniden onaylandı'
                notif_message = f"'{ilan.title}' başlıklı ilanınız yeniden onaylandı."
            elif action == 'geri_bekle':
                ilan.tiny_house_status = 'beklemede'
                notif_title = 'İlanınız beklemeye alındı'
                notif_message = f"'{ilan.title}' başlıklı ilanınız tekrar beklemede."
            else:
                notif_title = None

            ilan.save()
            
            # إنشاء الإشعار إذا كان هناك عنوان
            if notif_title:
                Notification.objects.create(
                    user=ilan.owner,           # صاحب الإعلان
                    title=notif_title,
                    message=notif_message
                )

            messages.success(
                request,
                f"İlan durumu güncellendi: {ilan.title} -> {ilan.tiny_house_status}"
            )
        except TinyHouse.DoesNotExist:
            messages.error(request, "İlan bulunamadı.")
        return redirect('admin_listing_management')

    # Fetch listings by status
    beklemede_list = TinyHouse.objects.filter(tiny_house_status='beklemede')
    onayli_list   = TinyHouse.objects.filter(tiny_house_status='onayli')
    iptal_list    = TinyHouse.objects.filter(tiny_house_status='iptal')

    context = {
        'beklemede_list': beklemede_list,
        'onayli_list': onayli_list,
        'iptal_list': iptal_list,
    }
    return render(request, 'listings/admin_listing_management.html', context)

    # Fetch listings by status
    beklemede_list = TinyHouse.objects.filter(tiny_house_status='beklemede')
    onayli_list   = TinyHouse.objects.filter(tiny_house_status='onayli')
    iptal_list    = TinyHouse.objects.filter(tiny_house_status='iptal')

    context = {
        'beklemede_list': beklemede_list,
        'onayli_list': onayli_list,
        'iptal_list': iptal_list,
    }
    return render(request, 'listings/admin_listing_management.html', context)


@login_required
def admin_listing_add(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'admin':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Yönetici İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # جلب جميع أصحاب المنازل (Profile.role == 'owner')
    owners = Profile.objects.filter(role='owner').select_related('user')

    if request.method == 'POST':
        owner_id        = request.POST.get('owner')
        title           = request.POST.get('title')
        location        = request.POST.get('location')
        start_date      = request.POST.get('start_date')
        end_date        = request.POST.get('end_date')
        max_tenant      = int(request.POST.get('max_tenant') or 0)
        price_per_night = Decimal(request.POST.get('price_per_night') or '0')
        description     = request.POST.get('description')
        is_active       = True if request.POST.get('is_active') == 'active' else False

        # خريطة لترجمة قيم الحالة الواردة من الـ form
        status_map = {
            'onayli':   'onayli',
            'beklemede':'beklemede',
            'iptal':    'iptal',
        }
        status_key = request.POST.get('status')
        status     = status_map.get(status_key, 'beklemede')

        # جلب الـ Profile الصحيح حسب user__id
        try:
            owner_profile = Profile.objects.get(user__id=owner_id, role='owner')
            owner_user    = owner_profile.user
        except Profile.DoesNotExist:
            messages.error(request, 'Seçilmiş Ev Sahibi Ortada Yok.')
            return render(request, 'listings/admin_listing_add.html', {
                'owners': owners,
                'errors': ['Seçilen Ev Sahip Yanlış.']
            })

        # إنشاء كائن TinyHouse
        house = TinyHouse.objects.create(
            owner=owner_user,
            title=title,
            location=location,
            start_date=start_date,
            end_date=end_date,
            max_tenant=max_tenant,
            price_per_night=price_per_night,
            description=description,
            is_active=is_active,
            status=status
        )

        # رفع الصور (إن وجدت)
        images = request.FILES.getlist('image')
        for img in images:
            TinyHouseImage.objects.create(
                tiny_house=house,
                image=img
            )
            
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_users = User.objects.filter(profile__role='admin')
        for admin_user in admin_users:
            Notification.objects.create(
                user=admin_user,
                title='Yeni ilan eklendi',
                message=f'{owner_user.username} kullanıcısı yeni bir ev ilanı oluşturdu: "{house.title}"',
            )

        messages.success(request, 'İlan Başarıyla Oluşturuldu.')
        return redirect('admin_listing_management')

    # عرض النموذج مع قائمة المالكين
    return render(request, 'listings/admin_listing_add.html', {
        'owners': owners
    })



@login_required
def owner_listing_management(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'owner':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Ev Sahibi İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # تحقق من أن المستخدم هو owner
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, "Kullanıcı Profili Bulunamadı.")
        return redirect('index')

    if profile.role != 'owner':
        messages.error(request, "İlan Ekleme İzniniz Yok.")
        return redirect('/dashboard/owner_dashboard/')

    # جلب الكلمة المفتاحية من GET للبحث
    query = request.GET.get('search', '').strip()

    # جلب إعلانات المالك، وتصفية بالبحث إن وُجد
    houses = TinyHouse.objects.filter(owner=request.user)
    if query:
        houses = houses.filter(title__icontains=query)

    if request.method == 'POST':
        # -- Handle deletion if requested --
        delete_id = request.POST.get('delete_id')
        if delete_id:
            try:
                house_to_delete = TinyHouse.objects.get(id=delete_id, owner=request.user)
                house_to_delete.delete()
                messages.success(request, "İlan Başarıyla Silindi.")
            except TinyHouse.DoesNotExist:
                messages.error(request, "Silinecek ilan bulunamadı.")
            return redirect('owner_listing_management')

        # Handle new listing creation
        title           = request.POST.get('title')
        location        = request.POST.get('location')
        start_date      = request.POST.get('start_date')
        end_date        = request.POST.get('end_date')
        max_tenant      = request.POST.get('max_tenant')
        price_per_night = request.POST.get('price_per_night')
        description     = request.POST.get('description')
        is_active_str   = request.POST.get('is_active')  # "active" أو "inactive"

        is_active = True if is_active_str == 'active' else False

        house = TinyHouse.objects.create(
            owner=request.user,
            title=title,
            location=location,
            start_date=start_date,
            end_date=end_date,
            max_tenant=max_tenant,
            price_per_night=price_per_night,
            description=description,
            is_active=is_active,
        )

        images = request.FILES.getlist('image')
        for img in images:
            TinyHouseImage.objects.create(
                tiny_house=house,
                image=img
            )

        messages.success(request, "İlan Başarıyla Eklendi.")
        return redirect('owner_listing_management')

    # GET: قائمة الإعلانات الحالية
    houses = TinyHouse.objects.filter(owner=request.user)

    return render(request, 'listings/owner_listing_management.html', {
        'houses': houses,
        'search_query': query,
    })

@login_required
def owner_listing_edit(request, pk):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'owner':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Ev Sahibi İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # تحقق من أن المستخدم هو owner
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, "Kullanıcı Profili Bulunamadı.")
        return redirect('index')

    if profile.role != 'owner':
        messages.error(request, "Düzenleme İzniniz Yok.")
        return redirect('owner_listing_management')

    # جلب الإعلان المعني
    try:
        house = TinyHouse.objects.get(id=pk, owner=request.user)
    except TinyHouse.DoesNotExist:
        messages.error(request, "İlan Bulunamadı.")
        return redirect('owner_listing_management')

    if request.method == 'POST':
        # تحديث الحقول
        house.title           = request.POST.get('title')
        house.location        = request.POST.get('location')
        house.start_date      = request.POST.get('start_date')
        house.end_date        = request.POST.get('end_date')
        house.max_tenant      = request.POST.get('max_tenant')
        house.price_per_night = request.POST.get('price_per_night')
        house.description     = request.POST.get('description')
        is_active_str         = request.POST.get('is_active')
        house.is_active       = True if is_active_str == 'active' else False
        house.save()

        # صور جديدة (إذا وُجدت)
        images = request.FILES.getlist('image')
        for img in images:
            TinyHouseImage.objects.create(
                tiny_house=house,
                image=img
            )

        messages.success(request, "İlan Başarıyla Güncellendi.")
        return redirect('owner_listing_management')

    # GET: عرض النموذج مع البيانات الحالية
    return render(request, 'listings/owner_listing_edit.html', {
        'house': house,
    })


@login_required
def tenant_listing_details(request, pk):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'tenant':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Kiracı İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # جلب المنزل أو إظهار 404 إن لم يوجد
    house = get_object_or_404(TinyHouse, pk=pk)
    # جلب كل الصور المرتبطة بالمنزل
    images = TinyHouseImage.objects.filter(tiny_house=house)

    # تجهيز فترة التوفر الكاملة كحدث
    availability = [{
        'title': 'Müsait',
        'start': house.start_date.isoformat(),
        'end': (house.end_date + datetime.timedelta(days=1)).isoformat(),
        'allDay': True,
        'color': '#28a745',  # أخضر للتوفر
    }]

    # جلب كل الحجوزات المرتبطة بالمنزل
    reservations = Reservation.objects.filter(tiny_house=house)

    # تجهيز أحداث للحجوزات لاستبعادها أو تمييزها
    reservations = reservations.exclude(reservation_status='iptal')
    reserved_events = []
    for res in reservations:
        reserved_events.append({
            'title': 'müsait Değil',
            'start': res.start_date.isoformat(),
            'end': (res.end_date + datetime.timedelta(days=1)).isoformat(),
            'allDay': True,
            'color': '#dc3545',  # أحمر للحجوزات
        })

    # دمج الأحداث: التوفر والحجوزات
    events = availability + reserved_events

    context = {
        'house': house,
        'images': images,
        'calendar_events_json': json.dumps(events, cls=DjangoJSONEncoder),
    }
    return render(request, 'listings/tenant_listing_details.html', context)

