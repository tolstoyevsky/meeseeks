"""Module contains Holidays application settings. """

import os

from apps.holidays.defaults import *  # pylint: disable=wildcard-import,unused-wildcard-import

load_dotenv()

# Holidays settings
CUSTOM_HOLIDAYS = os.getenv('CUSTOM_HOLIDAYS', '')

# Scheduler
HOLIDAYS_CRONTAB_WEEK_BEFORE = os.getenv('HOLIDAYS_CRONTAB_WEEK_BEFORE', '0 0 7 * * *')

HOLIDAYS_CRONTAB_DAY_BEFORE = os.getenv('HOLIDAYS_CRONTAB_DAY_BEFORE', '0 0 18 * * *')
