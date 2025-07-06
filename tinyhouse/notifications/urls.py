from django.urls import path
from . import views

urlpatterns=[
    path('admin_notifications',views.admin_notifications, name='admin_notifications'),
    path('owner_notifications',views.owner_notifications, name='owner_notifications'),
    path('tenant_notifications/',views.tenant_notifications, name='tenant_notifications'),
]
