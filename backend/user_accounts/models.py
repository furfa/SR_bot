from __future__ import annotations

import logging

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from base.classes import DjangoModelAutoStr
from location.models import Country, City

logger = logging.getLogger(__name__)


class BotUser(DjangoModelAutoStr, models.Model):
    id = models.IntegerField(verbose_name="tg_id", primary_key=True)
    has_access = models.BooleanField(verbose_name="Есть доступ к боту", default=True)
    is_admin = models.BooleanField(verbose_name="Является ли админом", default=False)
    language = models.CharField(verbose_name="Локаль пользователя", choices=settings.LANGUAGES, default=settings.LANGUAGES[0][0], max_length=50)

    class SexChoices(models.TextChoices):
        GIRL    = "GIRL", "Женщина"
        MALE    = "MALE", "Мужчина"
        UNKNOWN = "UNKNOWN", "Не установлен"

    sex = models.CharField(
        verbose_name="Роль",
        choices=SexChoices.choices,
        default=SexChoices.UNKNOWN,
        max_length=32
    )

    last_usage_at = models.DateTimeField(auto_now_add=True, verbose_name="Последний вход")

    balance = models.DecimalField(verbose_name="Бонусный баланс", default=0, max_digits=17, decimal_places=10)

    inviting_user = models.ForeignKey(
        "self",
        verbose_name="Пригласивший пользователь",
        related_name="referrals",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователя сервиса'
        verbose_name_plural = 'Пользователи сервиса'


class AbstractProfile(models.Model):
    has_vip_status = models.BooleanField(default=False, verbose_name="Есть вип статус")

    class Meta:
        abstract = True


class GirlProfile(DjangoModelAutoStr, AbstractProfile):
    has_top_status = models.BooleanField(default=False, verbose_name="Есть топ статус")
    user = models.OneToOneField(BotUser, related_name="girl_profile", null=True, blank=True, on_delete=models.CASCADE)


class GirlForm(DjangoModelAutoStr, models.Model):
    profile = models.ForeignKey(GirlProfile, on_delete=models.SET_NULL, null=True, related_name="forms")

    class StatusChoices(models.TextChoices):
        CREATED   = "CREATED", "Создан"
        FILLED    = "FILLED", "Заполнен"
        CONFIRMED = "CONFIRMED", "Подтвержден"
        REJECTED  = "REJECTED", "Отклонен"
        DELETED   = "DELETED", "Удален"

    status = models.CharField(max_length=32, choices=StatusChoices.choices, default=StatusChoices.CREATED)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name="countries", blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)

    first_name = models.CharField(max_length=64, default=None, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    weight = models.PositiveIntegerField(null=True, blank=True)
    body_params = models.CharField(max_length=64, null=True, blank=True)
    nationality = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name="nationalities", blank=True)


class GirlFormPhoto(DjangoModelAutoStr, models.Model):
    is_approve = models.BooleanField(default=False, verbose_name="Для подтверждения")
    photo = models.ImageField(upload_to="girl_photo/", verbose_name="Фото")
    form = models.ForeignKey(GirlForm, on_delete=models.CASCADE, verbose_name="Форма", related_name="photos")


class UserSupportQuestion(DjangoModelAutoStr, models.Model):
    user = models.ForeignKey(BotUser, related_name="questions", verbose_name="Пользователь", on_delete=models.CASCADE)

    question_body = models.TextField(verbose_name="Вопрос", default="", blank=True)
    answer_body   = models.TextField(verbose_name="Ответ", default="", blank=True)

    class StatusChoices(models.TextChoices):
        CREATED  = "CREATED", "Создан"
        ANSWERED = "ANSWERED", "Отвечен"

    status = models.CharField(
        verbose_name="Статус",
        choices=StatusChoices.choices,
        default=StatusChoices.CREATED,
        max_length=32
    )

    class TypeChoices(models.TextChoices):
        CLIENT           = "CLIENT", "Клиентская"
        TECHNICAL        = "TECHNICAL", "Техническая"
        PERSONAL_MANAGER = "PERSONAL_MANAGER", "Персональный менеджер"
        PARTNERSHIP      = "PARTNERSHIP", "Сотрудничество"

    type = models.CharField(
        verbose_name="Тип",
        choices=TypeChoices.choices,
        default=TypeChoices.CLIENT,
        max_length=32
    )
