from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from listings.models import TinyHouse


# Create your models here.

STATUS_CHOICES = [
    ('beklemede', 'beklemede'),
    ('onayli',   'onayli'),
    ('iptal',    'iptal'),
]

class Reservation(models.Model):
    tiny_house = models.ForeignKey(
        TinyHouse,
        on_delete=models.CASCADE,
    )  #  NOT NULL
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )  #  NOT NULL
    start_date = models.DateField()  # Rezervasyon Başlangıç Tarihi, NOT NULL
    end_date = models.DateField()    # Rezervasyon Bitiş Tarihi, NOT NULL
    reservation_status = models.CharField(
    max_length=10,
    choices=STATUS_CHOICES,
    default='beklemede',
    )
   

    created_at = models.DateTimeField(auto_now_add=True)  # Oluşturulma Tarihi, DEFAULT CURRENT_TIMESTAMP, NOT NULL



    def __str__(self):
        return f"Reservation #{self.id} for House {self.tiny_house_id}"