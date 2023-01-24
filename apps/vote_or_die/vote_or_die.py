"""Module contains VoteOrDie application classes. """

from apps.vote_or_die.mixins import CommandsMixin
from apps.vote_or_die.restapi import RestAPI
from meeseeks.commands.mixins import DialogsBase as DialogsMixin
from meeseeks import MeeseeksCore
from meeseeks.logger import LOGGER


class VoteOrDie(CommandsMixin, DialogsMixin, MeeseeksCore):
    """VoteOrDie application. """

    app_name = 'vote-or-die'

    def __init__(self, **kwargs):
        super().__init__()

        self.__dict__.update(kwargs)

        self._restapi = RestAPI(self._headers)

    async def setup(self):
        """Trying to log in Meeseeks to Rocket.Chat server. """

        LOGGER.info('%s: Started', self.__class__.__name__)
