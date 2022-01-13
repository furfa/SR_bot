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
            "telegram_meta",
            "has_access",
            "language",
            "sex",
            "balance",
            "is_admin"
        )


class GirlFormPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.GirlFormPhoto
        fields = (
            "id",
            "is_approve",
            "photo",
            "form",
        )


class GirlFormSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    photos = GirlFormPhotoSerializer(many=True)

    class Meta:
        model = models.GirlForm
        fields = (
            "id",
            "status",
            "country",
            "city",
            "nationality",
            "additional_data",
            "photos",
            "user",
            "has_top_status",
            "price"
        )

    def get_user(self, obj):
        return obj.profile.user.id


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