from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    money = models.FloatField(default=10.00)
    def __str__(self):
        return self.username
