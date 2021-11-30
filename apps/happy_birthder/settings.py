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
BIRTHDAY_CHANNEL_TTL = int(os.getenv('BIRTHDAY_CHANNEL_TTL', '3'))

BIRTHDAY_LOGGING_CHANNEL = os.getenv('BIRTHDAY_LOGGING_CHANNEL')

CREATE_BIRTHDAY_CHANNELS = os.getenv('CREATE_BIRTHDAY_CHANNELS', '').lower() == 'true'

COMPANY_NAME = os.environ['COMPANY_NAME']

GREETINGS_RESPONSE = os.getenv(
    'GREETINGS_RESPONSE',
    f'Welcome to {COMPANY_NAME}!'
)

NOTIFY_SET_BIRTH_DATE = os.getenv(
    'NOTIFY_SET_BIRTH_DATE',
    'Hmm…\nIt looks like you forgot to set the date of birth.'
    '\nPlease enter it (DD.MM.YYYY).'
)

NUMBER_OF_DAYS_IN_ADVANCE = int(os.getenv('NUMBER_OF_DAYS_IN_ADVANCE', '7'))

PERSONS_WITHOUT_BIRTHDAY_RESPONSE = os.getenv('PERSONS_WITHOUT_BIRTHDAY_RESPONSE',
                                              'These persons did not provide date of birth.')

SET_BIRTHDAY_RESPONSE = os.getenv(
    'SET_BIRTHDAY_RESPONSE',
    'I memorized you birthday, well done! :wink:'
)

# TenorAPI
_CONGRATULATION_PHRASES = os.getenv('CONGRATULATION_PHRASES')
CONGRATULATION_PHRASES = (_CONGRATULATION_PHRASES.split(',') if _CONGRATULATION_PHRASES
                          else CONGRATULATION_PHRASES)

TENOR_API_KEY = os.environ['TENOR_API_KEY']

TENOR_API_URL = os.getenv('TENOR_API_URL', 'https://api.tenor.com/v1/')

TENOR_IMAGE_LIMIT = int(os.getenv('TENOR_IMAGE_LIMIT', '5'))

_TENOR_SEARCH_TERM = os.getenv('TENOR_SEARCH_TERM')
TENOR_SEARCH_TERM = (_TENOR_SEARCH_TERM.split(',') if _TENOR_SEARCH_TERM else TENOR_SEARCH_TERM)


_TENOR_BLACKLISTED_GIF_IDS = os.getenv('TENOR_BLACKLISTED_GIF_IDS')
TENOR_BLACKLISTED_GIF_IDS = (_TENOR_BLACKLISTED_GIF_IDS.split(',')
                             if _TENOR_BLACKLISTED_GIF_IDS else [])

# Scheduler
HB_CRONTAB = os.getenv('HB_CRONTAB', '0 7 * * *')

SCHEDULER_SETTINGS = {
    'apscheduler.timezone': TIME_ZONE,
}
