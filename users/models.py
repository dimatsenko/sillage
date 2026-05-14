from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model for Sillage store.
    Inherits from AbstractUser to allow easy extension in the future.
    """
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефону")

    def __str__(self):
        return self.username
