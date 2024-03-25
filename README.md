# Бот стилист WildBerries

Для настройки бота необходимо:
- Переименовать `.env.example` в `.env` и заполнить API бота, API ChatGPT, DB-URL
- Переименовать `redis_example.conf` в `redis.conf`
- Переименовать `docker-compose_example.conf` в `docker-compose.conf` и заполнить конфигурацию БД в согласованности с .env

Для запуска бота:
- `sudo docker-compose build`
- `sudo docker-compose up`

Для завершения работы бота:
- Терминировать процесс в консоли с помощью CTRL + C или `kill -2 PID`, указав PID процесса docker-compose
- `sudo docker-compose down`

