"""Module containing Meeseeks commands mixins. """
from abc import ABC

from meeseeks import settings
from meeseeks.commands.base import CommandsBase, DialogsBase
from meeseeks.commands.decorators import cmd


class CommandsMixin(CommandsBase, ABC):
    """Contains methods for running Meeseeks commands on client Rocket.Chat. """

    @cmd(name='get rooms info', permissions=['admin'], description='__doc__')
    async def cmd_rooms_info(self):
        """Sends information about rooms. """

        rooms = await self._restapi.get_rooms(command=True)
        title = 'Hi, here is the information about the rooms :point_down:\n'
        rooms_list = ''

        for key, name in rooms.items():
            rooms_list = rooms_list + f'\n**{key}** : {name}'

        await self._write_command_msg(title + rooms_list)

    @cmd(name='get users info', permissions=['admin'], description='__doc__')
    async def cmd_users_info(self):
        """Sends information about users. """

        users = await self._restapi.get_users()
        title = 'Hi, here is the information about the users :point_down:\n'
        users_list = ''

        for user in users.values():
            users_list = users_list + f'\n**{user["_id"]}** : {user["name"]}'

        await self._write_command_msg(title + users_list)


class DialogsMixin(DialogsBase, ABC):
    """Contains methods for communication Rocket.Chat user and Meeseeks. """

    async def dialog_hello(self, message):
        """Return response to the received direct message "hello". """

        if message == 'hello':
            await self._write_command_msg(settings.HELLO_RESPONSE)
