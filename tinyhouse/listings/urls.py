from django.urls import path
from . import views

urlpatterns=[
    path('admin_listing_management',views.admin_listing_management, name='admin_listing_management'),
    path('admin_listing_add',views.admin_listing_add, name='admin_listing_add'),
    path('owner_listing_management/',views.owner_listing_management, name='owner_listing_management'),
    path('owner_listing_edit/<int:pk>/',views.owner_listing_edit, name='owner_listing_edit'),
    path('tenant_listing_details/<int:pk>/',views.tenant_listing_details, name='tenant_listing_details'),
]
