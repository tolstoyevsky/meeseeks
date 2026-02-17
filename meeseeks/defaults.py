"""Module contains default variables. """

# Installed apps are launched by Meeseeks
INSTALLED_APPS = (
    'meeseeks.MeeseeksBaseApp',
    'apps.HappyBirthder',
    'apps.Holidays',
    'apps.VoteOrDie',
    'apps.Reminder'
)

RC_REALTIME_LOGIN = 'login'

CHAT_MESSAGE_POST_REQUEST = '/chat.postMessage'

CHAT_REACT_POST_REQUEST = '/chat.react'

GROUPS_CREATE_POST_REQUEST = '/groups.create'

GROUPS_DELETE_POST_REQUEST = '/groups.delete'

GROUPS_INVITE_POST_REQUEST = '/groups.invite'

GROUPS_MEMBERS_GET_REQUEST = '/groups.members'

GROUP_INFO_GET_REQUEST = '/groups.info'

ROOMS_GET_REQUEST = '/rooms.get'

USERS_LIST_REQUEST = '/users.list?count=0'

USERS_INFO_REQUEST = '/users.info'

USERS_SET_STATUS_REQUEST = '/users.setStatus'

TRACEBACK_ALERT_MSG = (
    "Oh! An unexpected error! :what:\n"
    "I wasn’t ready for this! Nobody prepared me for this!\n"
    "Here it is:"
    "\n```\n{}\n```\n"
    "Please fix it so I can complete my mission!"
)

TRACEBACK_ALERT_GROUP = 'HR'
