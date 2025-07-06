from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Profile(models.Model):
    """
    Profile modeli, varsayılan User modeline birebir ilişkiyle ek alanlar sağlar.
    role: Kullanıcı rolü (admin , Kiracı veya Ev Sahibi)
    phone_number: İletişim telefonu
    address: Adres bilgisi
    """
    ROLE_CHOICES = [
        ('tenant', 'Kiraci'),
        ('owner',  'Ev Sahibi'),
        ('admin',  'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='tenant',
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profil"

# Signal: Yeni User oluşturulduğunda otomatik olarak Profile oluşturur ve kaydeder\@
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
