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
  * Fetching a random GIF from [GIPHY](https://giphy.com) before writing a birthday message to a birthday boy/girl.
    The bot picks a random tag from `GIPHY_SEARCH_TERMS`, searches GIPHY with `GIPHY_RATING`,
    filters out `GIPHY_BLACKLISTED_GIF_IDS`, and attaches one random GIF from the results.
    If GIPHY returns nothing or the request fails after `GIPHY_MAX_ATTEMPTS` retries,
    the message is still sent without a GIF.
    By default, `GIPHY_SEARCH_TERMS` is [darth vader birthday](https://giphy.com/search/darth%20vader%20birthday), [game of thrones birthday](https://giphy.com/search/game%20of%20thrones%20birthday), [futurama birthday](https://giphy.com/search/futurama%20birthday), [harry potter birthday](https://giphy.com/search/harry%20potter%20birthday), [king of the hill birthday](https://giphy.com/search/king%20of%20the%20hill%20birthday), [lana del rey birthday](https://giphy.com/search/lana%20del%20rey%20birthday), [mad hatter birthday](https://giphy.com/search/mad%20hatter%20birthday), [pulp fiction birthday](https://giphy.com/search/pulp%20fiction%20birthday), [rick and morty birthday](https://giphy.com/search/rick%20and%20morty%20birthday), [rocket birthday](https://giphy.com/search/rocket%20birthday), [sheldon birthday](https://giphy.com/search/sheldon%20birthday), [simpson birthday](https://giphy.com/search/simpson%20birthday), [the simpsons birthday](https://giphy.com/search/the%20simpsons%20birthday), [tmnt birthday](https://giphy.com/search/tmnt%20birthday), [south park birthday](https://giphy.com/search/south%20park%20birthday).
  * Writing birthday messages to `#general`.
  * Reminding users of the upcoming birthdays one day and a few days in advance. It's possible to specify how long before the event occurs the reminder should be triggered.
  * Creating private channels in advance and inviting all the users to the channels except the birthday boys/girls for the purpose of discussing the presents for them. Expired channels are automatically removed.
- Work anniversaries
  * Memorizing the date when a new employee logs in to Rocket.Chat for the first time (the date is equal to the first working day in the company).
  * Congratulating employees on anniversary of working in the company (congratulations are written to `#general`).

## How to use crontab expression

**Parameters:**

- second – (0-59)
- minute - (0-59)
- hour – (0-23)
- day of month - (1-31)
- month – (1-12)
- day of week – number or name of weekday (0-6 or MON,TUE,WED,THU,FRI,SAT,SUN)

## Project configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ALIAS` | Name of your bot | |
| `ROCKET_CHAT_API` | Rocket.Chat address | |
| `PASSWORD` | Password of your bot | |
| `USER_NAME` | User name of your bot | |
| `CONNECT_ATTEMPTS` | Number of attempts to start on failure | |
| `GIPHY_API_KEY` | Client key for GIPHY API access. This is the only **mandatory** parameter. | |
| `GIPHY_API_URL` | GIPHY API base URL. | `https://api.giphy.com/v1/` |
| `GIPHY_BLACKLISTED_GIF_IDS` | A comma separated list of the GIPHY GIF IDs which will be excluded when choosing one from the search results. | |
| `GIPHY_IMAGE_LIMIT` | Fetches up to the specified number of results, but not more than **50**. | 5 |
| `GIPHY_RATING` | Content rating for GIPHY search results. Allowed values: `g`, `pg`, `pg-13`, `r`. | `g` |
| `GIPHY_SEARCH_TERMS` | A comma separated list of tags which will be used when fetching GIFs from GIPHY. | See [Features](#features) |
| `GIPHY_MAX_ATTEMPTS` | Number of retries with a different random tag before giving up on fetching a GIF. | 3 |
| `CREATE_BIRTHDAY_CHANNELS` | Specifies whether to create the birthday channels for the purpose of discussing presents for birthday boys/girls. All the users are invited to the channel except the birthday boy/girl. | False |
| `BIRTHDAY_CHANNEL_BLACKLIST` | A comma separated list of the users which won't be invited to the birthday channel when it's created. | |
| `BIRTHDAY_CHANNEL_TTL` | Specifies TTL (time to live) of the birthday channel. | 3 |
| `BIRTHDAY_LOGGING_CHANNEL` | Allows specifying the name of the channel which is used for logging the events related to birth dates. The bot must be in the channel (see the Prerequisites sections). | hr |
| `COMPANY_NAME` | Allows specifying the company name which is used in the welcome message. | CusDeb |
| `HB_CRONTAB` | Allows specifying the frequency with which the script checks for nearest birthdays and writes birthday messages to users. The value of this parameter must follow the Cron Format. | 0 0 7 * * * |
| `NUMBER_OF_DAYS_IN_ADVANCE` | Sets (in days) how long before the event occurs the reminder will be triggered. | 7 |
| `RESPOND_TO_DM` | Allows you to create polls using command | False |
| `REMINDERS_LIST` | JSON string that specifies all reminders that will be sent to specfy channel according to schedule. Format of string: `[{"crontab": "0 30 8 * * MON,FRI", "text": "Today is a good day", "channel": "general"}]` | [] |
