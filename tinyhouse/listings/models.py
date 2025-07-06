from django.db import models
from django.conf import settings
# Create your models here.


STATUS_CHOICES = [
    ('beklemede', 'beklemede'),
    ('onayli',   'onayli'),
    ('iptal',    'iptal'),
]

class TinyHouse(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='houses_owned',   # اسم عكسي مميّز للـ owner
    )  #  NOT NULL
    title = models.CharField(max_length=255)  # İlan Başlığı, NOT NULL
    location = models.CharField(max_length=255)  # مثال: "Antalya, Türkiye"
    start_date = models.DateField() 
    end_date   = models.DateField()
    max_tenant = models.PositiveIntegerField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)  # Gece Başına Fiyat, NOT NULL  
    description = models.TextField(blank=True, null=True)  # Ev Açıklaması
    is_active = models.BooleanField(default=True)  # İlan Aktiflik Durumu, NOT NULL

    tiny_house_status     =  models.CharField(max_length=10,
                           choices=STATUS_CHOICES,
                           default='beklemede',)

    created_at = models.DateTimeField(auto_now_add=True)  # Oluşturulma Tarihi, DEFAULT CURRENT_TIMESTAMP, NOT NULL
    


    def __str__(self):
        return f"{self.title} (#{self.id})"


class TinyHouseImage(models.Model):
    tiny_house = models.ForeignKey(TinyHouse,  on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tinyhouse_photos/%Y/%m/%d',blank=True, null=True)
    


