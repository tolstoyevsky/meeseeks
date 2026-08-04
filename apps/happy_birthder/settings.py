"""Settings for HappyBirthder application. """
import os

from apps.happy_birthder.defaults import *  # pylint: disable=wildcard-import,unused-wildcard-import

load_dotenv()

# Postgres
PG_NAME = os.environ['PG_NAME']

PG_PASSWORD = os.environ['PG_PASSWORD']

PG_PORT = os.environ['PG_PORT']

PG_HOST = os.environ['PG_HOST']

PG_USER = os.environ['PG_USER']

# HappyBirthder
BIRTHDAY_CHANNEL_TTL = int(os.getenv('BIRTHDAY_CHANNEL_TTL', '7'))

BIRTHDAY_LOGGING_CHANNEL = os.getenv('BIRTHDAY_LOGGING_CHANNEL', 'hr')

CHECK_USERS_AVATARS = os.getenv('CHECK_USERS_AVATARS', '').lower() == 'true'

CREATE_BIRTHDAY_CHANNELS = os.getenv('CREATE_BIRTHDAY_CHANNELS', '').lower() == 'true'

COMPANY_NAME = os.environ['COMPANY_NAME']

GREETINGS_RESPONSE = os.getenv(
    'GREETINGS_RESPONSE',
    f'Welcome to {COMPANY_NAME}!'
)

NOTIFY_SET_AVATAR = os.getenv(
    'NOTIFY_SET_AVATAR',
    "Oh, I see you didn't set your avatar!\nPlease, do it as soon as possible. :grin:",
)

NOTIFY_SET_BIRTH_DATE = os.getenv(
    'NOTIFY_SET_BIRTH_DATE',
    'Hmm…\nIt looks like you forgot to set the date of birth.'
    '\nPlease enter it (DD.MM.YYYY).'
)

NUMBER_OF_DAYS_IN_ADVANCE = int(os.getenv('NUMBER_OF_DAYS_IN_ADVANCE', '7'))

PERSONS_WITHOUT_BIRTHDAY_RESPONSE = os.getenv('PERSONS_WITHOUT_BIRTHDAY_RESPONSE',
                                              'These persons did not provide date of birth.')

PERSONS_WITHOUT_AVATAR_RESPONSE = os.getenv(
    'PERSONS_WITHOUT_AVATAR_RESPONSE',
    "These users didn't set their avatars.",
)

SET_BIRTHDAY_RESPONSE = os.getenv(
    'SET_BIRTHDAY_RESPONSE',
    'I memorized you birthday, well done! :wink:'
)

# GIPHY
_CONGRATULATION_PHRASES = os.getenv('CONGRATULATION_PHRASES')
CONGRATULATION_PHRASES = (_CONGRATULATION_PHRASES.split(',') if _CONGRATULATION_PHRASES
                          else CONGRATULATION_PHRASES)

GIPHY_API_KEY = os.environ['GIPHY_API_KEY']

GIPHY_API_URL = os.getenv('GIPHY_API_URL', 'https://api.giphy.com/v1/')

GIPHY_IMAGE_LIMIT = int(os.getenv('GIPHY_IMAGE_LIMIT', '5'))

_GIPHY_SEARCH_TERMS = os.getenv('GIPHY_SEARCH_TERMS')
GIPHY_SEARCH_TERMS = (_GIPHY_SEARCH_TERMS.split(',') if _GIPHY_SEARCH_TERMS else GIPHY_SEARCH_TERMS)

GIPHY_RATING = os.getenv('GIPHY_RATING', 'g')

GIPHY_MAX_ATTEMPTS = int(os.getenv('GIPHY_MAX_ATTEMPTS', '3'))

_GIPHY_BLACKLISTED_GIF_IDS = os.getenv('GIPHY_BLACKLISTED_GIF_IDS')
GIPHY_BLACKLISTED_GIF_IDS = (_GIPHY_BLACKLISTED_GIF_IDS.split(',')
                             if _GIPHY_BLACKLISTED_GIF_IDS else [])

# Scheduler
HB_CRONTAB = os.getenv('HB_CRONTAB', '0 0 7 * * *')
