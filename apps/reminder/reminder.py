"""Module contains Holidays application classes. """

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apps.reminder import settings
from meeseeks import MeeseeksCore
from meeseeks.logger import LOGGER


class Reminder(MeeseeksCore):
    """Reminder application. """

    app_name = 'reminder'

    def __init__(self, **kwargs):
        super().__init__()

        self.scheduler = AsyncIOScheduler(settings.SCHEDULER_SETTINGS)

        self.__dict__.update(kwargs)

    async def _send_reminder(self, text, channel):
        """Send reminder in Rocket.Chat. """

        return await self._restapi.write_msg(f'{settings.REMINDER_MESSAGE_TOPIC}{text}',
                                             channel)

    @staticmethod
    def _parse_crontab(crontab: str) -> dict[str, str]:
        """Return parsed params from given crontab string. """

        second, minute, hour, day, month, day_of_week = crontab.split()

        return {
            'second': second,
            'minute': minute,
            'hour': hour,
            'day': day,
            'month': month,
            'day_of_week': day_of_week,
        }

    async def _start_scheduler(self):
        """Starts all scheduler jobs. """

        for reminder in settings.REMINDERS_LIST:
            self.scheduler.add_job(
                self._send_reminder,
                kwargs={'text': reminder['text'], 'channel': reminder['channel']},
                coalesce=False,
                max_instances=1,
                trigger='cron',
                **self._parse_crontab(reminder['crontab']),
            )

        self.scheduler.start()

    async def setup(self):
        """Trying to log in Meeseeks to Rocket.Chat server. """

        await self._start_scheduler()
        LOGGER.info('%s: Started', self.__class__.__name__)
