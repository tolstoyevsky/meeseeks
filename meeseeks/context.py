"""Module contains context classes. """

from datetime import datetime, timedelta
from typing import Any, Type

from meeseeks.exceptions import SerializerError
from meeseeks.logger import LOGGER
from meeseeks.serializers import ctx_factory
from meeseeks.type import ContextRoomOptions


class Context:
    """Contains default context attrs. """

    def __init__(self, raw_context: tuple):
        self._raw_context = raw_context
        self.method: str = ''

    def serialize(self) -> None:
        """Method serialize context. """

        raise NotImplementedError


class ContextUser:
    """Contains user context. """

    def __init__(self, _id: str, username: str, name: str):
        self.id: str = _id
        self.username: str = username
        self.name: str = name


class ContextRoom:
    """Contains room context. """

    CHANNEL_ROOM_TYPE = 'c'
    DIALOG_ROOM_TYPE = 'd'
    PRIVATE_ROOM_TYPE = 'p'

    def __init__(self, room_id: str, options: ContextRoomOptions):
        self.id = room_id
        self.type = options.get('roomType')
        self.participant = options.get('roomParticipant')
        self.name = options.get('roomName')


class ChangedRoomMessageCtx(Context):
    """Contains room message context. """

    def __init__(self, *args: dict):
        super().__init__(args)

        self._args: dict = {}

        self.user: Type[ContextUser] | ContextUser = ContextUser
        self.fresh_msg_date: bool = False
        self.link_previews: bool = False
        self.room: Type[ContextRoom] | ContextRoom = ContextRoom
        self.msg: str = ''

    def serialize(self) -> None:
        """Method serialize context. """

        try:
            self._args = self._raw_context[0]['fields']['args']

            self.method: str = self._raw_context[0]['msg']
            self.msg = self._args[0]['msg']
            self.user = ContextUser(**self._args[0]['u'])
            self.fresh_msg_date = self._check_msg_date()
            self.link_previews = self._check_link_previews()
            self.room = ContextRoom(self._args[0]['rid'], self._args[1])
        except (KeyError, TypeError, ValueError, ) as exc:
            LOGGER.error('Failed to serialize %s: %s', self.__class__.__name__, exc)
            raise SerializerError from exc

    def _check_msg_date(self) -> bool:
        """Return data of context message. """

        ts: int = self._args[0]['ts']['$date']
        updated_at: str = (
                datetime.utcfromtimestamp(ts / 1000) + timedelta(seconds=1)
        ).strftime('%Y-%m-%d %H:%M:%S')
        now: str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        return updated_at >= now

    def _check_link_previews(self) -> bool:
        if 'urls' in self._args[0]:
            if self._args[0]['urls'] and 'meta' in self._args[0]['urls'][0]:
                return True

        return False


class LoginCtx(Context):
    """Contains login context. """

    def __init__(self, *args: dict):
        super().__init__(args)

        self._args: dict[str, Any] = {}

        self.user_id: str = ''
        self.token: str = ''

    def serialize(self) -> None:
        """Method serialize context. """

        try:
            self._args = self._raw_context[0]['result']

            self.user_id = self._args['id']
            self.token = self._args['token']
        except (KeyError, TypeError, ValueError, ) as exc:
            raise SerializerError from exc


ctx_factory.register('changed', 'stream-room-messages', ChangedRoomMessageCtx)
ctx_factory.register('result', 'login', LoginCtx)
