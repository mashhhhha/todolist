TODOLIST

Приложение для работы с целями и отслеживания прогресса по ним.

Стек:
1. python3.10
2. Django
3. Postgres

Уставновить зависимости:
poetry install

Уставновить зависимости:
на осонове .env.template

Запустить postgres:
docker-compose up -d db

Применить миграции:
./manage.py migrate

Запустить сервер:
./manage.py runserver