# Дипломный проект Foodgram

![workflow](https://github.com/Ingv4r/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Для ревью
домен: https://ingvar-foodgram.ddns.net/ \
ip сервера: 158.160.23.165

Суперюзер: \
login: admin \
password: admin

## Описание проекта

Foodgram (Продуктовый помощник) — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд. Список можно будет скачать в pdf формате.

## Запуск проекта локально

### Клонирование проекта

На примере git bash

```
git clone https://github.com/Ingv4r/foodgram-project-react.git
```

### Создание вирутального окружения Python

Версия питона 3.9

```
cd foodgram-project-react
python -3.9 -m venv venv
source venv/Scripts/activate # на git bash или unix подобных ос (Linux, MacOS)
venv\Scripts\activate.bat # на Windows
cd backend/
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Изменение базы данных

Проект работает на базе данных PostgeSQL. Для тестирования проекта на локальном компьютере рекомендовано изменить базу данных в настройке проекта на SQLite

в settings.py изменить строки DATABASES
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

#### Запуск проекта

Миграции в базу данных

```
python manage.py makemigrationns
python manage.py migrate
```

Создание суперюзера для того, чтобы можно было зайти на /admin 

```
python manage.py createsuperuser # Затем заполнение полей
```

Перед запуском сервера можно загрузить в базу данных подготовленные ингредиенты

```
python manage.py write_from_csv_to_db
```

Запуск сервера

```
python manage.py runserver
```

#### Результат

Будет запущена backend-часть проекта.

API - http://127.0.0.1:8000/api/ 

Админка - http://127.0.0.1:8000/admin/



## Запуск проекта в контейнерах Docker

### Клонирование проекта

```
git clone https://github.com/Ingv4r/foodgram-project-react.git
сd backend/
```

### Создание .env-файла

На production обязательно заменить значение SECRET_KEY

С помощью команды ниже в папке будет создан .env-файл

```
SECRET_KEY=<django secret key>
MY_HOST=<your hostname>
POSTGRES_USER=<postgres username>
POSTGRES_PASSWORD=<secret password>
POSTGRES_DB=foodgram
DB_NAME=<name of db>
DB_HOST=db
DB_PORT=5432
```

### Сборка контейенеров

Соберите контейнеры и запустите их

```
cd ..
docker compose up -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend python manage.py createsuperuser # Заполнение полей суперюзера
```

### Заполнение базы данных

Заполните БД подготовленными данными

```
docker compose exec backend python manage.py write_from_csv_to_db
```

### Результат

Будет запущен весь проект.

API - http://localhost/

Redoc - http://localhost/api/docs/

Frontend - http://localhost/

Админка - http://localhost/admin/


## Автор backend и docker части проекта

Игорь Кузьмин, backend-разработчик на python
