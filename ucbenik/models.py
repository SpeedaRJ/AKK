from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    MALE = 'M'
    FEMALE = 'F'
    SEX = (
        (MALE, 'Male'),
        (FEMALE, 'Female'))
    sex = models.CharField(max_length=1, choices=SEX)

    def __str__(self):
        print(self.first_name + " " + self.last_name)
