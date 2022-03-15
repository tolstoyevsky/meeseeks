"""Module containing HappyBirthder mixins. """

import re
from abc import ABC
from datetime import datetime, date

from tabulate import tabulate

from apps.happy_birthder import settings
from apps.happy_birthder.models import User
from meeseeks.commands.decorators import cmd
from meeseeks.commands.mixins import CommandsBase, DialogsBase


class CommandsMixin(CommandsBase, ABC):
    """Contains methods for running HappyBirthder commands on client Rocket.Chat. """

    @staticmethod
    def check_user_status(user):
        """Check user status for processing data. """

        return (user['active'] and 'guest' not in user['roles'] and
                'bot' not in user['roles'])

    @cmd(name='set users birthday', permissions=['admin'], description='__doc__')
    async def cmd_set_users_birthday(self):
        """Sets birth date to given users. """

        arguments = self._get_arguments(self._command_method.command_name)
        users_info = [user_info_raw.split() for user_info_raw in arguments]
        response = ''

        for user_info in users_info:
            user_name = user_info[0].replace('@', '')
            user_in_base = await User.query.where(User.name == user_name).gino.first()

            if not user_in_base:
                response += f'\n@{user_name} - User does not exist in base'
            else:
                try:
                    birth_date = datetime.strptime(user_info[1], '%d.%m.%Y').date()
                except ValueError:
                    response += f'\n@{user_name} - Invalid date format'
                    continue
                except IndexError:
                    response += f'\n@{user_name} - Date of birth not given'
                    continue

                await user_in_base.update(birth_date=birth_date).apply()
                response += f'\n@{user_name} - Success'

        await self._write_command_msg(response)

    @cmd(name='delete all users', permissions=['admin'], description='__doc__')
    async def cmd_del_all_users(self):
        """Delete all users from database. """

        users = await User.query.gino.all()
        for user in users:
            await user.delete()

        await self._write_command_msg('Success')

    @cmd(name='get users base', permissions=['admin'], description='__doc__')
    async def cmd_get_users_base(self):
        """Receive all users from database. """

        users = await User.query.gino.all()
        headers = ['user_id', 'name', 'birth_date', 'fwd']
        table = []

        for user in users:
            birth_date = user.birth_date.strftime('%d.%m.%Y') if user.birth_date else None
            fwd = user.fwd.strftime('%d.%m.%Y') if user.fwd else None
            table.append([user.user_id, user.name, birth_date, fwd])

        await self._write_command_msg(
            f'```\n{tabulate(table, headers, tablefmt="fancy_grid")}\n```')

    @cmd(name='create users', permissions=['admin'], description='__doc__')
    async def cmd_create_users(self):
        """Create given users. """

        server_users = await self._restapi.get_users()
        arguments = self._get_arguments(self._command_method.command_name)
        users_info = [user_info_raw.split() for user_info_raw in arguments]
        response = ''

        for user_info in users_info:
            user_name = user_info[0].replace('@', '')
            user_in_base = await User.query.where(User.name == user_name).gino.first()
            user_id = ''

            for server_user_values in server_users.values():
                if user_name == server_user_values['username']:
                    user_id = server_user_values['_id']

            if user_id == '':
                response += f'\n@{user_name} - User does not exist in Rocket.Chat'
            elif not user_in_base:
                try:
                    birth_date = (datetime.strptime(user_info[1], '%d.%m.%Y').date() if
                                  len(user_info) == 2 else None)
                except ValueError:
                    response += f'\n@{user_name} - Invalid date format'
                    continue

                await User.create(user_id=user_id, name=user_name, birth_date=birth_date)
                response += f'\n@{user_name} - Success'
            else:
                response += f'\n@{user_name} - User exist'

        await self._write_command_msg(response)

    @cmd(name='delete users', permissions=['admin'], description='__doc__')
    async def cmd_delete_users(self):
        """Delete given users. """

        arguments = self._get_arguments(self._command_method.command_name)
        users_info = [user_info_raw.split() for user_info_raw in arguments]
        response = ''

        for user_info in users_info:
            user_name = user_info[0].replace('@', '')
            user_in_base = await User.query.where(User.name == user_name).gino.first()

            if user_in_base:
                await user_in_base.delete()
                response += f'\n@{user_name} - Success'
            else:
                response += f'\n@{user_name} - User does not exist in base'

        await self._write_command_msg(response)

    @cmd(name='update users', permissions=['admin'], description='__doc__')
    async def cmd_update_users(self):
        """Receive all user in chat and updates information in database. """

        server_users = await self._restapi.get_users()
        for user in server_users.values():
            if self.check_user_status(user):
                if not await User.get(user['_id']):
                    await User.create(user_id=user['_id'], name=user['username'], fwd=date.today())

        await self._write_command_msg('Success')

    @cmd(name='get fwd list', permissions=['admin'], description='__doc__')
    async def cmd_get_fwd_list(self):
        """Receive first working day of all users. """

        users_in_base = await User.query.gino.all()
        response = '_First working days list_'

        for user in users_in_base:
            try:
                response += f'\n@{user.name} joined our team **{user.fwd.strftime("%d.%m.%Y")}**'
            except AttributeError:
                response += f'\n@{user.name} date not given'

        await self._write_command_msg(response)

    @cmd(name='set users fwd', permissions=['admin'], description='__doc__')
    async def cmd_set_users_fwd(self):
        """Set first working day to given users. """

        arguments = self._get_arguments(self._command_method.command_name)
        users_info = [user_info_raw.split() for user_info_raw in arguments]
        response = ''

        for user_info in users_info:
            user_name = user_info[0].replace('@', '')
            user_in_base = await User.query.where(User.name == user_name).gino.first()

            if not user_in_base:
                response += f'\n@{user_name} - User does not exist in base'
            else:
                try:
                    fwd = datetime.strptime(user_info[1], '%d.%m.%Y').date()
                except ValueError:
                    response += f'\n@{user_name} - Invalid date format'
                    continue
                except IndexError:
                    response += f'\n@{user_name} - Date of first working day not given'
                    continue

                await user_in_base.update(fwd=fwd).apply()
                response += f'\n@{user_name} - Success'

        await self._write_command_msg(response)


class DialogsMixin(DialogsBase, ABC):
    """Contains methods for communication Rocket.Chat user and HappyBirthder. """

    def __init__(self):
        super().__init__()

        self._dialogs_methods = self._get_dialog_methods()

    async def dialog_get_birth_date(self, message):
        """Receive user birth date. """

        if re.match(r'^\d\d\.\d\d\.\d\d\d\d$', message):
            try:
                birth_date = datetime.strptime(message, '%d.%m.%Y').date()
                user = await User.get(self._ctx.user.id)

                if user:
                    await user.update(birth_date=birth_date).apply()
                    await self._write_command_msg(settings.SET_BIRTHDAY_RESPONSE)
                    await self._restapi.write_msg(
                        f'All right, @{user.name} birthday was specified!',
                        settings.BIRTHDAY_LOGGING_CHANNEL)
            except ValueError:
                await self._write_command_msg('Hey! This date does not exist. Please, try again.')
