# Проектная работа 4 спринта
## Асинхронный API для кинотеатра

### Запуск проекта

1. Клонируйте репозиторий:

    ```sh
    git clone https://github.com/samoilovartem/sprint_1_async_api.git
    ```

2. Для сборки и запуска контейнеров перейдите в папку с проектом и запустите docker-compose:

    ```sh
    docker-compose -f docker-compose.yml up -d --build
    ```
Данные шаги запустят сервисы с приложением на Python + FastAPI, ETL, Postgres, ElasticSearch и Redis.


### Документация к API

0. Swagger: http://localhost:8000/api/openapi
1. Показать популярные фильмы: http://localhost:8000/api/v1/movies?sort=-imdb_rating&page_number=0&page_size=20
2. Поиск по фильмам: http://localhost:8000/api/v1/movies/search?query=star%20wars&page_number=0&page_size=20
3. Подробная информация о фильме: http://localhost:8000/api/v1/movies/c35dc09c-8ace-46be-8941-7e50b768ec33
4. Показать похожие фильмы: http://localhost:8000/api/v1/movies/c35dc09c-8ace-46be-8941-7e50b768ec33/similar
5. Популярные фильмы в жанре: http://localhost:8000/api/v1/movies/genres/120a21cf-9097-479e-904a-13dd7198c1dd
6. Показать список жанров: http://localhost:8000/api/v1/genres?page_number=0&page_size=20
7. Информация о жанре: http://localhost:8000/api/v1/genres/120a21cf-9097-479e-904a-13dd7198c1dd
8. Показать список персон: http://localhost:8000/api/v1/persons?page_number=0&page_size=20
9. Поиск по персонам: http://localhost:8000/api/v1/persons/search?query=Steven%20Melching&page_number=0&page_size=20
10. Данные о персоне: http://localhost:8000/api/v1/persons/84c192fa-7178-4a57-bdd6-a81716e7bb40


### Тесты

Для запуска тестов необходимо перейти в папку tests/functional/ и запустить docker-compose (предварительно подставив .env-файл, к примеру .env.example).
При запуске контейнера сперва произойдёт ожидание подключения к elasticsearch и redis, а затем - запуск тестов.
Если всё хорошо, то в консоли вы увидите примерно следующее:

`Connecting to Elasticsearch at elasticsearch:9200...`

`Elasticsearch connected`

`Connecting to Redis at redis:6379...`

`Redis connected`

`============================= test session starts ==============================`

`platform linux -- Python 3.11.2, pytest-7.2.2, pluggy-1.0.0`

`rootdir: /tests/functional`

`plugins: asyncio-0.12.0`

`collected 24 items`

`src/test_genres.py ....                                                  [ 16%]`

`src/test_movies.py .............                                         [ 70%]`

`src/test_persons.py .......                                              [100%]`

`======================== 24 passed, 4 warnings in 0.40s ========================`
