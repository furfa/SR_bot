from __future__ import annotations
import django
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import serializers, validators
from . import models
import logging
from event_bus.utils import publish

logger = logging.getLogger(__name__)


class BotUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BotUser
        fields = (
            "id",
            "has_access",
            "language",
            "sex",
            "balance",
            "is_admin"
        )


class UserSupportQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserSupportQuestion
        fields = (
            "id",
            "user",
            "question_body",
            "answer_body",
            "status",
            "type"
        )