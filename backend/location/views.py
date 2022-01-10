from django.shortcuts import render
from rest_framework import viewsets

from . import serializers, models


class CountyViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CountrySerializer
    queryset = models.Country.objects.all()
