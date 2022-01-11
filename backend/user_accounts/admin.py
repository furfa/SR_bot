import random
from attr import fields
from django.contrib import admin
from django.utils import timezone
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property
from django.urls import reverse
from django.db.models import Count, Q
from django.db.utils import ProgrammingError

from . import models


@admin.register(models.BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "has_access",
        "is_admin",
        "sex",
        "last_usage_at",
        "balance"
    )

    readonly_fields = (
        "last_usage_at",
    )


@admin.register(models.GirlProfile)
class GirlProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(models.GirlForm)
class GirlFormAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "price",
        "created_at",
        "display_user",
    )

    search_fields = (
        "profile__user__id__exact",
    )

    list_filter = (
        "status",
    )

    @admin.display(description='Пользователь')
    def display_user(self, obj):
        try:
            return obj.profile.user.id
        except Exception as e:
            return "-"


@admin.register(models.UserSupportQuestion)
class UserSupportQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "question_body",
        "answer_body",
        "status"
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "user__id__exact",
    )
