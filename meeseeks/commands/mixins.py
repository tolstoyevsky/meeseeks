"""Module contains Meeseeks commands mixins. """
from abc import ABC

from meeseeks import settings
from meeseeks.commands.base import CommandsBase, DialogsBase
from meeseeks.commands.decorators import cmd


class CommandsMixin(CommandsBase, ABC):
    """Contains methods for running Meeseeks commands on client Rocket.Chat. """

    @cmd(
        name='get rooms info',
        permissions=['admin', ],
        description='Get information about available rooms',
    )
    async def cmd_rooms_info(self) -> None:
        """Receives available rooms from Rocket.Chat and sends response to Rocket.Chat. """

        rooms: dict[str, str] = await self._restapi.get_rooms()
        title: str = 'Hi, here is the information about the rooms :point_down:\n'
        response: str = ''

        if isinstance(rooms, dict):
            for key, name in rooms.items():
                response = response + f'\n**{key}** : {name}'

            await self._write_command_msg(title + response)

    @cmd(
        name='get users info',
        permissions=['admin', ],
        description='Get information about users',
    )
    async def cmd_users_info(self) -> None:
        """Receives users from Rocket.Chat and sends response to Rocket.Chat. """

        users: dict[str, dict] = await self._restapi.get_users()
        title: str = 'Hi, here is the information about the users :point_down:\n'
        response: str = ''

        for user in users.values():
            response = response + f'\n**{user["_id"]}** : {user["name"]}'

        await self._write_command_msg(title + response)


class DialogsMixin(DialogsBase, ABC):
    """Contains methods for communication Rocket.Chat user and Meeseeks. """

    async def dialog_hello(self, message: str) -> None:
        """Return response to the received direct message "hello". """

        if message == 'hello':
            await self._write_command_msg(settings.HELLO_RESPONSE)
