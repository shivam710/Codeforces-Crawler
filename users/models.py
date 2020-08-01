from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.contrib.auth.models import User

class CustomUser(AbstractUser):
    handle = models.CharField(max_length=16)

