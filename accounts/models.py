
# Create your models here.
from django.conf import settings
from django.db import models


class Donor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=60, blank=True)
    state = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
class CenterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='center_profile')
    center = models.OneToOneField('centers.CareCenter', on_delete=models.CASCADE,
                                related_name='owner')
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.center.name
    