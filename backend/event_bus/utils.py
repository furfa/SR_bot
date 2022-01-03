import logging
from . import models
from rest_framework.renderers import JSONRenderer

logger = logging.getLogger(__name__)


def publish(event_type, body):
    logger.info(f"publishing to event bus {event_type} {body}")
    body = JSONRenderer().render(body).decode()
    models.Event.objects.create(
        event_type=event_type,
        body=body
    )