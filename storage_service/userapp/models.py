from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    phone = PhoneNumberField('Номер телефона', region='RU')
    address = models.CharField('Адрес доставки', max_length=100)
    avatar = models.FileField('Фото', null=True, blank=True)

