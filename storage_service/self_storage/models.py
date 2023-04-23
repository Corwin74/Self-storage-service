import datetime
import uuid

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from random import randint


def now_plus_30():
    """Прибавляет к текущей дате 30 дней."""
    return datetime.datetime.now() + datetime.timedelta(days=30)


class Warehouse(models.Model):
    name = models.CharField(
        'Название склада',
        max_length=30,
        help_text='Склад на Арбате'
    )

    address = models.TextField(
        'Адрес склада',
        help_text='г.Москва, ул.Подольских курсантов, д.5'
    )

    number_of_floors = models.IntegerField(
        'Количество этажей',
        help_text='3'
    )

    boxes_per_floor = models.IntegerField(
        'Количество боксов на этаже',
        help_text='3')

    def __str__(self):
        return self.name


class Size(models.Model):
    BOX_SHELVE = 0.5
    BOX_BALCONY = 1.5
    BOX_STOREROOM = 3
    BOX_ROOM = 6
    BOX_GARAGE = 9
    BOX_ATTIC = 18
    BOX_CHOICES = [
        (BOX_SHELVE, ("Полка")),
        (BOX_BALCONY, ("Балкон")),
        (BOX_STOREROOM, ("Кладовка")),
        (BOX_ROOM, ("Комната")),
        (BOX_GARAGE, ("Гараж")),
        (BOX_ATTIC, ("Чердак")),
    ]
    name = models.FloatField(
        'Наименование размера',
        choices=BOX_CHOICES,
    )

    def __str__(self):
        return self.get_name_display()


class Box(models.Model):
    name = models.CharField(
        'Название бокса',
        max_length=20,
        help_text='Бокс №1'
    )

    warehouse = models.ForeignKey(
        Warehouse,
        verbose_name='Склад',
        related_name='boxes',
        on_delete=models.CASCADE
    )

    size = models.ForeignKey(
        Size,
        verbose_name='Объём бокса',
        related_name='boxes',
        on_delete=models.PROTECT
    )

    floor = models.IntegerField(
        'Номер этажа',
        help_text='3')

    occupied = models.BooleanField(
        'Занят',
        db_index=True,
        default=False
    )

    cost = models.PositiveSmallIntegerField(
        'Стоимость',
        default=3000
    )

    customer = models.ForeignKey(
        get_user_model(),
        verbose_name='Кем занят',
        related_name='boxes',
        on_delete=models.SET_NULL,
        null=True,
        blank=True)

    end_date = models.DateField(
        'Дата окончания хранения',
        default=timezone.now,
        db_index=True
    )

    def __str__(self):
        return f'{self.warehouse.name}-{self.name}'


class Order(models.Model):
    name = models.CharField(
        'Название заказа',
        max_length=20,
        db_index=True,
        default='Заказ без номера'
    )

    customer = models.ForeignKey(
        get_user_model(),
        verbose_name='Заказчик',
        related_name='orders',
        on_delete=models.CASCADE,
        db_index=True
    )

    box = models.ForeignKey(
        Box,
        verbose_name='Бокс',
        related_name='orders',
        on_delete=models.PROTECT
    )

    price = models.IntegerField(
        'Стоимость заказа',
        default=0,
        db_index=True,
    )

    payment_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name='Идентификатор платежа'
    )

    stripe_payment_id = models.CharField(
        max_length=100,
        blank=True,
        default='',
        editable=False,
        verbose_name='Идентификатор платежа stripe'
    )

    paid = models.BooleanField(
        'Оплачен',
        db_index=True,
        default=False
    )

    end_date = models.DateField(
        'Дата окончания хранения',
        default=now_plus_30,
        db_index=True
    )

    created_at = models.DateTimeField(
        'Дата создания заказа',
        default=timezone.now,
        db_index=True)

    def __str__(self):
        return f'{self.customer}, {self.box.warehouse}'
