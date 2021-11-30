"""Module containing VoteOrDie mixins. """

from abc import ABC

from apps.vote_or_die import settings
from meeseeks.context import ContextRoom
from meeseeks.commands.decorators import cmd
from meeseeks.commands.base import (
    CommandsBase as CommandsBaseCore,
    Communication as CommunicationBase
)


class Communication(CommunicationBase, ABC):
    """Contains methods for processing incoming Rocket.Chat messages. """

    async def _write_command_attachment(self, title, msg):
        """Sends a message to the channel from which the command was called. """

        return await self._restapi.write_attachments_msg(title, msg, self._ctx.room.id)


class CommandsBase(Communication, CommandsBaseCore, ABC):
    """Contains methods for running commands on client Rocket.Chat. """


class CommandsMixin(CommandsBase, ABC):
    """Contains methods for running VoteOrDie commands on client Rocket.Chat. """

    @cmd(name='vote', description='__doc__')
    async def cmd_vote(self):
        """Start vote with getting arguments. """

        if (self._ctx.room.type == ContextRoom.DIALOG_ROOM_TYPE and settings.RESPOND_TO_DM or
                self._ctx.room.type == ContextRoom.CHANNEL_ROOM_TYPE or
                self._ctx.room.type == ContextRoom.PRIVATE_ROOM_TYPE):
            arguments = self._get_arguments(self._command_method.command_name)
            if len(arguments) <= 2:
                return await self._write_command_msg('Please, more enter arguments.')

            if len(arguments) <= 12:
                title = arguments.pop(0)
                options = []
                for arg in arguments:
                    options.append(f'{settings.EMOJIS[len(options)]} {arg}')
                response = await self._write_command_attachment(title, '\n'.join(options))

                for i in range(0, len(options)):
                    await self._restapi.add_reaction(
                        response['message']['_id'], settings.EMOJIS[i], True)
            else:
                await self._write_command_msg(settings.TOO_MANY_ARGS)
