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
    pass


@admin.register(models.GirlProfile)
class GirlProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(models.GirlForm)
class GirlFormAdmin(admin.ModelAdmin):
    pass