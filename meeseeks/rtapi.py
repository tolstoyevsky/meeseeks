"""Module containing functionality for interaction with Rocket.Chat REST API. """

import json
from websockets import WebSocketClientProtocol  # pylint: disable=no-name-in-module

from meeseeks import settings


class RealTimeAPI:
    """Provide functionality for interaction with Rocket.Chat RealTime API. """

    def __init__(self, request: str, websocket: WebSocketClientProtocol):
        self._request: str = request
        self._websocket: WebSocketClientProtocol = websocket

    def connect(self) -> WebSocketClientProtocol:
        """Connects to RealtimeAPI. """

        self._request = json.dumps({
            'msg': 'connect',
            'version': '1',
            'support': ['1']
        })

        return self._websocket.send(self._request)

    def login(self) -> WebSocketClientProtocol:
        """Login user. """

        self._request = json.dumps({
            'msg': 'method',
            'method': 'login',
            'id': settings.RC_REALTIME_LOGIN,
            'params': [{
                'user': {'username': settings.USER_NAME},
                'password': settings.PASSWORD,
            }]
        })

        return self._websocket.send(self._request)

    def pong(self) -> WebSocketClientProtocol:
        """Answers to 'ping' message. """

        self._request = json.dumps({'msg': 'pong'})

        return self._websocket.send(self._request)

    @staticmethod
    def stream_room_messages_msg(rid: str) -> str:
        """Subscribes to certain room. """

        return json.dumps({
            'msg': 'sub',
            'id': rid,
            'name': 'stream-room-messages',
            'params': [rid, True],
        })

    async def stream_all_messages(self) -> WebSocketClientProtocol:
        """Subscribes to all messages. """

        await self._websocket.send(json.dumps({
            'msg': 'sub',
            'id': 'sub-all',
            'name': 'stream-room-messages',
            'params': ['__my_messages__', True],
            })
        )

    async def stream_room_messages(self, rids: list[str]) -> None:
        """Subscribes to given room list. """

        for rid in rids:
            await self._websocket.send(self.stream_room_messages_msg(rid))
