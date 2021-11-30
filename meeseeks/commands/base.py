"""Module contains necessary implementation for Meeseeks commands. """

import asyncio
from abc import ABC

from meeseeks import settings
from meeseeks.context import ChangedRoomMessageCtx, ContextRoom
from meeseeks.core import MeeseeksCore
from meeseeks.commands.decorators import cmd
from meeseeks.exceptions import CommandDoesNotExist


class Communication(MeeseeksCore, ABC):
    """Contains methods for processing incoming Rocket.Chat messages. """

    def _get_response_msg(self):
        """Return the message sent by user without prefix. """

        return self._ctx.msg.replace(f'@{settings.USER_NAME}', '', 1)

    async def _write_command_msg(self, msg):
        """Sends a message to the channel from which the command was called. """

        await self._restapi.write_msg(msg, self._ctx.room.id)


class CommandsBase(Communication, ABC):
    """Contains methods for running commands on client Rocket.Chat. """

    def __init__(self):
        super().__init__()

        self._command_methods = self._get_command_methods()
        self._command_method = None

    def _get_command_methods(self):
        """Return methods that are Meeseeks commands. """

        command_methods = []
        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, 'command_name'):
                command_methods.append(method)

        return command_methods

    @staticmethod
    def _normalize_msg(message):
        """Return normalize message. """

        return ' '.join(list(map(lambda word: word.strip().lower(), message.split())))

    def _get_arguments(self, command_name):
        """Return arguments from the message sent by user. """

        response_msg = self._normalize_msg(self._get_response_msg())
        arguments = response_msg.replace(command_name, '', 1).strip().split(',')
        arguments = list(map(lambda arg: arg.strip(), arguments))

        return arguments if arguments[0] != '' else []

    async def check_permissions(self, roles=None):
        """Checks if user who called the command has necessary role. """

        users_info = await self._restapi.get_user_info(self._ctx.user.id)
        allow = False
        if not roles:
            allow = True
        elif any(role in roles for role in users_info['roles']):
            allow = True

        return allow

    async def _process_command(self):
        """Performs Meeseeks command processing. """

        if (isinstance(self._ctx, ChangedRoomMessageCtx) and self._ctx.user.id != self._user_id and
                self._ctx.link_previews is False and self._ctx.fresh_msg_date and
                self._ctx.msg.startswith(f'@{settings.USER_NAME}')):
            raw_message = self._get_response_msg()
            requested_command = self._normalize_msg(raw_message)

            try:
                self._command_method = next(method for method in self._command_methods if
                                            requested_command.startswith(method.command_name))
            except StopIteration as exc:
                raise CommandDoesNotExist from exc

            if asyncio.iscoroutinefunction(self._command_method):
                await self._command_method()
            else:
                self._command_method()

    async def process(self, ctx):
        """Process Meeseeks command on user request. """

        await super().process(ctx)

        await self._process_command()

    @cmd(name='help', description='__doc__')
    async def cmd_help(self):
        """Return list of commands for this application. """

        arguments = self._get_arguments(self._command_method.command_name)
        if not arguments or self.app_name in arguments:
            help_title = f'**{self.app_name}** commands\n'
            docstrings_list = []
            for method in self._command_methods:
                command_name = method.command_name
                if command_name == 'help':
                    command_name = f'help {self.app_name}'
                if await self.check_permissions(method.permissions):
                    docstrings_list.append(f'@{settings.USER_NAME} **{command_name}** - '
                                           f'{method.command_description}')
            help_response = help_title + '\n'.join(docstrings_list)

            await self._write_command_msg(help_response)


class DialogsBase(Communication, ABC):
    """Contains base methods for dialogs. """

    def __init__(self):
        super().__init__()

        self._dialogs_methods = self._get_dialog_methods()

    def _get_dialog_methods(self):
        """Return methods that are Meeseeks dialogs. """

        dialog_methods = []
        for method_name in dir(self):
            if method_name.startswith('dialog_'):
                method = getattr(self, method_name)
                dialog_methods.append(method)

        return dialog_methods

    async def process(self, ctx):
        """Call all methods with prefix "dialogs_". """

        await super().process(ctx)

        self._ctx = ctx
        if (isinstance(self._ctx, ChangedRoomMessageCtx) and self._ctx.user.id != self._user_id and
                self._ctx.room.type == ContextRoom.DIALOG_ROOM_TYPE and self._ctx.fresh_msg_date):
            for dialog_method in self._dialogs_methods:
                await dialog_method(self._get_response_msg().lower())
