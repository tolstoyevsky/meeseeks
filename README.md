# meeseeks-happy-birthder


## Dependencies

* Python 3.10. If older version is installed on the machine, it is recommended to use [pyenv](https://github.com/pyenv/).
* Docker, installation instructions can be found [here](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-engine---community-1).
* virtualenv, which can be installed by running `sudo apt-get install virtualenv`.

## Installation

### Virtual environment:

* Create virtual environment, activate it and install requirements:
```bash
virtualenv -ppython3.10 meeseeks-env
source ./meeseeks-env/bin/activate
cd meeseeks
pip3 install -r requirements.txt
```

### happy_birthder setup

* Run Docker container and create the database if not:

`docker run --rm -p 5432:5432 -v $(pwd)/_db:/var/lib/postgresql/data --name happy_birthder_base -e POSTGRES_DB=happy_birthder_base -e POSTGRES_PASSWORD=secret -d postgres`

* Apply migrations to module database:
```bash
cd apps/happy_birthder
env PYTHONPATH=$(pwd)/../.. alembic upgrade head
```

### Run of the project

* Run from main project directory

`env PYTHONPATH=$(pwd) python3 manage.py`

## Features

The functionality of the script is divided into two parts: handling birthdays and work anniversaries.
- Birthdays
  * Asking new employees to specify their date birth and reminding them about it if they ignore this request for some reason.
  * Fetching a random GIF from [Tenor](https://tenor.com) before writing a birthday message to a birthday boy/girl. The `TENOR_SEARCH_TERM` environment variable stores a comma separated list of the tags which will be used when fetching GIFs. By default, the value of the variable is '[darthvaderbirthday](https://tenor.com/search/darthvaderbirthday), [futuramabirthday](https://tenor.com/search/futuramabirthday), [gameofthronesbirthday](https://tenor.com/search/gameofthronesbirthday), [harrypotterbirthday](https://tenor.com/search/harrypotterbirthday), [kingofthehillbirthday](https://tenor.com/search/kingofthehillbirthday), [lanadelreybirthday](https://tenor.com/search/lanadelreybirthday), [madhatterbirthday](https://tenor.com/search/madhatterbirthday), [pulpfictionbirthday](https://tenor.com/search/pulpfictionbirthday), [rickandmortybirthday](https://tenor.com/search/rickandmortybirthday), [rocketbirthday](https://tenor.com/search/rocketbirthday), [sheldonbirthday](https://tenor.com/search/sheldonbirthday), [simpsonbirthday](https://tenor.com/search/simpsonbirthday), [thesimpsonsbirthday](https://tenor.com/search/thesimpsonsbirthday), [tmntbirthday](https://tenor.com/search/tmntbirthday)'.
  * Writing birthday messages to `#general`.
  * Reminding users of the upcoming birthdays one day and a few days in advance. It's possible to specify how long before the event occurs the reminder should be triggered.
  * Providing fault tolerance:
    + if Tenor is for some reason unavailable right now, the script will try to request it a number of times with delays;
    + if all the requests failed, users will receive their birthday messages anyway.
  * Creating private channels in advance and inviting all the users to the channels except the birthday boys/girls for the purpose of discussing the presents for them. Expired channels are automatically removed.
- Work anniversaries
  * Memorizing the date when a new employee logs in to Rocket.Chat for the first time (the date is equal to the first working day in the company).
  * Congratulating employees on anniversary of working in the company (congratulations are written to `#general`).

## Конфигурирование проекта

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ALIAS` | Name of your bot | |
| `ROCKET_CHAT_API` | Rocket.Chat address | |
| `PASSWORD` | Password of your bot | |
| `USER_NAME` | User name of your bot | |
| `CONNECT_ATTEMPTS` | Number of attempts to start on failure | |
| `TENOR_API_KEY` | Сlient key for privileged API access. This is the only **mandatory** parameter. | |
| `TENOR_BLACKLIST` | A comma separated list of the GIFs ids which will be excluded when choosing one from the list returned by Tenor. If the script randomly chooses a GIF from the response which belongs to the blacklist, the script sends one more request to Tenor. | |
| `TENOR_IMAGE_LIMIT` | Fetches up to the specified number of result, but not more than **50**. | 5 |
| `TENOR_SEARCH_TERM` | A comma separated list of tags which will be used when fetching GIFs from Tenor. | See [Features](#features) |
| `CREATE_BIRTHDAY_CHANNELS` | Specifies whether to create the birthday channels for the purpose of discussing presents for birthday boys/girls. All the users are invited to the channel except the birthday boy/girl. | False |
| `BIRTHDAY_CHANNEL_BLACKLIST` | A comma separated list of the users which won't be invited to the birthday channel when it's created. | |
| `BIRTHDAY_CHANNEL_TTL` | Specifies TTL (time to live) of the birthday channel. | 3 |
| `BIRTHDAY_LOGGING_CHANNEL` | Allows specifying the name of the channel which is used for logging the events related to birth dates. The bot must be in the channel (see the Prerequisites sections). | hr |
| `COMPANY_NAME` | Allows specifying the company name which is used in the welcome message. | CusDeb |
| `HB_CRONTAB` | Allows specifying the frequency with which the script checks for nearest birthdays and writes birthday messages to users. The value of this parameter must follow the Cron Format. | 0 0 7 * * * |
| `NUMBER_OF_DAYS_IN_ADVANCE` | Sets (in days) how long before the event occurs the reminder will be triggered. | 7 |
| `RESPOND_TO_DM` | Allows you to create polls using command | False |
