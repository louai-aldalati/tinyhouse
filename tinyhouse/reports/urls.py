from django.urls import path
from . import views

urlpatterns=[
    path('admin_statistics_and_reporting',views.admin_statistics_and_reporting, name='admin_statistics_and_reporting'),

]