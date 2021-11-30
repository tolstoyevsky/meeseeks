"""Module containing functionality for interaction with Rocket.Chat RESTful API. """

import json

from meeseeks import settings


class RealTimeAPI:
    """Provide functionality for interaction with Rocket.Chat RESTful API. """

    def __init__(self, request, websocket):
        self._request = request
        self._websocket = websocket

    def connect(self):
        """Connects to RealtimeAPI. """

        self._request = json.dumps({
            'msg': 'connect',
            'version': '1',
            'support': ['1']
        })

        return self._websocket.send(self._request)

    def login(self):
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

    def pong(self):
        """Answers to 'ping' message. """

        self._request = json.dumps({'msg': 'pong'})

        return self._websocket.send(self._request)

    @staticmethod
    def stream_room_messages_msg(rid):
        """Subscribes to certain room. """

        return json.dumps({
            'msg': 'sub',
            'id': rid,
            'name': 'stream-room-messages',
            'params': [rid, True],
        })

    async def stream_all_messages(self):
        """Subscribes to all messages. """

        await self._websocket.send(json.dumps({
            'msg': 'sub',
            'id': 'sub-all',
            'name': 'stream-room-messages',
            'params': ['__my_messages__', True],
            })
        )

    async def stream_room_messages(self, rids: list):
        """Subscribes to given room list. """

        for rid in rids:
            await self._websocket.send(self.stream_room_messages_msg(rid))
