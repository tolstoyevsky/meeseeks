"""Settings for Holidays application. """

import os

from apps.holidays.defaults import *  # pylint: disable=wildcard-import,unused-wildcard-import

load_dotenv()

# Scheduler
HOLIDAYS_CRONTAB = os.getenv('HOLIDAYS_CRONTAB', '0 0 7 * * *')

SCHEDULER_SETTINGS = {
    'apscheduler.timezone': TIME_ZONE,
}
