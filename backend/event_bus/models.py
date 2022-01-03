from django.db import models

class Event(models.Model):
    """
        Событие (Todo: заменить на очередь)
    """
    body = models.TextField(verbose_name="Тело события")
    event_type = models.CharField(verbose_name="Тип события", max_length=50)