from unittest import mock

from aiohttp import ClientResponseError

from meeseeks import RestAPI
from tests.base import BaseTestClass
from tests.server_responses import (
    CHAT_POST_MESSAGE_SUCCESS_RESPONSE,
    CHAT_REACT_POST_SUCCESS_RESPONSE,
    GROUPS_CREATE_POST_SUCCESS_RESPONSE,
    GROUPS_DELETE_POST_SUCCESS_RESPONSE,
    GROUPS_INVITE_POST_SUCCESS_RESPONSE,
)


class TestRestAPI(BaseTestClass):
    """Tests of RestAPI class. """

    @mock.patch('meeseeks.settings.USERS_LIST_REQUEST', '/users.list_500/')
    def test_fail_make_request(self):
        """Test of failure make_request method. """

        @self.async_case
        async def body():
            with self.assertRaises(ClientResponseError):
                await RestAPI({}).get_users()

    def test_invite_user_to_group(self):
        """Test of success invite_user_to_group method. """

        @self.async_case
        async def body():
            response = await RestAPI({}).invite_user_to_group('test', 'X2gR7ZHZdmsrTSDRK')
            self.assertEqual(response, GROUPS_INVITE_POST_SUCCESS_RESPONSE)

    def test_get_users(self):
        """Test of success get_users method."""

        @self.async_case
        async def body():
            response = await RestAPI({}).get_users()
            result = {
                'X2gR7ZHZdmsrTSDRK': {
                    '_id': 'X2gR7ZHZdmsrTSDRK',
                    'emails': [{'address': 'test@mail.com', 'verified': False}],
                    'status': 'offline',
                    'active': True,
                    'roles': ['user', 'admin'],
                    'name': 'Test',
                    'lastLogin': '2022-05-01T09:27:55.359Z',
                    'username': 'test',
                    'nameInsensitive': 'test'
                }
            }

            self.assertEqual(response, result)

    def test_get_user_info(self):
        """Test of success get_users method. """

        @self.async_case
        async def body():
            response = await RestAPI({}).get_user_info('X2gR7ZHZdmsrTSDRK')
            result = {
                '_id': 'X2gR7ZHZdmsrTSDRK',
                'createdAt': '2022-01-11T16:17:01.382Z',
                'services': {},
                'emails': [{'address': 'admin@mail.com', 'verified': False}],
                'type': 'user',
                'status': 'online',
                'active': True,
                'roles': ['user', 'admin'],
                'name': 'Test',
                'lastLogin': '2022-05-01T20:23:16.801Z',
                'statusConnection': 'online',
                'utcOffset': 3,
                'username': 'test',
                'statusText': '',
                'requirePasswordChange': False,
                'canViewAllInfo': True
            }

            self.assertEqual(response, result)

    def test_get_rooms(self):
        """Test of success get_rooms method. """

        @self.async_case
        async def body():
            response = await RestAPI({}).get_rooms()
            result = {'general': 'GENERAL'}

            self.assertEqual(response, result)

    def test_get_group_users(self):
        """Test of success get_group_users method. """

        @self.async_case
        async def body():
            response = await RestAPI({}).get_group_users('test')
            result = [{
                '_id': 'ucPgkuQptW4TTqYH2',
                'username': 'test',
                'status': 'offline',
                '_updatedAt': '2022-07-05T13:47:16.392Z',
                'name': 'Test',
            }]

            self.assertEqual(response, result)

    def test_write_msg(self):
        """Test of success write_msg method. """

        @self.async_case
        async def body():
            response = await RestAPI({}).write_msg('Hello my friend', 'GENERAL')
            self.assertEqual(response, CHAT_POST_MESSAGE_SUCCESS_RESPONSE)

    def test_add_reaction(self):
        """Test of success add_reaction method. """

        @self.async_case
        async def body():
            response = await RestAPI({}).add_reaction('nESwxuPygMksAapZb', ':zero:', True)
            self.assertEqual(response, CHAT_REACT_POST_SUCCESS_RESPONSE)

    def test_create_group(self):
        """Test of success create_group method. """

        @self.async_case
        async def body():
            response = await RestAPI({}).create_group('test', ['test'])
            self.assertEqual(response, GROUPS_CREATE_POST_SUCCESS_RESPONSE)

    def test_delete_group(self):
        """Test of success delete_group method. """

        @self.async_case
        async def body():
            response = await RestAPI({}).delete_group('test')
            self.assertEqual(response, GROUPS_DELETE_POST_SUCCESS_RESPONSE)
