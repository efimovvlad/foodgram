Сервер efimovvlat.com
Логин: admin@mail.ru
Пароль: admin

# Проект Foodgram
 
## Описание
 
«Фудграм» — это сайт, на котором пользователи могут публиковать свои рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Зарегистрированным пользователям доступен сервис «Список покупок».
Он позволяет добавлять в корзину список продуктов, которые нужно купить для блюд.
Такой список продуктов (с общим количеством ингредиентов) можно скачать в формате txt.
Страницу любого рецепта можно скопировать при помощи короткой ссылки. 
Рецепты можно фильтровать по тегам.


Сайт доступен по адресу: efimovvlat.com

## Стек используемых технологий
- Python
- Django
- Django Rest Framework
- Docker
- Gunicorn
- Nginx
- PostgreSQL

## Запуск проекта локально
### 1. Клонируем репозиторий на свой компьютер
```
git clone https://github.com/efimovvlad/foodgram.git
```
В корне проекта необходимо создать файл .env со своими данными
```
POSTGRES_USER      #имя юзера в БД PostgreSQL
POSTGRES_PASSWORD  #пароль юзера в БД PostgreSQL
POSTGRES_DB        #имя БД
DB_HOST            #имя контейнера, где запущен сервер БД
DB_PORT            #порт, по которому Django будет обращаться к серверу с БД 
SECRET_KEY         #ваш секретный код из settings.py для Django проекта
DEBUG              #статус режима отладки (default=False)
ALLOWED_HOSTS      #список доступных хостов
```

### 2. Запуск Docker engine
### В корне проекта, где лежит файл docker-compose.yml, выполнить команду:
```
docker compose -f docker-compose.yml up -d

docker compose -f docker-compose.yml exec backend python manage.py makemigrations

docker compose -f docker-compose.yml exec backend python manage.py migrate

docker compose -f docker-compose.yml exec backend python manage.py import_tags

docker compose -f docker-compose.yml exec backend python manage.py import_ingredients
```
Последние команды загружают в БД подготовленный набор необходимых данных (ингредиенты и теги)
Дополнительно можно создать суперпользователя, для доступа к админ-панели сайта, командой:
```
docker compose exec backend python manage.py createsuperuser
```
Также необходимо скопировать статику для админки Django
```
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
```
И скопировать статику в volume static для бэкенда
```
docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

Проект будет доступен по адресу http://localhost
