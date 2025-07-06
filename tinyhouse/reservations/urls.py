from django.urls import path
from . import views

urlpatterns=[
    path('admin_reservation_management',views.admin_reservation_management, name='admin_reservation_management'),
    path('owner_reservation_management/',views.owner_reservation_management, name='owner_reservation_management'),
    path('tenant_make_reservation/<int:house_id>/',views.tenant_make_reservation, name='tenant_make_reservation'),
    path('tenant_my_reservations/',views.tenant_my_reservations, name='tenant_my_reservations'),

]