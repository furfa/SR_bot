import logging

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from celery import current_app

from . import models

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.BotUser, dispatch_uid="change sex")
def on_post_save_user(sender, **kwargs):
    instance = kwargs['instance']
    logger.info(f"user saved {instance}")
    if instance.sex == models.BotUser.SexChoices.GIRL and not hasattr(instance, 'girl_profile'):
        models.GirlProfile.objects.create(user=instance)

    if instance.sex == models.BotUser.SexChoices.MALE and hasattr(instance, 'girl_profile'):
        instance.girl_profile.delete()


# @receiver(post_save, sender=models.GirlProfile, dispatch_uid="auto_create_first_form")
# def on_post_save_girl_profile(sender, **kwargs):
#     instance = kwargs['instance']
#     models.GirlForm.objects.create(profile=instance)

