"""Module contains responses for requests to Rocket.Chat mock server. """

CHAT_POST_MESSAGE_SUCCESS_RESPONSE = {
    'ts': 1651854972660,
    'channel': 'GENERAL',
    'message': {
        'alias': '',
        'msg': 'Hello my friend',
        'attachments': [],
        'parseUrls': True,
        'groupable': False,
        'ts': '2022-05-06T16:36:12.616Z',
        'u': {'_id': 'ucPgkuQptW4TTqYH2', 'username': 'meeseeks', 'name': 'Mr.Meeseeks'},
        'rid': 'GENERAL',
        '_id': '64pxfnKAcg59sa69z',
        '_updatedAt': '2022-05-06T16:36:12.656Z',
        'urls': [],
        'mentions': [],
        'channels': [],
        'md': [{
            'type': 'PARAGRAPH',
            'value': [{'type': 'PLAIN_TEXT', 'value': 'Hello my friend'}]}
        ]},
    'success': True
}

CHAT_REACT_POST_SUCCESS_RESPONSE = {'success': True}

GROUPS_CREATE_POST_SUCCESS_RESPONSE = {
    'group': {
        '_id': 'ptapxCJSdphttDu77',
        'fname': 'test',
        'customFields': {},
        'name': 'test',
        't': 'p',
        'msgs': 0,
        'usersCount': 2,
        'u': {'_id': 'ucPgkuQptW4TTqYH2', 'username': 'meeseeks'},
        'ts': '2022-05-06T18:00:35.572Z',
        'ro': False,
        'default': False,
        'sysMes': True,
        '_updatedAt': '2022-05-06T18:00:35.617Z'},
    'success': True
}

GROUPS_DELETE_POST_SUCCESS_RESPONSE = {'success': True}

GROUPS_INVITE_POST_SUCCESS_RESPONSE = {
    'group': {
        '_id': 'ZAi5cBANwKx7MMZeQ',
        'fname': 'birthday-of-test',
        'customFields': {},
        'description': '',
        'broadcast': False,
        'encrypted': False,
        'name': 'birthday-of-test',
        't': 'p',
        'msgs': 9,
        'usersCount': 3,
        'u': {
            '_id': 'X2gR7ZHZdmsrTSDRK',
            'username': 'test'
        },
        'ts': '2022-07-05T12:37:42.161Z',
        'ro': False,
        'default': False,
        'sysMes': True,
        '_updatedAt': '2022-07-05T14:39:07.900Z',
        'lastMessage': {
            '_id': 'tKugNP57x4vp2AkL7',
            'rid': 'ZAi5cBANwKx7MMZeQ',
            'msg': '@meeseeks',
            'ts': '2022-07-05T12:42:30.490Z',
            'u': {
                '_id': 'X2gR7ZHZdmsrTSDRK',
                'username': 'test',
                'name': 'Test'
            },
            '_updatedAt': '2022-07-05T12:42:30.558Z',
            'urls': [],
            'mentions': [{
                '_id': 'ucPgkuQptW4TTqYH2',
                'username': 'meeseeks',
                'name': 'Mr.Meeseeks',
                'type': 'user'
            }],
            'channels': [],
            'md': [{
                'type': 'PARAGRAPH',
                'value': [{
                    'type': 'MENTION_USER',
                    'value': {
                        'type': 'PLAIN_TEXT',
                        'value': 'meeseeks'
                    }
                }]
            }]
        },
        'lm': '2022-07-05T12:42:30.490Z'
    },
    'success': True
}

GROUPS_MEMBERS_GET_SUCCESS_RESPONSE = {
    'members': [{
        '_id': 'ucPgkuQptW4TTqYH2',
        'username': 'test',
        'status': 'offline',
        '_updatedAt': '2022-07-05T13:47:16.392Z',
        'name': 'Test',
    }],
    'count': 2,
    'offset': 0,
    'total': 2,
    'success': True,
}

INTERNAL_SERVER_ERROR_RESPONSE = {
    'code': 1,
    'message': 'Internal server error (see proxy logs for more info)',
}

ROOMS_GET_SUCCESS_RESPONSE = {
    'update': [{
        '_id': 'GENERAL',
        'ts': '2022-01-11T16:16:16.826Z',
        't': 'c',
        'name': 'general',
        'usernames': [],
        'usersCount': 7,
        'default': True,
        '_updatedAt': '2022-04-23T16:51:38.235Z',
        'lm': '2022-04-23T16:51:38.161Z',
        'lastMessage': {
            '_id': 'HXYrKiNh7SEBsbgHw',
            'rid': 'GENERAL',
            'msg': '@meeseeks help',
            'ts': '2022-04-23T16:51:38.161Z',
            'u': {'_id': 'X2gR7ZHZdmsrTSDRK', 'username': 'test', 'name': 'Test'},
            '_updatedAt': '2022-04-23T16:51:38.226Z',
            'urls': [],
            'mentions': [{
                '_id': 'ucPgkuQptW4TTqYH2',
                'username': 'meeseeks',
                'name': 'Mr.Meeseeks',
                'type': 'user'
            }],
            'channels': [],
            'md': [{
                'type': 'PARAGRAPH', 'value': [{
                    'type': 'MENTION_USER',
                    'value': {'type': 'PLAIN_TEXT', 'value': 'meeseeks'}
                }, {
                    'type': 'PLAIN_TEXT',
                    'value': ' help'}]
            }]
        }
    }],
    'remove': [],
    'success': True
}

USER_INFO_GET_SUCCESS_RESPONSE = {
    'user': {
        '_id': 'X2gR7ZHZdmsrTSDRK',
        'createdAt': '2022-01-11T16:17:01.382Z',
        'services': {},
        'emails': [{'address': 'admin@mail.com', 'verified': False}],
        'type': 'user',
        'status': 'online',
        'active': True,
        'roles': ['user', 'admin'],
        'name': 'Test',
        'lastLogin': '2022-05-01T20:23:16.801Z',
        'statusConnection': 'online',
        'utcOffset': 3,
        'username': 'test',
        'statusText': '',
        'requirePasswordChange': False,
        'canViewAllInfo': True
    },
    'success': True
}

USERS_LIST_GET_SUCCESS_RESPONSE = {
    'users': [{
        '_id': 'X2gR7ZHZdmsrTSDRK',
        'emails': [{'address': 'test@mail.com', 'verified': False}],
        'status': 'offline',
        'active': True,
        'roles': ['user', 'admin'],
        'name': 'Test',
        'lastLogin': '2022-05-01T09:27:55.359Z',
        'username': 'test',
        'nameInsensitive': 'test',
    }],
    'count': 1,
    'offset': 0,
    'total': 1,
    'success': True
}

USERS_LIST_GET_SUCCESS_RESPONSE_WITHOUT_BOT_PERMISSIONS = {
    'users': [{
        '_id': 'X2gR7ZHZdmsrTSDRK',
        'status': 'away',
        'active': True,
        'name': 'Test',
        'username': 'test',
        'nameInsensitive': 'test'
    }],
    'count': 8,
    'offset': 0,
    'total': 8,
    'success': True
}
