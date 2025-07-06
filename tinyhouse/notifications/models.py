from django.db import models
from django.conf import settings


# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )  #  NOT NULL
    title = models.CharField(max_length=255)
    message = models.TextField()  # Bildirim Mesajı, NOT NULL
    is_read = models.BooleanField(default=False)  # Okundu Bilgisi, DEFAULT FALSE, NOT NULL
    created_at = models.DateTimeField(auto_now_add=True)  # Oluşturulma Tarihi, DEFAULT CURRENT_TIMESTAMP, NOT NULL

   

    def __str__(self):
     return f"Notification #{self.title} to User {self.user.username}"
