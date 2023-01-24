"""Module contains necessary implementation for Meeseeks commands. """

from abc import ABC
from typing import Callable

from meeseeks import settings
from meeseeks.context import ChangedRoomMessageCtx, ContextRoom
from meeseeks.core import MeeseeksCore
from meeseeks.commands.decorators import cmd, CommandMethod
from meeseeks.exceptions import CommandDoesNotExist
from meeseeks.type import UserInfo


class Communication(MeeseeksCore, ABC):
    """Contains methods for processing incoming Rocket.Chat messages. """

    _ctx: ChangedRoomMessageCtx

    def _get_response_msg(self) -> str:
        """Return message without prefix sent by user. """

        return self._ctx.msg.replace(f'@{settings.USER_NAME}', '', 1)

    async def _write_command_msg(self, msg: str) -> None:
        """Sends message to channel from which command was called. """

        await self._restapi.write_msg(msg, self._ctx.room.id)


class CommandsBase(Communication, ABC):
    """Contains methods for running commands on client Rocket.Chat. """

    def __init__(self) -> None:
        super().__init__()

        self._command_methods: list[CommandMethod] = self._get_command_methods()
        self._command_method: CommandMethod | None = None

    def _get_command_methods(self) -> list[CommandMethod]:
        """Return methods that are Meeseeks commands. """

        command_methods: list[CommandMethod] = []
        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, 'command_name'):
                command_methods.append(method)

        return command_methods

    @staticmethod
    def _normalize_msg(message: str) -> str:
        """Return normalized message. """

        return ' '.join(list(map(lambda word: word.strip().lower(), message.split())))

    def _get_arguments(self, command_name: str) -> list[str]:
        """Return arguments from message sent by user. """

        response_msg: str = self._normalize_msg(self._get_response_msg())
        arguments: list[str] = response_msg.replace(command_name, '', 1).strip().split(',')
        strip_arg: Callable[[str], str] = lambda arg: arg.strip()
        arguments = list(map(strip_arg, arguments))

        return arguments if arguments[0] != '' else []

    async def check_permissions(self, roles: list | None = None) -> bool:
        """Checks if user who called command has necessary role. """

        allow: bool = False
        users_info: UserInfo | None = await self._restapi.get_user_info(self._ctx.user.id)
        if not roles:
            allow = True
        elif users_info and any(role in roles for role in users_info['roles']):
            allow = True

        return allow

    async def _process_command(self) -> None:
        """Performs Meeseeks command processing. """

        if (isinstance(self._ctx, ChangedRoomMessageCtx) and self._ctx.user.id != self._user_id and
                self._ctx.link_previews is False and self._ctx.fresh_msg_date and
                self._ctx.msg.startswith(f'@{settings.USER_NAME}')):
            raw_message: str = self._get_response_msg()
            requested_command: str = self._normalize_msg(raw_message)

            try:
                self._command_method = next(method for method in self._command_methods if
                                            requested_command.startswith(method.command_name))
            except StopIteration as exc:
                raise CommandDoesNotExist from exc

            if self._command_method:
                await self._command_method()

    async def process(self, ctx: ChangedRoomMessageCtx) -> None:
        """Process Meeseeks command on user request. """

        await super().process(ctx)

        self._ctx = ctx
        await self._process_command()

    @cmd(name='help', description='Get commands list for this application',)
    async def cmd_help(self) -> None:
        """Receives apps commands and sends response to Rocket.Chat. """

        if not self._command_method or not self._command_method.command_name:
            return None

        arguments: list = self._get_arguments(self._command_method.command_name)
        if not arguments or self.app_name in arguments:
            help_title: str = f'**{self.app_name}** commands\n'
            docstrings_list: list = []
            for method in self._command_methods:
                command_name: str = method.command_name
                if command_name == 'help':
                    command_name = f'help {self.app_name}'
                if await self.check_permissions(method.permissions):
                    docstrings_list.append(f'@{settings.USER_NAME} **{command_name}** - '
                                           f'{method.command_description}')
            help_response: str = help_title + '\n'.join(docstrings_list)

            await self._write_command_msg(help_response)


class DialogsBase(Communication, ABC):
    """Contains base methods for dialogs. """

    def __init__(self) -> None:
        super().__init__()

        self._dialogs_methods = self._get_dialog_methods()

    def _get_dialog_methods(self) -> list[Callable]:
        """Return methods that are Meeseeks dialogs. """

        dialog_methods: list[Callable] = []
        for method_name in dir(self):
            if method_name.startswith('dialog_'):
                method = getattr(self, method_name)
                dialog_methods.append(method)

        return dialog_methods

    async def process(self, ctx: ChangedRoomMessageCtx) -> None:
        """Call all methods with prefix "dialogs_". """

        await super().process(ctx)

        self._ctx = ctx
        if (self._ctx.user.id != self._user_id and self._ctx.fresh_msg_date and
                self._ctx.room.type == ContextRoom.DIALOG_ROOM_TYPE):
            for dialog_method in self._dialogs_methods:
                await dialog_method(self._get_response_msg().lower())
