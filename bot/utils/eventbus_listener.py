import asyncio
from api.eventbus import Event
from loguru import logger
import json


class EventbusListener(object):
    def __init__(self, bot):
        self.bot = bot
        self.callbacks = {}

    async def notify(self, key, body):
        for callback in self.callbacks.get(key, []):
            return await callback(bot=self.bot, body=json.loads(body))

    def add_handler(self, key, callback):
        self.callbacks[key] = self.callbacks.get(key, [])
        self.callbacks[key].append(callback)
        return callback

    async def pooling_iteration(self):
        try:
            events = await Event.get()
        except Exception as e:
            logger.error("error while getting event from event bus")
            events = []

        for event in events:
            try:
                body = event.body.replace("'", '"')
                status = await self.notify(key=event.event_type, body=event.body)
                # logger.info(f'{status=}')
                if status:
                    logger.info(f'deleting event with {event.pk=}')
                    await Event.delete(event.pk)
            except Exception as e:
                logger.exception("Error in pooling!!!")
                logger.info(f'deleting event with {event.pk=}')
                try:
                    await Event.delete(event.pk)
                except Exception as e:
                    logger.exception("can't delete event second try")
                await asyncio.sleep(3)
            await asyncio.sleep(5)
