from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.contrib import messages
# Create your views here.
@login_required
def admin_notifications(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'admin':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Yönetici İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # إذا أرسل المستخدم طلب POST للتأكيد على قراءة إشعار
    if request.method == 'POST':
        notif_id = request.POST.get('notif_id')
        if notif_id:
            notif = get_object_or_404(Notification, id=notif_id, user=request.user)
            notif.is_read = True
            notif.save()
        # بعد تغيير حالة الإشعار نعيد توجيه المستخدم للصفحة نفسها
        return redirect('admin_notifications')

    # جلب جميع الإشعارات الخاصة بالمستخدم الحالي، مرتبة من الأحدث للأقدم
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'notifications/admin_notifications.html',
        {
            'notifications': notifications
        }
    )

@login_required
def owner_notifications(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'owner':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Ev Sahibi İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # إذا أرسل المستخدم طلب POST للتأكيد على قراءة إشعار
    if request.method == 'POST':
        notif_id = request.POST.get('notif_id')
        if notif_id:
            notif = get_object_or_404(Notification, id=notif_id, user=request.user)
            notif.is_read = True
            notif.save()
        # بعد تغيير حالة الإشعار نعيد توجيه المستخدم للصفحة نفسها
        return redirect('owner_notifications')
    # جلب جميع الإشعارات الخاصة بالمستخدم الحالي، مرتبة من الأحدث للأقدم
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'notifications/owner_notifications.html',
        {
            'notifications': notifications
        }
    )
    
  

@login_required
def tenant_notifications(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'tenant':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Kiracı İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # إذا أرسل المستخدم طلب POST للتأكيد على قراءة إشعار
    if request.method == 'POST':
        notif_id = request.POST.get('notif_id')
        if notif_id:
            notif = get_object_or_404(Notification, id=notif_id, user=request.user)
            notif.is_read = True
            notif.save()
        # بعد تغيير حالة الإشعار نعيد توجيه المستخدم للصفحة نفسها
        return redirect('tenant_notifications')
    # جلب جميع الإشعارات الخاصة بالمستخدم الحالي، مرتبة من الأحدث للأقدم
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'notifications/tenant_notifications.html',
        {
            'notifications': notifications
        }
    )
    
