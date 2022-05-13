"""Module containing functionality for interaction with Rocket.Chat REST API. """

import json

from meeseeks import settings
from meeseeks.restapi import RestAPI as RestAPIBase


class RestAPI(RestAPIBase):
    """Provide functionality for interaction with Rocket.Chat REST API. """

    async def write_attachments_msg(self, title, text, room_id):
        """Sends message to chat with attachments. """

        msg = json.dumps({
            'channel': room_id,
            'text': '_Please vote using reactions_',
            'alias': settings.ALIAS,
            'attachments': [{
                'title': 'Variants:',
                'fields': [
                    {
                        'short': False,
                        'title': title,
                        'value': text
                    }
                ],
            }]
        })

        return await self.make_request(settings.CHAT_MESSAGE_POST_REQUEST, 'post', msg)
