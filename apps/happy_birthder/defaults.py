"""Module contains HappyBirthder application default variables. """

from meeseeks.settings import *  # pylint: disable=wildcard-import, unused-wildcard-import

ANNIVERSARY = 'I`m glad to announce that today is day of anniversary for some of us! :tada:'

CONGRATULATION_PHRASES = [
    'May this year bring with it all the success and fulfillment your heart desires.',

    'Happy birthday to you, a person who is smart, good looking, '
    'and funny and reminds me a lot of myself.',

    'Your best years are still ahead of you.',

    'We know we’re getting old when the only thing we '
    'want for our birthday is not to be reminded of it.',

    'Wishing you all the great things in life, hope this day '
    'will bring you an extra share of all that makes you happiest.',

    'Birthdays are filled with yesterday’s memories, today’s joys, and tomorrow’s dreams.',
]

SCHEDULER_SETTINGS = {
    'apscheduler.timezone': TIME_ZONE,
}

TENOR_SEARCH_TERM = [
    'darthvaderbirthday',
    'gameofthronesbirthday',
    'futuramabirthday',
    'harrypotterbirthday',
    'kingofthehillbirthday',
    'lanadelreybirthday',
    'madhatterbirthday',
    'pulpfictionbirthday',
    'rickandmortybirthday',
    'rocketbirthday',
    'sheldonbirthday',
    'simpsonbirthday',
    'thesimpsonsbirthday',
    'tmntbirthday',
]

GREETINGS_RESPONSE = 'Welcome to CusDeb Solutions! :tada: Emm... where was I? Oh!'

NOTIFY_SET_AVATAR = (
    'Oh, I see you didn`t set your avatar!\nPlease, do it as soon as possible. :grin:'
)

NOTIFY_SET_BIRTH_DATE = (
    'Hmm…\nIt looks like you forgot to set the date of birth.\nPlease enter it (DD.MM.YYYY).'
)

PERSONS_WITHOUT_BIRTHDAY_RESPONSE = 'These persons did not provide date of birth.'

PERSONS_WITHOUT_AVATAR_RESPONSE = 'These users didn`t set their avatars.'

SET_BIRTHDAY_RESPONSE = 'I memorized you birthday, well done! :wink:'
