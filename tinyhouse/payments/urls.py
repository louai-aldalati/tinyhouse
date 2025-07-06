from django.urls import path
from . import views

urlpatterns=[
    path('admin_payment_management',views.admin_payment_management, name='admin_payment_management'),
    path('owner_payment_management/',views.owner_payment_management, name='owner_payment_management'),
    path('tenant_make_payment/<int:payment_id>/',views.tenant_make_payment, name='tenant_make_payment'),
]
