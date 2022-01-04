from django.contrib import admin

from . import models


class CityInline(admin.TabularInline):
    """
        Инлайн для городов
    """
    model = models.City
    extra = 0


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "display_cities",
    )

    inlines = (CityInline, )

    @admin.display(description='Города')
    def display_cities(self, obj):
        return ", ".join(obj.cities.values_list("name", flat=True))
