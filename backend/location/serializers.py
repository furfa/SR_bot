from rest_framework import serializers
from . import models


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = (
            "id",
            "name",
        )


class CountrySerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)

    class Meta:
        model = models.Country
        fields = (
            "id",
            "name",
            "cities"
        )
