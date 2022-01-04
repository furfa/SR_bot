from django.db import models

from base.classes import DjangoModelAutoStr


class Country(DjangoModelAutoStr, models.Model):
    """
        Модель страны
    """

    name = models.CharField(max_length=64, verbose_name="Название", unique=True, blank=True)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'


class City(DjangoModelAutoStr, models.Model):
    """
        Модель города
    """

    name = models.CharField(max_length=64, verbose_name="Название", unique=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
