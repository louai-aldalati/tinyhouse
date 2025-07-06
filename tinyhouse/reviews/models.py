from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from reservations.models import Reservation

# Create your models here.

class Review(models.Model):
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
    )  #  NOT NULL
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # Puan (1-5), CHECK (rating >= 1 AND rating <= 5), NOT NULL
    comment = models.TextField(blank=True, null=True)  # Yorum Metni
    reply = models.TextField(blank=True, null=True)  # cevap Metni 
    is_active = models.BooleanField(default=True)  # Yorum Aktiflik Durumu, NOT NULL
    created_at = models.DateTimeField(auto_now_add=True)  # Oluşturulma Tarihi, DEFAULT CURRENT_TIMESTAMP, NOT NULL


    def __str__(self):
        return f"Review #{self.id} – Rating: {self.rating}"
