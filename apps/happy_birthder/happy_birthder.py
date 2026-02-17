"""Module contains HappyBirthder application classes. """

import asyncio
import random
import traceback
from datetime import date, datetime, timedelta
from urllib.parse import urljoin

from aiohttp import ClientResponseError, ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apps.happy_birthder import settings
from apps.happy_birthder.mixins import CommandsMixin, DialogsMixin
from apps.happy_birthder.models import DB, User
from meeseeks import MeeseeksCore
from meeseeks.logger import LOGGER


class GifReceiver:  # pylint: disable=too-few-public-methods
    """Provide functionality for getting gifs from TenorAPI. """

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
            try:
                response_raw = await session.get(url)
                response = await response_raw.json()
            except ClientResponseError:
                return []

        gifs: list = response['results']
        filtered_gifs = []
        for gif in gifs:
            if gif['media'][0]['gif']['url'].split('/')[-2] in settings.TENOR_BLACKLISTED_GIF_IDS:
                continue
            filtered_gifs.append(gif['media'][0]['gif']['url'])

        return filtered_gifs

    async def get_random_gif_url(self):
        """Takes random gif from list of gifs. """

        gif_urls = await self._get_gif_urls()
        return random.choice(gif_urls) if gif_urls else ''


class HappyBirthder(CommandsMixin, DialogsMixin, MeeseeksCore):
    """HappyBirthder application. """

    app_name = 'happy-birthder'

    def __init__(self, **kwargs):
        super().__init__()

        self.__dict__.update(kwargs)

        self.gif_receiver = GifReceiver(settings.TENOR_API_KEY)
        self.scheduler = AsyncIOScheduler(settings.SCHEDULER_SETTINGS)

    @staticmethod
    def send_traceback(func):
        """Decorator handles unexpected exceptions and sends traceback to Rocket.Chat. """

        async def wrapper(self, *args, **kwargs):
            try:
                await func(self, *args, **kwargs)
            except Exception:  # pylint: disable=broad-exception-caught
                alert_msg = settings.TRACEBACK_ALERT_MSG.format(traceback.format_exc())
                await self._restapi.write_msg(alert_msg, settings.TRACEBACK_ALERT_GROUP)  # pylint: disable=protected-access
                raise

        return wrapper

    @send_traceback
    async def check_users_avatars_job(self):
        """Checks if the users set their avatars. """

        persons_without_avatar = ''
        server_users = await self._restapi.get_users()
        async with ClientSession() as session:
            for user in server_users.values():
                if self.check_user_status(user):
                    url = urljoin(settings.ROCKET_CHAT_API, f'/avatar/{user["username"]}')
                    response_raw = await session.get(url)
                    if response_raw.content_type == 'image/svg+xml':
                        persons_without_avatar += f'\n@{user["username"]}'
                        await self._restapi.write_msg(settings.NOTIFY_SET_AVATAR, user['_id'])

            if persons_without_avatar and settings.BIRTHDAY_LOGGING_CHANNEL:
                await self._restapi.write_msg(
                    settings.PERSONS_WITHOUT_AVATAR_RESPONSE + persons_without_avatar,
                    settings.BIRTHDAY_LOGGING_CHANNEL,
                )

    @send_traceback
    async def update_users_job(self):
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

    @send_traceback
    async def clean_users_job(self):
        """Deletes users from Postgres that were removed from Rocket.Chat. """

        server_users = await self._restapi.get_users()
        bot_users = await User.query.gino.all()
        for user in bot_users:
            if user.user_id not in server_users:
                await user.delete()

    async def prepare_users_info(self, users):
        """Return users info to use for checking dates. """

        users_info = []
        today = date.today()
        for user in users:
            user_id = user.user_id
            if not self.check_user_status(await self._restapi.get_user_info(user.user_id)):
                continue

            name = user.name
            birth_date = user.birth_date
            birthday_group_name = f'birthday-of-{name}'
            fwd = user.fwd
            users_for_mailing = {
                user.user_id: user.name for user in users if user.user_id != user_id and
                self.check_user_status(await self._restapi.get_user_info(user.user_id))
            }
            days_in_advance = today + timedelta(days=settings.NUMBER_OF_DAYS_IN_ADVANCE)

            users_info.append({
                'id': user_id,
                'name': name,
                'birth_date': birth_date,
                'fwd': fwd,
                'users_for_mailing': users_for_mailing,
                'birthday_group_name': birthday_group_name,
                'days_in_advance': days_in_advance,
            })

        return users_info

    async def create_birthday_group(self, user):
        """Create birthday group. """

        if settings.CREATE_BIRTHDAY_CHANNELS:
            birthday_group_name = user['birthday_group_name']
            users_for_mailing = user['users_for_mailing']

            await self._restapi.create_group(birthday_group_name, list(users_for_mailing.values()))
            await self._restapi.write_msg('@all, Let`s discuss a present', birthday_group_name)

    async def _check_birthday_group_ttl_expired(self, birth_date, birthday_group_name):
        """Checks if expired birthday group time to live. """

        try:
            group_info = await self._restapi.get_group_info(birthday_group_name)
        except ClientResponseError:
            return False

        utcnow = datetime.utcnow().date()
        group_ttl = timedelta(days=settings.BIRTHDAY_CHANNEL_TTL)
        group_last_message_date = datetime.fromisoformat(
            group_info['lastMessage']['ts'].replace('Z', '')
        ).date()

        # Use current year for valid comparison of day and month of birthday date
        birth_date_with_current_year = date(
            year=utcnow.year,
            month=birth_date.month,
            day=birth_date.day,
        )

        return (
            utcnow >= birth_date_with_current_year + group_ttl and
            utcnow >= group_last_message_date + group_ttl
        )

    @send_traceback
    async def check_dates_job(self):
        """Check users birthdays, first working days. """

        users = await User.query.gino.all()
        users_info = await self.prepare_users_info(users)
        today = date.today()
        tomorrow = today + timedelta(days=1)
        persons_without_birthday = ''
        users_anniversary = ''

        for user in users_info:
            is_birthday_group_ttl_expired = await self._check_birthday_group_ttl_expired(
                user['birth_date'],
                user['birthday_group_name'],
            )

            if user['birth_date'] is None:
                await self._restapi.write_msg(settings.NOTIFY_SET_BIRTH_DATE, user['id'])
                persons_without_birthday += f'\n@{user["name"]}'
            elif user['birth_date'].day == today.day and user['birth_date'].month == today.month:
                gif_url = await self.gif_receiver.get_random_gif_url()
                phrase = random.choice(settings.CONGRATULATION_PHRASES)
                response = f'{gif_url}\nToday is birthday of @{user["name"]}!\n{phrase}'
                await self._restapi.write_msg(response, 'GENERAL')
            elif (user['birth_date'].day == tomorrow.day and
                  user['birth_date'].month == tomorrow.month):
                for user_id_for_mailing in user['users_for_mailing'].keys():
                    await self._restapi.write_msg(f'@{user["name"]} is having a birthday tomorrow.',
                                                  user_id_for_mailing)
            elif (user['birth_date'].day == user['days_in_advance'].day and
                    user['birth_date'].month == user['days_in_advance'].month):
                await self.create_birthday_group(user)
                for user_id_for_mailing in user['users_for_mailing'].keys():
                    await self._restapi.write_msg(
                        f'@{user["name"]} is having a birthday on '
                        f'{date.strftime(user["days_in_advance"], "%d.%m.%Y")}',
                        user_id_for_mailing)
            elif is_birthday_group_ttl_expired and settings.CREATE_BIRTHDAY_CHANNELS:
                await self._restapi.delete_group(user['birthday_group_name'])

            if (user['fwd'] is not None and user['fwd'].day == today.day and
                    user['fwd'].month == today.month and (today.year - user['fwd'].year) > 0):
                anniversary = today.year - user['fwd'].year
                year_str = 'year' if anniversary == 1 else 'years'
                users_anniversary += (f'\n@{user["name"]} has been a part of our team for '
                                      f'**{anniversary} {year_str}!**')

        if persons_without_birthday and settings.BIRTHDAY_LOGGING_CHANNEL:
            await self._restapi.write_msg(
                settings.PERSONS_WITHOUT_BIRTHDAY_RESPONSE + persons_without_birthday,
                settings.BIRTHDAY_LOGGING_CHANNEL)

        if users_anniversary:
            await self._restapi.write_msg(
                'I am glad to announce that today is the day of anniversary for some of us!:tada:' +
                users_anniversary, 'GENERAL')

    async def scheduler_jobs(self):
        """Wraps scheduler jobs. """

        await self.clean_users_job()
        await self.update_users_job()
        await self.check_dates_job()

        if settings.CHECK_USERS_AVATARS:
            await self.check_users_avatars_job()

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

    async def start_scheduler(self):
        """Starts all scheduler jobs. """

        self.scheduler.add_job(
            self.scheduler_jobs,
            id='schedule',
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
