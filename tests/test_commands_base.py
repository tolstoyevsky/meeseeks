from unittest import mock

from meeseeks import settings, RestAPI, MeeseeksBaseApp
from meeseeks.commands.base import CommandsBase, Communication
from meeseeks.context import ChangedRoomMessageCtx
from tests.base import BaseTestClass


class TestCommunication(BaseTestClass):
    """Tests of Communication class. """

    def test_get_response_msg(self):
        """Test of success _get_response_msg method. """

        communication = Communication()
        communication._ctx = ChangedRoomMessageCtx()
        communication._ctx.msg = f'@{settings.USER_NAME} hello'
        result = communication._get_response_msg()

        self.assertEqual(result, ' hello')

    def test_fail_get_response_msg(self):
        """Test of failure _get_response_msg method. """

        communication = Communication()
        with self.assertRaises(AttributeError):
            communication._get_response_msg()

    def test_write_command_msg(self):
        """Test of success _write_command_msg method. """

        @self.async_case
        async def body():
            communication = Communication()
            communication._ctx = ChangedRoomMessageCtx()
            communication._ctx.room.id = 'general'
            communication._restapi = RestAPI({})
            with mock.patch('meeseeks.restapi.RestAPI.write_msg') as write_msg:
                await communication._write_command_msg('hello')

            write_msg.assert_called_once()

    def test_fail_write_command_msg(self):
        """Test of failure _write_command_msg method. """

        @self.async_case
        async def body():
            communication = Communication()
            communication._restapi = RestAPI({})
            with self.assertRaises(AttributeError):
                await communication._write_command_msg('hello')


class TestCommandsBase(BaseTestClass):
    """Tests of CommandsBase class. """

    def test_fail_get_command_methods(self):
        """Test of failure _get_command_methods method. """

        commands_base = CommandsBase()
        self.assertIn(commands_base.cmd_help, commands_base._command_methods)

    def test_normalize_msg(self):
        """Test of success _normalize_msg method. """

        commands_base = CommandsBase
        result = commands_base._normalize_msg(' TEST, test ')

        self.assertEqual(result, 'test, test')

    def test_get_arguments(self):
        """Test of success _get_arguments method. """

        commands_base = CommandsBase()
        commands_base._ctx = ChangedRoomMessageCtx()
        commands_base._ctx.msg = f'@{settings.USER_NAME} test arg1, arg2,arg3, ARG4'
        result = commands_base._get_arguments('test')

        self.assertEqual(result, ['arg1', 'arg2', 'arg3', 'arg4'])

    def test_empty_get_arguments(self):
        """Test of success _get_arguments method with no args in message. """

        commands_base = CommandsBase()
        commands_base._ctx = ChangedRoomMessageCtx()
        commands_base._ctx.msg = f'@{settings.USER_NAME} test'
        result = commands_base._get_arguments('test')

        self.assertEqual(result, [])

    def test_check_permissions(self):
        """Test of success check_permissions method. """

        @self.async_case
        async def body():
            commands_base = CommandsBase()
            commands_base._ctx = ChangedRoomMessageCtx()
            commands_base._ctx.user.id = 'X2gR7ZHZdmsrTSDRK'
            commands_base._restapi = RestAPI({})
            result = await commands_base.check_permissions(['user'])

            self.assertEqual(result, True)

    def test_empty_check_permissions(self):
        """Tests of success check_permissions method with no user role in args. """

        @self.async_case
        async def body():
            commands_base = CommandsBase()
            commands_base._ctx = ChangedRoomMessageCtx()
            commands_base._ctx.user.id = 'X2gR7ZHZdmsrTSDRK'
            commands_base._restapi = RestAPI({})
            result = await commands_base.check_permissions()

            self.assertEqual(result, True)

    def test_fail_check_permissions(self):
        """Tests of failure check_permissions method. """

        @self.async_case
        async def body():
            commands_base = CommandsBase()
            commands_base._ctx = ChangedRoomMessageCtx()
            commands_base._ctx.user.id = 'X2gR7ZHZdmsrTSDRK'
            commands_base._restapi = RestAPI({})
            result = await commands_base.check_permissions(['test'])

            self.assertEqual(result, False)


class TestDialogsBase(BaseTestClass):
    """Tests of DialogsBase class. """

    def test_get_dialog_methods(self):
        """Test of success _get_dialog_methods method. """

        dialogs_base = MeeseeksBaseApp()
        self.assertIn(dialogs_base.dialog_hello, dialogs_base._dialogs_methods)
