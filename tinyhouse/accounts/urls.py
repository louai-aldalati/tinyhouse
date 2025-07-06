from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

urlpatterns=[
    path('',views.index, name='index'),
    path('sign_in/',views.sign_in, name='sign_in'),
    path('sign_up/',views.sign_up, name='sign_up'),
    path('reset_password/',views.reset_password, name='reset_password'),
     #  مسار تأكيد إعادة التعيين
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm'
    ),

    #  مسار الصفحة النهائية بعد نجاح التعيين
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/reset_done.html'
        ),
        name='password_reset_complete'
    ),
    path('profile/',views.profile, name='profile'),
    path('admin_user_management/',views.admin_user_management, name='admin_user_management'),
    path('admin_user_add/',views.admin_user_add, name='admin_user_add'),
    path('admin_user_edit/<int:pk>/',views.admin_user_edit, name='admin_user_edit'),
    
]