"""Module containing HappyBirthder application classes. """

import asyncio
import random
from datetime import date, datetime, timedelta
from urllib.parse import urljoin

from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apps.happy_birthder import settings
from apps.happy_birthder.mixins import CommandsMixin, DialogsMixin
from apps.happy_birthder.models import DB, User
from meeseeks import MeeseeksCore
from meeseeks.logger import LOGGER


class GifReceiver:  # pylint: disable=too-few-public-methods
    """Provide functionality for getting gifs from tenor.com. """

    def __init__(self, api_key):
        self._api_key = api_key
        self._anon_id = ''

    async def _get_anon_id(self):
        if self._anon_id:
            return self._anon_id

        url = urljoin(settings.TENOR_API_URL, f'anonid?key={self._api_key}')
        async with ClientSession(raise_for_status=True) as session:
            response_raw = await session.get(url=url)
            response = await response_raw.json()

        self._anon_id = response['anon_id']

        return self._anon_id

    @staticmethod
    def _get_random_tag():
        return random.choice(settings.TENOR_SEARCH_TERM)

    async def _get_gif_urls(self):
        tag = self._get_random_tag()
        anon_id = await self._get_anon_id()

        url = urljoin(
            settings.TENOR_API_URL,
            f'search?tag={tag}&key={self._api_key}'
            f'&limit={settings.TENOR_IMAGE_LIMIT}&anon_id={anon_id}',
        )
        async with ClientSession(raise_for_status=True) as session:
            response_raw = await session.get(url=url)
            response = await response_raw.json()

        gifs: list = response['results']
        filtered_gifs = []
        for gif in gifs:
            if gif['media'][0]['gif']['url'].split('/')[-2] in settings.TENOR_BLACKLISTED_GIF_IDS:
                continue
            filtered_gifs.append(gif['media'][0]['gif']['url'])

        return filtered_gifs

    async def get_random_gif_url(self):
        """Takes random gif from list of gifs. """

        return random.choice(await self._get_gif_urls())


class HappyBirthder(CommandsMixin, DialogsMixin, MeeseeksCore):
    """HappyBirthder application. """

    app_name = 'happy-birthder'

    def __init__(self, **kwargs):
        super().__init__()

        self.__dict__.update(kwargs)

        self.gif_receiver = GifReceiver(settings.TENOR_API_KEY)
        self.scheduler = AsyncIOScheduler(settings.SCHEDULER_SETTINGS)

    async def update_users(self):
        """Receive all user in chat and updates information in database. """

        server_users = await self._restapi.get_users()
        for user in server_users.values():
            if self.check_user_status(user):
                if not await User.get(user['_id']):
                    await User.create(user_id=user['_id'], name=user['username'])
                    await self._restapi.write_msg(settings.GREETINGS_RESPONSE, user['_id'])

                user_in_base = await User.get(user['_id'])
                if not user_in_base.fwd:
                    user_info = await self._restapi.get_user_info(user['_id'])
                    user_fwd = datetime.strptime(user_info['createdAt'][:10], '%Y-%m-%d').date()
                    await user_in_base.update(fwd=user_fwd).apply()

    async def check_dates(self):
        """Checks all birth days, requests missing and notifies about closest. """

        users = await User.query.gino.all()
        persons_without_date = ''

        for user in users:
            user_id = user.user_id
            if not self.check_user_status(await self._restapi.get_user_info(user_id)):
                continue

            name = user.name
            birth_date = user.birth_date
            fwd = user.fwd
            users_for_mailing = {
                user.user_id: user.name for user in users if user.user_id != user_id and
                self.check_user_status(await self._restapi.get_user_info(user.user_id))
            }
            today = date.today()
            tomorrow = today + timedelta(days=1)
            channel_ttl = (birth_date + timedelta(days=settings.BIRTHDAY_CHANNEL_TTL) if birth_date
                           else None)
            days_in_advance = today + timedelta(days=settings.NUMBER_OF_DAYS_IN_ADVANCE)

            if birth_date is None:
                await self._restapi.write_msg(settings.NOTIFY_SET_BIRTH_DATE, user_id)
                persons_without_date = persons_without_date + f'\n@{name}'
            elif birth_date.day == today.day and birth_date.month == today.month:
                gif_url = await self.gif_receiver.get_random_gif_url()
                phrase = random.choice(settings.CONGRATULATION_PHRASES)
                response = f'{gif_url}\nToday is birthday of @{name}!\n{phrase}'
                await self._restapi.write_msg(response, 'GENERAL')
            elif birth_date.day == tomorrow.day and birth_date.month == tomorrow.month:
                for user_id_for_mailing in users_for_mailing.keys():
                    await self._restapi.write_msg(f'@{name} is having a birthday tomorrow.',
                                                  user_id_for_mailing)
            elif (birth_date.day == days_in_advance.day and
                    birth_date.month == days_in_advance.month):
                if settings.CREATE_BIRTHDAY_CHANNELS:
                    await self._restapi.create_private_room(f'birthday-of-{name}',
                                                            list(users_for_mailing.values()))
                    await self._restapi.write_msg('@all, Let`s discuss a present',
                                                  f'birthday-of-{name}')
                for user_id_for_mailing in users_for_mailing.keys():
                    await self._restapi.write_msg(
                        f'@{name} is having a birthday on '
                        f'{date.strftime(days_in_advance, "%d.%m.%Y")}', user_id_for_mailing)
            elif (today.day == channel_ttl.day and today.month == channel_ttl.month and
                  settings.CREATE_BIRTHDAY_CHANNELS):
                await self._restapi.delete_private_room(f'birthday-of-{name}')

            if (fwd is not None and fwd.day == today.day and fwd.month == today.month and
                    (today.year - fwd.year) > 0):
                response = ('I am glad to announce that today '
                            'is the day of anniversary for some of us!')
                response += (f'\n@{name} has been a part of our team for '
                             f'{today.year - fwd.year} years!')
                await self._restapi.write_msg(response, 'GENERAL')

        if persons_without_date != '' and settings.BIRTHDAY_LOGGING_CHANNEL:
            await self._restapi.write_msg(
                settings.PERSONS_WITHOUT_BIRTHDAY_RESPONSE + persons_without_date,
                settings.BIRTHDAY_LOGGING_CHANNEL)

    async def scheduler_jobs(self):
        """Wraps scheduler jobs. """

        await self.update_users()
        await self.check_dates()

    @staticmethod
    def parse_crontab(crontab: str) -> dict[str, str]:
        """Return parsed params from given crontab string. """

        minute, hour, day, month, day_of_week = crontab.split()

        return {
            'minute': minute,
            'hour': hour,
            'day': day,
            'month': month,
            'day_of_week': day_of_week,
        }

    async def start_scheduler(self):
        """Starts all scheduler jobs. """

        self.scheduler.add_job(
            self.scheduler_jobs,
            id='check_dates',
            coalesce=False,
            max_instances=1,
            trigger='cron',
            **self.parse_crontab(settings.HB_CRONTAB)
        )
        self.scheduler.start()

    @staticmethod
    async def _connect_base():
        """Connect to PostgresSQL. """

        await DB.set_bind(
            f'postgresql://{settings.PG_USER}:{settings.PG_PASSWORD}'
            f'@{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_NAME}'
        )

    async def setup(self):
        """Trying to log in Meeseeks to Rocket.Chat server. """

        await asyncio.get_event_loop().create_task(self._connect_base())
        await self.start_scheduler()
        LOGGER.info('%s: Started', self.__class__.__name__)
