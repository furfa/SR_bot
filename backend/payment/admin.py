from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models


@admin.register(models.PaymentScreenshot)
class PaymentScreenshotAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "status",
        "user",
        "amount",
        "display_screenshot"
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "user__id__exact",
    )

    @admin.display(description='Скриншот')
    def display_screenshot(self, obj):
        if obj.screenshot:
            return mark_safe(f'<img src="{obj.screenshot.url}" height="200"')
        else:
            return mark_safe(f'<img src="" height="200"')