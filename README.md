Сервис сокращения ссылок, реализованный на FastAPI - позволяет создавать короткие ссылки, управлять ими и получать статистику использования.

Развернутый сервис доступен по адресу:  
https://fastapi-link-shortener.onrender.com/docs

## Функциональность API

Сервис предоставляет следующие возможности:

1. Создание короткой ссылки.
2. Перенаправление на оригинальный URL по короткому коду.
3. Обновление оригинального URL для существующей короткой ссылки.
4. Удаление короткой ссылки.
5. Получение статистики по ссылке.
6. Поиск ссылок по оригинальному URL.
7. Создание кастомного alias для короткой ссылки.
8. Указание срока жизни ссылки (expires_at).
9. Регистрация и авторизация пользователей.
10. Ограничение изменения и удаления ссылок только для авторизованных пользователей.
11. Кэширование популярных ссылок с использованием Redis.




## Стек

- FastAPI
- SQLAlchemy
- SQLite
- Redis
- JWT авторизация
- Docker
- Docker Compose


## База данных

Основным хранилищем данных является SQLite.

База данных содержит следующие основные таблицы:

### users
Хранит информацию о пользователях.

Поля:
- id
- username
- email
- password_hash
- created_at

### links
Хранит информацию о сокращенных ссылках.

Поля:
- id
- original_url
- short_code
- created_at
- expires_at
- click_count
- last_used_at
- owner_id


## Кэширование

Для ускорения работы используется Redis.

В Redis кэшируются:
- соответствия short_code → original_url

Кэш очищается при:
- обновлении ссылки
- удалении ссылки.


## Инструкция по запуску

1. Клонировать репозиторий


git clone https://github.com/muradpo/fastapi-link-shortener.git

cd fastapi-link-shortener


2. Создать виртуальное окружение


python -m venv venv
source venv/bin/activate


3. Установить зависимости


pip install -r requirements.txt


4. Запустить приложение


uvicorn app.main:app --reload


Документация будет доступна


http://127.0.0.1:8000/docs



## Запуск через Docker

1. Клонировать репозиторий


git clone https://github.com/muradpo/fastapi-link-shortener.git

cd fastapi-link-shortener


2. Запустить контейнеры


docker compose up --build


Сервис будет доступен


http://localhost:8000/docs

## Эндпоинты API

### Регистрация

- POST /register
- Создает нового пользователя

Пример запроса


{
"username": "polina",
"email": "polina@test.com
",
"password": "123456"
}



### Авторизация

- POST /login
- Возвращает JWT токен

Пример запроса


username=polina
password=123456



### Создание короткой ссылки

- POST /links/shorten

Пример


{
"original_url": "https://google.com
"
}



### Создание ссылки с кастомным alias


{
"original_url": "https://google.com
",
"custom_alias": "mygoogle"
}



### Создание ссылки со сроком жизни


{
"original_url": "https://google.com
",
"custom_alias": "mygoogle",
"expires_at": "2026-03-06T18:35:00"
}



### Переход по короткой ссылке

- GET /links/{short_code}
- Перенаправляет на оригинальный URL


### Обновление ссылки

- PUT /links/{short_code}
- Требует авторизацию

Пример


{
"original_url": "https://newsite.com
"
}



### Удаление ссылки

- DELETE /links/{short_code}
- Требует авторизацию


### Статистика ссылки

- GET /links/{short_code}/stats

Возвращает

- оригинальный URL
- дату создания
- количество переходов
- дату последнего использования


### Поиск по оригинальному URL

- GET /links/search?original_url={url}

Пример


GET /links/search?original_url=https://google.com



## Используемые технологии

- FastAPI
- SQLAlchemy
- SQLite
- Redis
- JWT авторизация
- Docker
- Docker Compose


## База данных

### Таблица users

- id
- username
- email
- password_hash
- created_at

### Таблица links

- id
- original_url
- short_code
- created_at
- expires_at
- click_count
- last_used_at
- owner_id


## Кэширование

- используется Redis
- кэшируется соответствие short_code → original_url
- кэш очищается при обновлении или удалении ссылки


