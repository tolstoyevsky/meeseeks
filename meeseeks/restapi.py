"""Module containing functionality for interaction with Rocket.Chat REST API. """

import json

from aiohttp import ClientSession

from meeseeks import settings


class RestAPI:
    """Provide functionality for interaction with Rocket.Chat REST API. """

    def __init__(self, headers):
        self._headers = headers

    async def make_request(self, restapi_method, method, data=None):
        """Sends async http request. """

        url = settings.HOST + '/api/v1' + restapi_method
        async with ClientSession() as session:
            response_raw = await session.request(method, url=url, headers=self._headers, data=data)
            response_raw.raise_for_status()

            return await response_raw.json()

    async def get_users(self):
        """Receive all users. """

        response = await self.make_request('/users.list', 'get')

        return {user['_id']: user for user in response['users']}

    async def get_user_info(self, user_id):
        """Receive information about certain user. """

        response = await self.make_request(f'/users.info?userId={user_id}', 'get')

        return response['user']

    async def get_rooms(self, command=None):
        """Receive all rooms ids. """

        response = await self.make_request('/rooms.get', 'get')

        if command:
            rooms = {}
            for room in response['update']:
                if 'name' in room:
                    rooms[room['name']] = room['_id']
            return rooms

        rooms = []
        for room in response['update']:
            rooms.append(room['_id'])

        return rooms

    async def write_msg(self, text, rid):
        """Sends message to chat. """

        msg = json.dumps({
            'channel': rid,
            'text': text,
            'alias': settings.ALIAS
        })

        return await self.make_request('/chat.postMessage', 'post', msg)

    async def add_reaction(self, msg_id, emoji, should_react):
        """Add or remove reaction on message in chat. """

        msg = json.dumps({
            'messageId': msg_id,
            'emoji': emoji,
            'shouldReact': should_react,
        })

        return await self.make_request('/chat.react', 'post', msg)

    async def create_private_room(self, name, users):
        """Create private room. """

        msg = json.dumps({
            'name': name,
            'members': users
        })

        return await self.make_request('/groups.create', 'post', msg)

    async def delete_private_room(self, name):
        """Delete private room. """

        msg = json.dumps({
            'roomName': name,
        })

        return await self.make_request('/groups.delete', 'post', msg)
