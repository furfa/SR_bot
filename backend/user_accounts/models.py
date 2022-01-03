from __future__ import annotations

import logging

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from base.classes import DjangoModelAutoStr

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
        default=None
    )

    class Meta:
        verbose_name = 'Пользователя сервиса'
        verbose_name_plural = 'Пользователи сервиса'


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
        CLIENT            = "CLIENT", "Клиентская"
        TECHNICAL         = "TECHNICAL", "Техническая"
        PERSONAL_MANAGER  = "PERSONAL_MANAGER", "Персональный менеджер"
        PARTNERSHIP       = "PARTNERSHIP", "Сотрудничество"

    type = models.CharField(
        verbose_name="Тип",
        choices=TypeChoices.choices,
        default=TypeChoices.CLIENT,
        max_length=32
    )
