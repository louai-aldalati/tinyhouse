from django.db import models
from reservations.models import Reservation
# Create your models here.


STATUS_CHOICES = [
    ('beklemede', 'beklemede'),
    ('tamamlandi',   'tamamlandi'),
    ('iptal',    'iptal'),
]

class Payment(models.Model):
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
    )  #  NOT NULL
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )  # Ödeme Tutarı, NOT NULL
    payment_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
       default='beklemede',
    )  #  NOT NULL
    payment_date = models.DateTimeField(blank=True, null=True)  # Ödeme Tarihi
    payment_method = models.CharField(
        max_length=50 ,blank=True, null=True
    )  
    transaction_id    = models.CharField(max_length=100, blank=True, null=True, unique=True)
    gateway_response  = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f"Payment #{self.id} ({self.payment_status})"
