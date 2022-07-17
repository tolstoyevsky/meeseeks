"""Module containing Holidays application classes. """

import gzip
import io
from datetime import datetime, timedelta
from urllib.parse import urljoin
from xml.etree import ElementTree

from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apps.holidays import settings
from meeseeks import MeeseeksCore
from meeseeks.logger import LOGGER


class Holidays(MeeseeksCore):
    """Holidays application. """

    app_name: str = 'holidays'

    def __init__(self, **kwargs):
        super().__init__()

        self.scheduler = AsyncIOScheduler(settings.SCHEDULER_SETTINGS)

        self.__dict__.update(kwargs)

    @staticmethod
    async def get_xml_file(year):
        """Return object of bytes xml file. """

        api_url = urljoin(settings.XML_CALENDAR_HOST, f'/data/ru/{year}/calendar.xml.gz')
        async with ClientSession() as session:
            response_raw = await session.get(api_url)
            response_raw.raise_for_status()
            file_bytes = response_raw.content._buffer[0]  # pylint: disable=protected-access

        return io.BytesIO(file_bytes)

    @staticmethod
    def get_holiday_year(now):
        """Return year of future holiday. """

        new_year_soon = (now + timedelta(7)).year == now.year + 1
        if new_year_soon:
            return now.year + 1

        return now.year

    async def send_notification(self, response):
        """Send notification about holidays in Rocket.Chat. """

        response_msg = f'Через неделю **"{response["title"]}"**: '

        if response['start'] == response['end']:
            response_msg += f'не работаем **{response["start"]}**'
        else:
            response_msg += f'не работаем с **{response["start"]}** по **{response["end"]}**'

        return await self._restapi.write_msg(response_msg, 'GENERAL')

    async def check_holidays(self):
        """Check holidays from xml file and notify in chat. """

        now = datetime.today()
        now = datetime(2021, 12, 25)
        # now = datetime(2022, 2, 16)
        # now = datetime(2022, 2, 28)
        # now = datetime(2022, 4, 24)
        # now = datetime(2022, 6, 5)
        # now = datetime(2022, 12, 25)
        # now = datetime(2022, 10, 28)

        holiday_year = self.get_holiday_year(now)

        file = await self.get_xml_file(holiday_year)
        with gzip.GzipFile(fileobj=file) as gz_file:
            root = ElementTree.parse(gz_file).getroot()

            holidays = {
                holiday.attrib['id']: holiday.attrib['title']
                for holiday in root.findall('holidays/holiday')
            }
            days = root.findall('days/day')
            response = {}
            prev_date = None

            for day in days:
                if 'h' in day.attrib or 'f' in day.attrib:
                    date = datetime.strptime(f'{holiday_year}.{day.attrib["d"]}', '%Y.%m.%d').date()
                    if ((now + timedelta(7)).month == date.month and
                            (now + timedelta(7)).day == date.day):
                        if (prev_date and (date - timedelta(1)).month == prev_date.month and
                                (date - timedelta(1)).day == prev_date.day):
                            break

                        holiday_title = holidays.get(day.attrib.get('h'))
                        if holiday_title:
                            response.update({'title': holiday_title})

                        response.update({'start': date})
                        response.update({'end': date})
                        prev_date = date

                        break

                    prev_date = date

            if response:
                for day in days:
                    if 'h' in day.attrib or 'f' in day.attrib:
                        date = datetime.strptime(
                            f'{holiday_year}.{day.attrib["d"]}', '%Y.%m.%d'
                        ).date()
                        if prev_date > date:
                            continue

                        if ((date - timedelta(1)).month == prev_date.month and
                                (date - timedelta(1)).day == prev_date.day):
                            holiday_title = holidays.get(day.attrib.get('h'))
                            if holiday_title:
                                response.update({'title': holiday_title})
                            response.update({'end': date})
                            prev_date = date

                await self.send_notification(response)

    @staticmethod
    def parse_crontab(crontab: str) -> dict[str, str]:
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

    async def scheduler_jobs(self):
        """Wraps scheduler jobs. """

        await self.check_holidays()

    async def start_scheduler(self):
        """Starts all scheduler jobs. """

        self.scheduler.add_job(
            self.scheduler_jobs,
            id='schedule',
            coalesce=False,
            max_instances=1,
            trigger='cron',
            **self.parse_crontab(settings.HOLIDAYS_CRONTAB)
        )
        self.scheduler.start()

    async def setup(self):
        """Trying to log in Meeseeks to Rocket.Chat server. """

        await self.start_scheduler()
        LOGGER.info('%s: Started', self.__class__.__name__)
