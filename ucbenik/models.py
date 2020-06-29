from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from .users.managers import CustomUserManager


# Create your models here.

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    MALE = 'M'
    FEMALE = 'F'
    SEX = (
        (MALE, 'Male'),
        (FEMALE, 'Female'))
    sex = models.CharField(max_length=1, choices=SEX)
    age = models.IntegerField(default=99)
    objects = CustomUserManager()

    def __str__(self):
        return self.first_name + " " + self.email + " " + self.sex + " " + str(self.age)

