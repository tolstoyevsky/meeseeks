"""Module contains basic functionality used by all applications. """

import asyncio
import json
from types import ModuleType
from typing import Generic, Type, TypeVar
from urllib.parse import ParseResult, urljoin, urlparse

import websockets
from aiohttp import ClientResponseError
from websockets import WebSocketClientProtocol  # pylint: disable=no-name-in-module
from websockets.exceptions import ConnectionClosedOK

from meeseeks import settings
from meeseeks.context import Context, ChangedRoomMessageCtx, LoginCtx
from meeseeks.exceptions import (
    AbortCommandExecution,
    BadConfigure,
    CommandDoesNotExist,
    LogInFailed,
    SerializerError,
)
from meeseeks.logger import LOGGER
from meeseeks.restapi import RestAPI
from meeseeks.rtapi import RealTimeAPI
from meeseeks.serializers import ContextSerializer

_ACCESS_DENIED_MSG = 'Access denied, not enough permissions'
_COMMAND_DOES_NOT_EXIST = 'Requested command does not exist'

_T = TypeVar('_T', bound='MeeseeksCore')


class MeeseeksCore(Generic[_T]):
    """Provide basic functionality for building applications. """

    app_name: str = ''

    _url: ParseResult = urlparse(settings.ROCKET_CHAT_API)
    _headers: dict[str, str] = {}
    _restapi: RestAPI
    _rtapi: RealTimeAPI
    _token: str = ''
    _user_id: str = ''
    _apps: list = []

    def __init__(self) -> None:
        self._request: str = ''
        self._websocket: WebSocketClientProtocol = WebSocketClientProtocol
        self._websocket_protocol: str = 'wss' if self._url.scheme == 'https' else 'ws'

    async def check_bot_permissions(self) -> None:
        """Check if Meeseeks has valid permission on Rocket.Chat. """

        server_users: dict[str, dict] = await self._restapi.get_users()
        if 'roles' not in server_users[self._user_id]:
            raise BadConfigure('Give Meeseeks permission "View Full Other User Info"'
                               'on Rocket.Chat')

    @staticmethod
    def check_app_name(app: _T) -> None:
        """Check if attribute app_name in applications classes. """

        if not app.app_name:
            raise NotImplementedError(f'Implement attribute "app_name" '
                                      f'in {app.__class__.__name__} class.')

    async def bot_configure(self) -> None:
        """Check if Meeseeks configured correctly. """

        await self.check_bot_permissions()

    async def login(self) -> bool:
        """Trying to log in Meeseeks to Rocket.Chat server. """

        await self._rtapi.connect()

        for i in range(0, settings.CONNECT_ATTEMPTS):
            await self._rtapi.login()
            try:
                for _ in range(0, 4):
                    raw_context: WebSocketClientProtocol = json.loads(await self._websocket.recv())

                    try:
                        serializer: ContextSerializer = ContextSerializer(
                            raw_context, raw_context['msg'], raw_context['id'],
                        )
                        ctx: Context = serializer.serialize()
                    except (KeyError, ValueError, ):
                        continue

                    if isinstance(ctx, LoginCtx):
                        self._user_id = ctx.user_id
                        self._token = ctx.token
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

    async def process(self, ctx: ChangedRoomMessageCtx) -> None:
        """Method for its further redefinition to implement the Meeseeks app functionality. """

    @staticmethod
    def _apps_receive(name: str) -> Type[_T] | None:
        """Receive application class. """

        components: list[str] = name.split('.')
        module: ModuleType = __import__(components[0])
        app_class: Type[_T] | None = None

        for comp in components[1:]:
            app_class = getattr(module, comp)

        return app_class

    def _init_apps(self) -> list[_T]:
        """Return list of apps classes. """

        app_instances: list = []
        for app in settings.INSTALLED_APPS:
            app_class = self._apps_receive(app)
            if app_class:
                app_instances.append(app_class(**self.__dict__))

        return app_instances

    async def message_handler(self, message: str) -> None:
        """Serializes message context and run processing for each app. """

        raw_context: WebSocketClientProtocol = json.loads(message)
        if raw_context.get('msg') == 'ping':
            await self._rtapi.pong()
            return None

        try:
            serializer: ContextSerializer = ContextSerializer(
                raw_context, raw_context['msg'], raw_context['collection'],
            )
        except (KeyError, ValueError, ):
            return None

        try:
            ctx: Context = serializer.serialize()
        except SerializerError:
            return None

        if isinstance(ctx, ChangedRoomMessageCtx):
            exc_counter = 0
            for app in self._apps:
                try:
                    await app.process(ctx)
                except AbortCommandExecution:
                    await self._restapi.write_msg(_ACCESS_DENIED_MSG, ctx.room.id)
                    break
                except CommandDoesNotExist:
                    exc_counter += 1

            if exc_counter == len(self._apps):
                await self._restapi.write_msg(_COMMAND_DOES_NOT_EXIST, ctx.room.id)

    async def setup(self) -> None:
        """Add functional in app after login. """

        raise NotImplementedError(f'Implement method setup in {self.__class__.__name__}.')

    async def run(self) -> None:
        """Entry point for run Meeseeks app. """

        websocket_url: str = urljoin(f'{self._websocket_protocol}://{self._url.netloc}',
                                     'websocket')
        async with websockets.connect(websocket_url) as websocket:
            self._websocket = websocket
            self._rtapi = RealTimeAPI(self._request, self._websocket)
            self._restapi = RestAPI(self._headers)

            await self.login()

            self._apps: list[_T] = self._init_apps()
            for app in self._apps:
                self.check_app_name(app)
                await app.setup()

            async for message in websocket:
                try:
                    asyncio.create_task(self.message_handler(message))
                except ClientResponseError as exc:
                    LOGGER.error(exc)
                except ConnectionClosedOK:
                    LOGGER.info('ConnectionClosedOk, relogin ...')
                    self._websocket = await websockets.connect(websocket_url)
                    self._rtapi = RealTimeAPI(self._request, self._websocket)
                    await self.login()
