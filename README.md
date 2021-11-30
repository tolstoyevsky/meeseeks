# meeseeks-happy-birthder


## Установка зависимостей

* Python 3.10. Если на машине установлена более старая версия, то рекомендуется воспользоваться [pyenv](https://github.com/pyenv/).
* Docker, инструкцию по установке которого можно найти [здесь](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-engine---community-1).
* virtualenv, который можно установить, выполнив `sudo apt-get install virtualenv`.

## Разворачивание на машине разработчика

### Виртуальное окружение:

* Создаем виртуальное окружение, активируем его и устанавливаем зависимости:
```bash
virtualenv -ppython3.10 meeseeks-env
source ./meeseeks-env/bin/activate
cd meeseeks
pip3 install -r requirements.txt
```

### Настройка модуля happy_birthder

* Поднимаем Docker контейнер и создаем базу если нет:

`docker run --rm -p 5432:5432 -v $(pwd)/_db:/var/lib/postgresql/data --name happy_birthder_base -e POSTGRES_DB=happy_birthder_base -e POSTGRES_PASSWORD=secret -d postgres`

* Накатываем миграции модуля:
```bash
cd apps/happy_birthder
env PYTHONPATH=$(pwd)/../.. alembic upgrade head
```

### Запуск проекта

* Запуск из главной директории проекта

`env PYTHONPATH=$(pwd) python3 manage.py`

## Конфигурирование проекта

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TENOR_API_KEY` | Сlient key for privileged API access. This is the only **mandatory** parameter. | |
| `TENOR_BLACKLIST` | A comma separated list of the GIFs ids which will be excluded when choosing one from the list returned by Tenor. If the script randomly chooses a GIF from the response which belongs to the blacklist, the script sends one more request to Tenor. | |
| `TENOR_IMAGE_LIMIT` | Fetches up to the specified number of result, but not more than **50**. | 5 |