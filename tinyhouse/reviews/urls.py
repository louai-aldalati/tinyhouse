from django.urls import path
from . import views

urlpatterns=[
     path('admin_comments_and_ratings/',views.admin_comments_and_ratings, name='admin_comments_and_ratings'),
    path('owner_comments_and_ratings',views.owner_comments_and_ratings, name='owner_comments_and_ratings'),
    path('tenant_comments_and_ratings/',views.tenant_comments_and_ratings, name='tenant_comments_and_ratings'),
   
]