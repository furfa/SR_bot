from rest_framework import serializers

from . import models


class PaymentScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentScreenshot
        fields = (
            "id",
            "status",
            "user",
            "amount",
            "screenshot"
        )
