# json_downloader
json_downloader
Скрипт для сохранения резульататов селекта джсонов из базы тарники.  

Корректируем переменные окружения в файле docker-compose.yaml 
Корректировать строчки после комментариев.
Добавляем скл-запрос в request.sql

собираем docker-compose
docker-compose build

запусаем docker-compose
docker-compose up -d

смотрим что запущен, копируем CONTAINER ID
docker ps -a

запускаем контейнер 
docker exec -it <CONTAINER ID> sh

запускаем скрипт 
python main.py

в контейнере результат находится в папке /opt/result
