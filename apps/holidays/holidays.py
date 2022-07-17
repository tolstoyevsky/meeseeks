"""Module containing Holidays application classes. """

import io
import json
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

    _custom_holidays = ''
    _year_of_holiday = ''
    _days = []
    _holidays_names = {}
    _now = None
    _future_date = None
    _number_of_days_in_advance = None
    _xml_file = None

    app_name = 'holidays'

    def __init__(self, **kwargs):
        super().__init__()

        self.scheduler = AsyncIOScheduler(settings.SCHEDULER_SETTINGS)

        self.__dict__.update(kwargs)

    @staticmethod
    async def _get_xml_file(year):
        """Return object of bytes xml file. """

        api_url = urljoin(settings.XML_CALENDAR_HOST, f'/data/ru/{year}/calendar.xml')
        async with ClientSession() as session:
            response_raw = await session.get(api_url)
            response_raw.raise_for_status()
            file_bytes = response_raw.content._buffer[0]  # pylint: disable=protected-access

        return io.BytesIO(file_bytes)

    async def _send_notification(self, response):
        """Send notification about holiday in Rocket.Chat. """

        if response:
            if self._number_of_days_in_advance == 7:
                response_msg = f'Через неделю **"{response["title"]}"**: '
                if response['start'] == response['end']:
                    response_msg += f'не работаем **{response["start"]}**'
                else:
                    response_msg += (
                        f'не работаем с **{response["start"]}** по **{response["end"]}**'
                    )

                return await self._restapi.write_msg(response_msg, 'GENERAL')

            return await self._restapi.write_msg('Приятных выходных :tada:', 'GENERAL')

        return None

    async def _get_custom_holiday_response(self):
        """Check custom holidays and return response. """

        response = {}
        if settings.CUSTOM_HOLIDAYS:
            self._custom_holidays = json.loads(settings.CUSTOM_HOLIDAYS)
            advance_date = (self._now + timedelta(days=self._number_of_days_in_advance))

            for title, custom_days in self._custom_holidays.items():
                start_date = datetime.strptime(
                    f'{self._future_date.year}.{custom_days[0]}', '%Y.%m.%d'
                ).date()
                if advance_date.month == start_date.month and advance_date.day == start_date.day:
                    response.update({'title': title})
                    response.update({'start': start_date})

                    if len(custom_days) > 1:
                        end_date = datetime.strptime(
                            f'{self._future_date.year}.{custom_days[1]}', '%Y.%m.%d').date()
                    else:
                        end_date = start_date
                    response.update({'end': end_date})

        return response

    async def _get_start_date_of_holiday(self):
        """Return start date of holidays. """

        response = {}
        prev_date = None

        for day in self._days:
            if day['type'] == '1':
                holiday_date = datetime.strptime(
                    f'{self._future_date.year}.{day["day"]}', '%Y.%m.%d'
                ).date()

                if (self._future_date.month == holiday_date.month and
                        self._future_date.day == holiday_date.day):
                    if prev_date and (holiday_date - prev_date).days == 1:
                        break

                    holiday_title = self._holidays_names.get(day.get('holiday_id'))
                    if holiday_title:
                        response.update({'title': holiday_title})
                    response.update({'start': holiday_date})
                    response.update({'end': holiday_date})
                    prev_date = holiday_date
                    break

                prev_date = holiday_date

        return prev_date, response

    async def _get_end_date_of_holiday(self, prev_date, response):
        """Return end date of holiday. """

        if response:
            for day in self._days:
                if 'holiday_id' in day or 'from' in day:
                    date = datetime.strptime(
                        f'{self._future_date.year}.{day["day"]}', '%Y.%m.%d'
                    ).date()
                    if prev_date > date:
                        continue

                    if prev_date and (date - prev_date).days == 1:
                        holiday_title = self._holidays_names.get(day.get('holiday_id'))
                        if holiday_title:
                            response.update({'title': holiday_title})
                        response.update({'end': date})
                        prev_date = date

        return response

    async def _get_holiday_response(self):
        """Check holidays from xml file and return response. """

        root = ElementTree.parse(self._xml_file).getroot()
        for holiday_raw in root.findall('holidays/holiday'):
            self._holidays_names.update({
                holiday_raw.attrib['id']: holiday_raw.attrib['title']
            })

        for day_raw in root.findall('days/day'):
            self._days.append({
                'day': day_raw.attrib['d'],
                'type': day_raw.attrib['t'],
                'holiday_id': day_raw.attrib.get('h'),
                'from': day_raw.attrib.get('f'),
            })

        prev_date, response = await self._get_start_date_of_holiday()
        response = await self._get_end_date_of_holiday(prev_date, response)

        return response

    async def _check_holidays(self, number_of_days_in_advance):
        """Check custom holidays and holidays from xml file and send response in Rocket.Chat. """

        self._now = datetime.today()
        self._number_of_days_in_advance = number_of_days_in_advance
        self._future_date = self._now + timedelta(days=self._number_of_days_in_advance)
        self._xml_file = await self._get_xml_file(self._future_date.year)

        await self._send_notification(await self._get_custom_holiday_response())

        await self._send_notification(await self._get_holiday_response())

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

        self.scheduler.add_job(
            self._check_holidays,
            id='check_week_before',
            kwargs={'number_of_days_in_advance': 7},
            coalesce=False,
            max_instances=1,
            trigger='cron',
            **self._parse_crontab(settings.HOLIDAYS_CRONTAB_WEEK_BEFORE),
        )

        self.scheduler.add_job(
            self._check_holidays,
            id='check_day_before',
            kwargs={'number_of_days_in_advance': 1},
            coalesce=False,
            max_instances=1,
            trigger='cron',
            **self._parse_crontab(settings.HOLIDAYS_CRONTAB_DAY_BEFORE),
        )

        self.scheduler.start()

    async def setup(self):
        """Trying to log in Meeseeks to Rocket.Chat server. """

        await self._start_scheduler()
        LOGGER.info('%s: Started', self.__class__.__name__)
