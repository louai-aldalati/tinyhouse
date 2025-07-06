"""
URL configuration for tinyhouse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls') ,name='accounts'),
    path('dashboard/', include('dashboard.urls') ,name='dashboard'),
    path('listings/', include('listings.urls') ,name='listings'),
    path('payments/', include('payments.urls') ,name='payments'),
    path('reports/', include('reports.urls') ,name='reports'),
    path('reservations/', include('reservations.urls') ,name='reservations'),
    path('notifications/', include('notifications.urls') ,name='notifications'),
    path('reviews/', include('reviews.urls') ,name='reviews'),
]

# هذا الجزء مهمّ لخدمة ملفات الوسائط أثناء التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
