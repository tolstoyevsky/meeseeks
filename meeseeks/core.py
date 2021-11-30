"""Module contains the basic functionality used by all applications. """

import asyncio
import json

import websockets
from websockets.exceptions import ConnectionClosedOK

from meeseeks import settings
from meeseeks.context import LoginCtx
from meeseeks.exceptions import (
    AbortCommandExecution,
    BadConfigure,
    CommandDoesNotExist,
    LogInFailed,
    SerializerError
)
from meeseeks.logger import LOGGER
from meeseeks.restapi import RestAPI
from meeseeks.rtapi import RealTimeAPI
from meeseeks.serializers import ContextSerializer

_ACCESS_DENIED_MSG = 'Access denied, not enough permissions'
_COMMAND_DOES_NOT_EXIST = 'Requested command does not exist'


class MeeseeksCore:
    """Provide basic functionality for building applications. """

    app_name = None

    _domain = settings.HOST.split('://')[1]
    _certificate = 's' if settings.HOST.split('://')[0].endswith('s') else ''
    _headers = {}
    _restapi = None
    _rtapi = None
    _token = None
    _user_id = None
    _apps = None

    def __init__(self):
        self._ctx = None
        self._request = None
        self._websocket = None

    async def check_bot_permissions(self):
        """Check if Meeseeks has valid permission on Rocket.Chat. """

        server_users = await self._restapi.get_users()
        if 'roles' not in server_users[self._user_id]:
            raise BadConfigure('Give Meeseeks permission "View Full Other User Info"'
                               'on Rocket.Chat')

    @staticmethod
    def check_app_name(app):
        """Check if attribute app_name in applications classes. """

        if not app.app_name:
            raise NotImplementedError(f'Implement attribute "app_name" '
                                      f'in {app.__class__.__name__} class.')

    async def bot_configure(self):
        """Check if Meeseeks configured correctly. """

        await self.check_bot_permissions()

    async def login(self):
        """Trying to log in Meeseeks to Rocket.Chat server. """

        await self._rtapi.connect()

        for i in range(0, settings.CONNECT_ATTEMPTS):
            await self._rtapi.login()
            try:
                for _ in range(0, 4):
                    raw_context = json.loads(await self._websocket.recv())

                    try:
                        serializer = ContextSerializer(
                            raw_context, raw_context['msg'], raw_context['id'],
                        )
                        self._ctx = serializer.serialize()
                    except (KeyError, ValueError, ):
                        continue

                    if isinstance(self._ctx, LoginCtx):
                        self._user_id = self._ctx.user_id
                        self._token = self._ctx.token
                        self._headers.update({
                            'X-Auth-Token': self._token,
                            'X-User-Id': self._user_id,
                            'Content-type': 'application/json'
                        })
                        LOGGER.info('%s: Login complete', self.__class__.__name__)
                        await self.bot_configure()
                        await self._rtapi.stream_all_messages()
                        return True
            except SerializerError:
                LOGGER.error('%s: '
                             'Unsuccessful connection attempt. Retrying...    '
                             'Step: %s/%s', self.__class__.__name__, i+1, settings.CONNECT_ATTEMPTS)
                await asyncio.sleep(3)

        raise LogInFailed(f'{self.__class__.__name__}: Cannot log in to Rocket.Chat server')

    async def process(self, _ctx):
        """Method for its further redefinition to implement the Meeseeks app functionality. """

    @staticmethod
    def _apps_receive(name):
        """Receive application class. """

        components = name.split('.')
        module = __import__(components[0])

        for comp in components[1:]:
            module = getattr(module, comp)

        return module

    def _init_apps(self):
        """Return list of apps classes. """

        return [self._apps_receive(app)(**self.__dict__) for app in settings.INSTALLED_APPS]

    async def loop(self):
        """Method is intended for calling in endless loop to process Rocket.Chat callbacks. """

        raw_context = json.loads(await self._websocket.recv())
        if raw_context.get('msg') == 'ping':
            return await self._rtapi.pong()

        try:
            serializer = ContextSerializer(
                raw_context, raw_context['msg'], raw_context['collection'],
            )
        except (KeyError, ValueError, ):
            return None

        try:
            self._ctx = serializer.serialize()
        except SerializerError:
            return None

        exc_counter = 0
        for app in self._apps:
            try:
                await app.process(self._ctx)
            except AbortCommandExecution:
                await self._restapi.write_msg(_ACCESS_DENIED_MSG, self._ctx.room.id)
                break
            except CommandDoesNotExist:
                exc_counter += 1

        if exc_counter == len(self._apps):
            await self._restapi.write_msg(_COMMAND_DOES_NOT_EXIST, self._ctx.room.id)

    async def setup(self):
        """Add functional in app after login. """

        raise NotImplementedError(f'Implement method setup in {self.__class__.__name__}.')

    async def run(self):
        """Entry point for run Meeseeks app. """

        websocket_url = f'ws{self._certificate}://{self._domain}/websocket'
        async with websockets.connect(websocket_url) as websocket:
            self._websocket = websocket
            self._rtapi = RealTimeAPI(self._request, self._websocket)
            self._restapi = RestAPI(self._headers)

            await self.login()

            self._apps = self._init_apps()
            for app in self._apps:
                self.check_app_name(app)
                await app.setup()

            while True:
                try:
                    await self.loop()
                except ConnectionClosedOK:
                    LOGGER.info('ConnectionClosedOk, relogin ...')
                    self._websocket = await websockets.connect(websocket_url)
                    self._rtapi = RealTimeAPI(self._request, self._websocket)
                    await self.login()
