# Бот стилист WildBerries

Для настройки бота необходимо:
- Переименовать `.env.example` в `.env` и заполнить API бота и API ChatGpt
- Переименовать `redis_example.conf` в `redis.conf`

Для запуска бота:
- `sudo docker-compose build`
- `sudo docker-compose up`

Для завершения работы бота:
- Терменировать процесс в консоли с помощью CTRL + C или `kill -2 PID`, указав PID процесса docker-compose
- `sudo docker-compose down`