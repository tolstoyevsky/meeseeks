"""Module contains functionality for interaction with Rocket.Chat RestAPI. """

import json
from typing import Any

from aiohttp import ClientSession, ClientResponse

from meeseeks import settings
from meeseeks.type import UserInfo


class RestAPI:
    """Contains method for interaction with Rocket.Chat RestAPI. """

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

    async def get_rooms(self) -> dict[str, str]:
        """Receive dict of rooms names and ids. """

        response = await self.make_request(settings.ROOMS_GET_REQUEST, 'get')
        rooms_dict: dict[str, str] = {}
        for room in response['update']:
            if 'name' in room:
                rooms_dict[room['name']] = room['_id']

        return rooms_dict

    async def get_group_users(self, group_name: str) -> list[dict[str, str]]:
        """Receive list users of group. """

        response = await self.make_request(
            f'{settings.GROUPS_MEMBERS_GET_REQUEST}?roomName={group_name}', 'get'
        )
        users_list: list[dict[str, str]] = response['members']

        return users_list

    async def invite_user_to_group(self, group_id: str, user_id: str) -> dict[str, Any]:
        """Invite one user or bulk users to group. """

        msg: str = json.dumps({
            'roomId': group_id,
            'userId': user_id,
        })

        return await self.make_request(f'{settings.GROUPS_INVITE_POST_REQUEST}', 'post', msg)

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

    async def create_group(self, name: str, users: list) -> dict[str, Any]:
        """Create group. """

        msg: str = json.dumps({
            'name': name,
            'members': users,
        })

        return await self.make_request(settings.GROUPS_CREATE_POST_REQUEST, 'post', msg)

    async def delete_group(self, name: str) -> dict[str, Any]:
        """Delete group. """

        msg: str = json.dumps({
            'roomName': name,
        })

        return await self.make_request(settings.GROUPS_DELETE_POST_REQUEST, 'post', msg)

    async def get_group_info(self, name: str) -> dict[str, Any]:
        """Receives info about group. """

        response = await self.make_request(
            f'{settings.GROUP_INFO_GET_REQUEST}?roomName={name}', 'get',
        )
        group_info: dict[str, Any] = response['group']

        return group_info

    async def set_online_status(self) -> dict[str, Any]:
        """Set online status for bot. When bot will turn off, status will change to offline. """

        msg: str = json.dumps({
            'username': settings.USER_NAME,
            'status': 'online',
        })

        return await self.make_request(settings.USERS_SET_STATUS_REQUEST, 'post', msg)
