from django.shortcuts import render
from rest_framework import serializers, mixins, viewsets
from . import models

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = (
            "pk",
            "body",
            "event_type",
        )
        read_only_fields = (
            "pk",
            "body",
            "event_type",
        )

class EventViewset(mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):

    serializer_class = EventSerializer
    queryset = models.Event.objects.all()