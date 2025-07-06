from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.db import IntegrityError
from .models import Profile
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

# Create your views here.



def index(request):
    
    return render(request, 'accounts/index.html')



def sign_in(request):
    # استخرج قيمة الدور سواء من GET أو POST
    role = request.POST.get('role') or request.GET.get('role')

    # إذا الدور غير صالح، نعيد طلب GET مع خطأ
    if role not in dict(Profile.ROLE_CHOICES):
        return HttpResponseBadRequest("Geçersiz Rol Geçti")

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # تأكد أن دور المستخدم يطابق ما اختار
            if hasattr(user, 'profile') and user.profile.role == role:
                login(request, user)
                # إعادة التوجيه حسب الدور
                if role == 'tenant':
                    return redirect('tenant_dashboard')
                elif role == 'owner':
                    return redirect('owner_dashboard')
                elif role == 'admin':
                    return redirect('admin_dashboard')
            else:
                error = "Kullanıcı Rolü Seçimi İle Uyuşmuyor."
        else:
            error = "Kullanıcı Adı Veya Şifre Hatalı."
        # إذا فشل، أعد عرض القالب مع رسالة الخطأ
        return render(request, 'accounts/sign_in.html', {'error': error})
    
    # عند GET، فقط اعرض القالب مع الدالة GET لالتقاط role في الحقل المخفي
    return render(request, 'accounts/sign_in.html')



def sign_up(request):
    errors = []
    form_data = {}

    if request.method == 'POST':
        # جمع البيانات
        role         = request.POST.get('rol')
        username     = request.POST.get('username', '').strip()
        email        = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address      = request.POST.get('address', '').strip()
        pwd1         = request.POST.get('password1')
        pwd2         = request.POST.get('password2')

        # حفظ البيانات لإعادة العرض في حال الخطأ
        form_data = {
            'rol': role,
            'username': username,
            'email': email,
            'phone_number': phone_number,
            'address': address,
        }

        # تحقق من الحقول
        if role not in dict(Profile.ROLE_CHOICES):
            errors.append("Rol geçersiz.")
        if not username:
            errors.append("Kullanıcı adı gerekli.")
        if not email:
            errors.append("E-posta gerekli.")
        if not pwd1 or not pwd2:
            errors.append("Her iki parola da gerekli.")
        elif pwd1 != pwd2:
            errors.append("Parolalar eşleşmiyor.")
        

        # التحقق من تكرار username/email
        if User.objects.filter(username=username).exists():
            errors.append("Bu kullanıcı adı zaten alınmış.")
        if User.objects.filter(email=email).exists():
            errors.append("Bu e-posta zaten kayıtlı.")

        # إذا لا أخطاء، ننشئ المستخدم
        if not errors:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=pwd1
                )
                # تأكد من إنشاء Profile عبر الإشارة موجود أو أنشئه يدوياً
                profile = user.profile
                profile.role         = role
                profile.phone_number = phone_number or None
                profile.address      = address or None
                profile.save()

                # عرض رسالة نجاح التسجيل
                messages.success(request, "Kayıt başarılı! Lütfen giriş yapın.")

                # إعادة التوجيه إلى صفحة تسجيل الدخول مثلاً
                return redirect('index')

            except IntegrityError:
                errors.append("Hesap Oluşturma Hatası. Tekrar Deneyin")
    
    # GET أو في حال وجود أخطاء: عرض القالب مع الأخطاء والبيانات المعبأة
    return render(request, 'accounts/sign_up.html', {
        'errors': errors,
        'form_data': form_data
    })
    



def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Kontrol: E-posta adresi girilmiş mi?
        if not email:
            messages.error(request, 'Lütfen e-posta adresinizi girin.')
            return render(request, 'accounts/reset_password.html', {'email': email})

        # Kullanıcının varlığını kontrol et
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Bu e-posta kayıtlı değil.')
            return render(request, 'accounts/reset_password.html', {'email': email})

        # UID ve token oluştur
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Şifre sıfırlama bağlantısını oluştur
        reset_link = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={
                'uidb64': uidb64,
                'token': token
            })
        )

        # E-posta içeriği
        subject = 'Şifre Sıfırlama Bağlantısı'
        message = (
            f'Merhaba {user.username},\n\n'
            f'Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın:\n{reset_link}\n\n'
            'Bu isteği siz yapmadıysanız, bu mesajı göz ardı edebilirsiniz.'
        )

        # E-postayı gönder
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        messages.success(request, 'Şifre sıfırlama bağlantısı e-posta adresinize gönderildi.')
        return redirect('reset_password')

    # GET isteğinde formu render et
    return render(request, 'accounts/reset_password.html')



@login_required
def profile(request):
    user = request.user
    profile = user.profile
    errors = []
    success = None
    form_data = {}

    if request.method == 'POST':
        # اجمع البيانات من النموذج
        username     = request.POST.get('username', '').strip()
        email        = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address      = request.POST.get('address', '').strip()

        # احتفظ بالقيم لإعادة العرض في حال الخطأ
        form_data = {
            'username': username,
            'email': email,
            'phone_number': phone_number,
            'address': address,
        }

        # تحقق من الحقول
        if not username:
            errors.append("Kullanıcı adı boş olamaz.")
        if not email:
            errors.append("E-posta boş olamaz.")

        # تحقق من عدم تكرار username
        if username != user.username and User.objects.filter(username=username).exists():
            errors.append("Bu kullanıcı adı zaten kullanılıyor.")
        # تحقق من عدم تكرار email
        if email != user.email and User.objects.filter(email=email).exists():
            errors.append("Bu e-posta başka bir hesapta kullanılıyor.")

        # إذا لا أخطاء، نفذ التحديث
        if not errors:
            try:
                user.username = username
                user.email = email
                user.save()

                profile.phone_number = phone_number or None
                profile.address = address or None
                profile.save()

                success = "Bilgiler başarıyla güncellendi."
                # نظف form_data حتى يعرض النموذج القيم الجديدة من user/profile
                form_data = {}

            except IntegrityError:
                errors.append("Güncelleme sırasında hata oluştu. Lütfen tekrar deneyin.")

    # GET أو بعد POST (ناجحة أو بها أخطاء)
    return render(request, 'accounts/profile.html', {
        'user': user,
        'profile': profile,
        'errors': errors,
        'success': success,
        'form_data': form_data,
    })


@login_required
def admin_user_management(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'admin':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Yönetici İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    # إذا جاء POST، ننفّذ العملية المطلوبة
    if request.method == 'POST':
        action = request.POST.get('action')
        pk     = request.POST.get('pk')
        profile = get_object_or_404(Profile, pk=pk)
        user = profile.user

        if action == 'delete':
            user.delete()
        elif action == 'deactivate':
            user.is_active = False
            user.save()
        # بعد العملية نعيد التوجيه لنفس الصفحة لتحديث القائمة
        return redirect('admin_user_management')

    # أما GET فنعرض القائمة
    profiles = Profile.objects.filter(role__in=['tenant', 'owner']).select_related('user')
    return render(request, 'accounts/admin_user_management.html', {'profiles': profiles})


@login_required
def admin_user_add(request):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'admin':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Yönetici İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    errors = []
    form_data = {}

    if request.method == 'POST':
        # جمع البيانات
        role         = request.POST.get('rol')
        username     = request.POST.get('username', '').strip()
        email        = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address      = request.POST.get('address', '').strip()
        pwd1         = request.POST.get('password1')
        pwd2         = request.POST.get('password2')

        # حفظ البيانات لإعادة العرض في حال الخطأ
        form_data = {
            'rol': role,
            'username': username,
            'email': email,
            'phone_number': phone_number,
            'address': address,
        }

        # تحقق من الحقول
        if role not in dict(Profile.ROLE_CHOICES):
            errors.append("Rol geçersiz.")
        if not username:
            errors.append("Kullanıcı adı gerekli.")
        if not email:
            errors.append("E-posta gerekli.")
        if not pwd1 or not pwd2:
            errors.append("Her iki parola da gerekli.")
        elif pwd1 != pwd2:
            errors.append("Parolalar eşleşmiyor.")
        

        # التحقق من تكرار username/email
        if User.objects.filter(username=username).exists():
            errors.append("Bu kullanıcı adı zaten alınmış.")
        if User.objects.filter(email=email).exists():
            errors.append("Bu e-posta zaten kayıtlı.")

        # إذا لا أخطاء، ننشئ المستخدم
        if not errors:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=pwd1
                )
                # تأكد من إنشاء Profile عبر الإشارة موجود أو أنشئه يدوياً
                profile = user.profile
                profile.role         = role
                profile.phone_number = phone_number or None
                profile.address      = address or None
                profile.save()


                # عرض رسالة نجاح التسجيل
                messages.success(request, "Kullanıcı Başarıyla Eklendi.")

                # إعادة التوجيه إلى صفحة تسجيل الدخول مثلاً
                return redirect('/admin_user_add')

                

            except IntegrityError:
                errors.append("Hesap Oluşturma Hatası. Tekrar Deneyin")
    
    # GET أو في حال وجود أخطاء: عرض القالب مع الأخطاء والبيانات المعبأة
    return render(request, 'accounts/admin_user_add.html', {
        'errors': errors,
        'form_data': form_data
    })

def admin_user_edit(request, pk):
    # تحقق من دور المستخدم
    if request.user.profile.role != 'admin':
        messages.error(request, "Girmek İstediğiniz Sayfa Yalnızca Yönetici İçindir.")
        return redirect('/')  # إعادة توجيه إلى الصفحة الرئيسية
    
    profile = get_object_or_404(Profile, pk=pk)
    user = profile.user
    errors = []
    success = None

    if request.method == 'POST':
        # جلب البيانات من الفورم
        username     = request.POST.get('username', '').strip()
        email        = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address      = request.POST.get('address', '').strip()
        role         = request.POST.get('rol', '').strip()
        is_active    = request.POST.get('is_active', 'False')

        # تحقق بسيط
        if not username:
            errors.append('Kullanıcı adı boş olamaz.')
        if not email:
            errors.append('E-posta boş olamaz.')
        if role not in dict(Profile.ROLE_CHOICES):
            errors.append('Geçersiz rol seçimi.')

        if not errors:
            # حفظ التغييرات
            user.username         = username
            user.email            = email
            user.is_active        = (is_active == 'True')
            profile.phone_number  = phone_number
            profile.address       = address
            profile.role          = role

            user.save()
            profile.save()
            success = 'Profil başarıyla güncellendi.'
            form_data = {}
        else:
            # إبقاء القيم المدخلة حال حدوث خطأ
            form_data = {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'rol': role,
                'is_active': is_active,
            }
    else:
        form_data = {}

    context = {
        'profile': profile,
        'user': user,
        'errors': errors,
        'success': success,
        'form_data': form_data,
    }
    return render(request, 'accounts/admin_user_edit.html', context)

