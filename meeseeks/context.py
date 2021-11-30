"""Module contains context classes. """

from datetime import datetime, timedelta

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
    PRIVATE_ROOM_TYPE = 'p'

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
        self.fresh_msg_date = None
        self.link_previews = None
        self.room = None
        self.msg = ''

    def serialize(self):
        """Method serialize context. """

        try:
            self._args = self._raw_context[0]['fields']['args']

            self.method = self._raw_context[0]['msg']
            self.msg = self._args[0]['msg']
            self.user = ContextUser(**self._args[0]['u'])
            self.fresh_msg_date = self._check_msg_date()
            self.link_previews = self._check_link_previews()
            self.room = ContextRoom(self._args[0]['rid'], **self._args[1])
        except (KeyError, TypeError, ValueError, ) as exc:
            LOGGER.error('Failed to serialize %s: %s', self.__class__.__name__, exc)
            raise SerializerError from exc

    def _check_msg_date(self):
        """Return data of context message. """

        ts = self._args[0]['ts']['$date']
        updated_at = (datetime.utcfromtimestamp(ts / 1000) +
                      timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        return updated_at >= now

    def _check_link_previews(self):
        if 'urls' in self._args[0]:
            if self._args[0]['urls'] and 'meta' in self._args[0]['urls'][0]:
                return True

        return False


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
