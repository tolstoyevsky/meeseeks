"""Module containing functionality for interaction with Rocket.Chat REST API. """

import json
from typing import Any

from aiohttp import ClientSession, ClientResponse

from meeseeks import settings
from meeseeks.type import UserInfo


class RestAPI:
    """Provide functionality for interaction with Rocket.Chat REST API. """

    def __init__(self, headers: dict[str, str]):
        self._headers: dict[str, str] = headers

    async def make_request(
            self, restapi_method: str, method: str, data: str | None = None,
    ) -> dict[str, Any]:
        """Sends async http request. """

        url: str = settings.ROCKET_CHAT_API + restapi_method
        async with ClientSession(raise_for_status=True) as session:
            response_raw: ClientResponse = await session.request(
                method,
                url=url,
                headers=self._headers,
                data=data,
            )
            response: dict[str, Any] = await response_raw.json()

            return response

    async def get_users(self) -> dict[str, dict[str, Any]]:
        """Receive all users. """

        response = await self.make_request(settings.USERS_LIST_REQUEST, 'get')
        return {user['_id']: user for user in response['users']}

    async def get_user_info(self, user_id: str) -> UserInfo:
        """Receive information about certain user. """

        response = await self.make_request(f'{settings.USERS_INFO_REQUEST}?userId={user_id}', 'get')
        user: UserInfo = response['user']

        return user

    async def get_rooms(self, command: bool = False) -> dict[str, str] | list[str]:
        """Receive all rooms ids. """

        response = await self.make_request(settings.ROOMS_GET_REQUEST, 'get')

        if command:
            rooms_dict: dict[str, str] = {}
            for room in response['update']:
                if 'name' in room:
                    rooms_dict[room['name']] = room['_id']

            return rooms_dict

        rooms_list: list[str] = []
        for room in response['update']:
            rooms_list.append(room['_id'])

        return rooms_list

    async def write_msg(self, text: str, rid: str) -> dict[str, Any]:
        """Sends message to chat. """

        msg: str = json.dumps({
            'channel': rid,
            'text': text,
            'alias': settings.ALIAS,
        })

        return await self.make_request(settings.CHAT_MESSAGE_POST_REQUEST, 'post', msg)

    async def add_reaction(self, msg_id: str, emoji: str, should_react: bool) -> dict[str, Any]:
        """Add or remove reaction on message in chat. """

        msg: str = json.dumps({
            'messageId': msg_id,
            'emoji': emoji,
            'shouldReact': should_react,
        })

        return await self.make_request(settings.CHAT_REACT_POST_REQUEST, 'post', msg)

    async def create_private_room(self, name: str, users: list) -> dict[str, Any]:
        """Create private room. """

        msg: str = json.dumps({
            'name': name,
            'members': users,
        })

        return await self.make_request(settings.GROUPS_CREATE_POST_REQUEST, 'post', msg)

    async def delete_private_room(self, name: str) -> dict[str, Any]:
        """Delete private room. """

        msg: str = json.dumps({
            'roomName': name,
        })

        return await self.make_request(settings.GROUPS_DELETE_POST_REQUEST, 'post', msg)
