"""Module contains context classes. """

from datetime import datetime

from meeseeks.exceptions import SerializerError
from meeseeks.logger import LOGGER
from meeseeks.serializers import ctx_factory


class ContextUser:
    """Contains user context. """

    def __init__(self, _id, username, name):
        self.id = _id
        self.username = username
        self.name = name


class ContextRoom:
    """Contains room context. """

    CHANNEL_ROOM_TYPE = 'c'
    DIALOG_ROOM_TYPE = 'd'

    def __init__(self, room_id, **kwargs):
        self.id = room_id
        self.type = kwargs.pop('roomType')
        self.participant = kwargs.pop('roomParticipant')
        self.name = kwargs.get('roomName')


class Context:
    """Contains default context attrs. """

    def __init__(self, raw_context):
        self._raw_context = raw_context
        self.method = ''

    def serialize(self):
        """Method serialize context. """

        raise NotImplementedError


class ChangedRoomMessageCtx(Context):
    """Contains room message context. """

    def __init__(self, *args):
        super().__init__(args)

        self._args = {}

        self.user = None
        self.updated_at = None
        self.room = None
        self.msg = ''

    def serialize(self):
        """Method serialize context. """

        try:
            self._args = self._raw_context[0]['fields']['args']

            self.method = self._raw_context[0]['msg']
            self.msg = self._args[0]['msg']
            self.user = ContextUser(**self._args[0]['u'])
            self.updated_at = self._get_updated_at()
            self.room = ContextRoom(self._args[0]['rid'], **self._args[1])
        except (KeyError, TypeError, ValueError, ) as exc:
            LOGGER.error('Failed to serialize %s: %s', self.__class__.__name__, exc)
            raise SerializerError from exc

    def _get_updated_at(self):
        """Return data of context message. """

        ts = self._args[0]['ts']['$date']
        updated_at = datetime.utcfromtimestamp(ts / 1000)

        return updated_at


class LoginCtx(Context):
    """Contains login context. """

    def __init__(self, *args):
        super().__init__(args)

        self._args = {}

        self.user_id = ''
        self.token = ''

    def serialize(self):
        """Method serialize context. """

        try:
            self._args = self._raw_context[0]['result']

            self.user_id = self._args['id']
            self.token = self._args['token']
        except (KeyError, TypeError, ValueError, ) as exc:
            raise SerializerError from exc


ctx_factory.register('changed', 'stream-room-messages', ChangedRoomMessageCtx)
ctx_factory.register('result', 'login', LoginCtx)
