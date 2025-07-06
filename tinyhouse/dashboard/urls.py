from django.urls import path
from . import views

urlpatterns=[
    path('admin_dashboard/',views.admin_dashboard, name='admin_dashboard'),
    path('owner_dashboard/',views.owner_dashboard, name='owner_dashboard'),
    path('tenant_dashboard/',views.tenant_dashboard, name='tenant_dashboard'),
]