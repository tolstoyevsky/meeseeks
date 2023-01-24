"""Module contains MeeseeksBaseApp application classes. """

from meeseeks.commands import CommandsMixin, DialogsMixin
from meeseeks.logger import LOGGER


class MeeseeksBaseApp(CommandsMixin, DialogsMixin):
    """Application contains base Meeseeks functionality. """

    app_name: str = 'meeseeks'

    def __init__(self, **kwargs: dict):
        super().__init__()

        self.__dict__.update(kwargs)

    async def setup(self) -> None:
        """Trying to log in MeeseeksBaseApp to Rocket.Chat server. """

        LOGGER.info('%s: Started', self.__class__.__name__)
