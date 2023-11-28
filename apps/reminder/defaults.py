"""Module contains Reminder application default variables. """

from meeseeks.settings import *  # pylint: disable=wildcard-import, unused-wildcard-import

SCHEDULER_SETTINGS = {
    'apscheduler.timezone': TIME_ZONE,
}

REMINDER_MESSAGE_TOPIC = 'I have a reminder for you! :calendar_spiral:\n'
