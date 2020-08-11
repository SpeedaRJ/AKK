import json

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
    is_admin = models.BooleanField(default=False)
    last_page = models.CharField(max_length=30, default='')
    chapters = models.CharField(max_length=200, default='Introduction')

    objects = CustomUserManager()

    def __str__(self):
        return self.first_name + " " + self.email + " " + self.sex + " " + str(self.age)

    def set_last_page(self, last_page):
        self.last_page = last_page
        self.save()

    def add_chapter(self, chapter):
        if chapter in self.chapters:
            return
        self.chapters += f',{chapter}'
        self.save()


class CharacterMetaData(models.Model):
    neck = models.CharField(max_length=30)
    body_color = models.CharField(max_length=30)
    height = models.CharField(max_length=5)
    body_type = models.CharField(max_length=4)
    hair_color = models.CharField(max_length=30)
    glasses = models.CharField(max_length=30)
    hair_type = models.CharField(max_length=30)

    class Meta:
        abstract = True


class CharacterDataWomen(CharacterMetaData, models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    pants_color = models.CharField(max_length=10, blank=True)
    dress_color = models.CharField(max_length=30, blank=True)
    shoes_color = models.CharField(max_length=30, blank=True)
    shirt_color = models.CharField(max_length=30, blank=True)
    wearing = models.CharField(max_length=15, blank=True)


class CharacterDataMen(CharacterMetaData, models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    beard = models.CharField(max_length=30)
    suite_color = models.CharField(max_length=30)

class Solution(models.Model):
    link = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    solved = models.BooleanField()

    def __str__(self):
        if self.solved:
            return self.user.first_name + " - " + self.link + " - " + "solved"
        return self.user.first_name + " - " + self.link + " - " + "unsolved"

    def solve(self):
        self.solved = True
        self.save()