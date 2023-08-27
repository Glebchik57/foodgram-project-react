#  Дипломный проект - FOODGRAM
## _Продуктовый помошник_

сайт доступен по https://thebestfoodgram.hopto.org/

## Технологии

 - Python 3.9
 - Django 3.2
 - Docker
 - Nginx
 - gunicorn
 - PostgreSQL
 
 ## Возможности:

 - Регистрация пользователей
 - Создание, просмотр и редактирование рецептов
 - Подписки на пользователей
 - Добавление лучших рецептов в избранное
 - формирование и скачивание списка покупок

## Как запустить проект на локальный компьютер:
Клонировать репозиторий и перейти в него в командной строке:
```
git@github.com:Glebchik57/foodgram-project-react.git
```
Подключиться к удалённому серверу:
```
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
```
Установить Docker на сервер:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
Скопировать на сервер файл docker-compose.production.yml:
```
 scp -i path_to_SSH/SSH_name docker-compose.yml username@server_ip:/home/username/taski/docker-compose.yml
 _или сделать это вручную_
```
Создать файл .env:
```
sudo touch .env
```
В файле .env прописать следующие: 
```
SECRET_KEY
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
DB_HOST
DB_PORT
```
Запустить Docker Compose в режиме демона:
```
sudo docker compose -f docker-compose.yml up -d
```
Выполнить миграции, соберите статические файлы бэкенда:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```
Откоректировать конфиг nginx на сервере:
```
sudo nano /etc/nginx/sites-enabled/default
```

Ну вот и все! Добро пожаловать в увлекательный мир кулинарии.

## Автор:
_Севостьянов Глеб_