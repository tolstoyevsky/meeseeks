"""Module containing MeeseeksBaseApp application classes. """

from meeseeks.commands import CommandsMixin, DialogsMixin
from meeseeks.logger import LOGGER


class MeeseeksBaseApp(CommandsMixin, DialogsMixin):
    """Application contains base Meeseeks functionality. """

    app_name = 'meeseeks'

    def __init__(self, **kwargs):
        super().__init__()

        self.__dict__.update(kwargs)

    async def setup(self):
        """Trying to log in Meeseeks to Rocket.Chat server. """

        await self._rtapi.stream_all_messages()
        LOGGER.info('%s: Subscription complete', self.__class__.__name__)
