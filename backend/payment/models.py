from django.db import models


def get_screenshot_image_path(instance, filename):
    return '/'.join(['screenshots', str(instance.user.id), filename])


class PaymentScreenshot(models.Model):
    class StatusChoices(models.TextChoices):
        CREATED  = "CREATED", "Создан"
        APPROVED = "APPROVED", "Подтвержден"
        REJECTED = "REJECTED", "Отклонен"

    status = models.CharField(max_length=32, choices=StatusChoices.choices, default=StatusChoices.CREATED)

    user = models.ForeignKey("user_accounts.BotUser", verbose_name="Пользователь", on_delete=models.SET_NULL, null=True)

    amount = models.DecimalField(verbose_name="Сумма оплаты", default=0, max_digits=17, decimal_places=10)

    screenshot = models.ImageField(verbose_name="Скрин", upload_to=get_screenshot_image_path)