"""Module configure alembic.ini file from docker container. """

import configparser

from apps.happy_birthder import settings


def main():
    """Reading alembic.ini and set config variables. """

    config = configparser.ConfigParser()
    config.read('alembic.ini')
    config.set('alembic', 'sqlalchemy.url',
               f'postgresql://{settings.PG_USER}:{settings.PG_PASSWORD}@{settings.PG_HOST}'
               f':{settings.PG_PORT}/{settings.PG_NAME}')

    with open('alembic.ini', 'w', encoding='utf8') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    main()
