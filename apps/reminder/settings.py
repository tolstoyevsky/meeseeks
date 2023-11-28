"""Module contains Reminder application settings. """

import json

from apps.reminder.defaults import *  # pylint: disable=wildcard-import, unused-wildcard-import

# Reminder settings
REMINDERS_LIST = json.loads(os.getenv('REMINDERS_LIST', '[]'))
