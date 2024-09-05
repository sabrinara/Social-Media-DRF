from django.db import models
from django.contrib.auth.models import User
from .constants import GENDER_TYPE, DIVISION_TYPE
# Create your models here.

class UserDetails(models.Model):
    user = models.OneToOneField(
        User, related_name='AbstractUserDetails', on_delete=models.CASCADE)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='accounts/media/profile_pics/')
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_TYPE)
    division = models.CharField(max_length=100, null=True, blank=True, choices=DIVISION_TYPE)
    district = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return str(self.user.email)
