from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, parsers

from event_bus.utils import publish
from user_accounts.models import BotUser
from . import models, serializers


class PaymentScreenshotViewset(mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.UpdateModelMixin,
                               viewsets.GenericViewSet):
    serializer_class = serializers.PaymentScreenshotSerializer
    queryset = models.PaymentScreenshot.objects.all()
    parser_classes = (parsers.MultiPartParser, parsers.JSONParser)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def perform_create(self, serializer):
        obj = serializer.save()
        for admin in BotUser.objects.filter(is_admin=True):
            publish("new_payment_screenshot", {
                "admin_id": admin.id,
            })

    def perform_update(self, serializer):
        obj = serializer.save()
        publish("payment_screenshot_processed", serializers.PaymentScreenshotSerializer(obj).data)

        if obj.status == models.PaymentScreenshot.StatusChoices.APPROVED:
            obj.user.balance += obj.amount
            obj.user.save()