"""Settings for meeseeks project. """

import os

from dotenv import load_dotenv

from meeseeks.defaults import *  # pylint: disable=wildcard-import, unused-wildcard-import

load_dotenv()

# Standard settings
ALIAS = os.getenv('ALIAS')

ROCKET_CHAT_API_V1 = os.environ['ROCKET_CHAT_API_V1']

PASSWORD = os.environ['PASSWORD']

USER_NAME = os.environ['USER_NAME']

CONNECT_ATTEMPTS = int(os.getenv('CONNECT_ATTEMPTS', '5'))

HELLO_RESPONSE = os.getenv('HELLO_RESPONSE', 'Hello my friend')

TIME_ZONE = os.getenv('TIME_ZONE', 'Europe/Moscow')
