# Corporate Microblogging Service

Backend корпоративного сервиса микроблогов, разработанный в рамках итогового проекта курса Python Advanced.

Сервис предоставляет API для публикации коротких сообщений, загрузки изображений, лайков, подписок и формирования пользовательской ленты.

## Возможности

Приложение позволяет:

- создавать твиты;
- удалять собственные твиты;
- загружать изображения;
- прикреплять изображения к твитам;
- ставить лайки;
- удалять лайки;
- подписываться на пользователей;
- отписываться от пользователей;
- получать ленту пользователей, на которых выполнена подписка;
- сортировать ленту по популярности;
- получать собственный профиль;
- получать профиль другого пользователя;
- работать через HTTP-заголовок `api-key`.

Регистрация пользователей через API не предусмотрена. Пользователи создаются автоматически при первом запуске приложения.

## Технологии

- Python 3.11
- FastAPI
- PostgreSQL 15
- SQLAlchemy
- Pydantic
- Docker Compose
- Pytest
- Ruff

## Структура проекта

```text
twitter_clone/
├── app/
│   ├── routers/
│   │   ├── media.py
│   │   ├── tweets.py
│   │   └── users.py
│   ├── services/
│   │   ├── media_service.py
│   │   ├── tweet_service.py
│   │   └── user_service.py
│   ├── media/
│   ├── static/
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── seed.py
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Запуск проекта

Для запуска необходимо установить:

- Docker;
- Docker Compose;
- Git.

Склонируйте проект:

```bash
git clone <ссылка-на-ваш-GitLab-репозиторий>
cd twitter_clone
```

Создайте файл `.env` в корне проекта:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/mydb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=mydb
```

Запустите приложение:

```bash
docker-compose up -d
```

Также можно использовать современный вариант команды:

```bash
docker compose up -d
```

Проверьте состояние контейнеров:

```bash
docker compose ps
```

Остановить приложение:

```bash
docker compose down
```

Остановить приложение и удалить данные PostgreSQL:

```bash
docker compose down -v
```

> Команда `docker compose down -v` удаляет volume базы данных и все сохранённые данные. Используйте её только для полного сброса проекта.

## Адреса приложения

Frontend:

```text
http://localhost:8001/
```

Swagger:

```text
http://localhost:8001/docs
```

OpenAPI JSON:

```text
http://localhost:8001/openapi.json
```

## Тестовые пользователи

После запуска автоматически создаются пользователи:

| Пользователь | API-ключ |
|---|---|
| Alice | `alice-key` |
| Bob | `bob-key` |
| Charlie | `charlie-key` |

API-ключ передаётся в заголовке:

```text
api-key: alice-key
```

## API

### Создание твита

```http
POST /api/tweets
```

Заголовок:

```text
api-key: alice-key
```

Тело запроса:

```json
{
  "tweet_data": "Мой первый твит",
  "tweet_media_ids": []
}
```

Ответ:

```json
{
  "result": true,
  "tweet_id": 1
}
```

### Загрузка изображения

```http
POST /api/medias
```

Заголовок:

```text
api-key: alice-key
```

Тип запроса:

```text
multipart/form-data
```

Имя поля:

```text
file
```

Поддерживаются изображения:

- JPEG;
- PNG;
- GIF;
- WebP;
- AVIF.

Ответ:

```json
{
  "result": true,
  "media_id": 1
}
```

### Удаление собственного твита

```http
DELETE /api/tweets/{tweet_id}
```

Заголовок:

```text
api-key: alice-key
```

Ответ:

```json
{
  "result": true
}
```

Пользователь не может удалить твит другого пользователя.

### Добавление лайка

```http
POST /api/tweets/{tweet_id}/likes
```

Заголовок:

```text
api-key: alice-key
```

Ответ:

```json
{
  "result": true
}
```

### Удаление лайка

```http
DELETE /api/tweets/{tweet_id}/likes
```

Заголовок:

```text
api-key: alice-key
```

### Подписка на пользователя

```http
POST /api/users/{user_id}/follow
```

Заголовок:

```text
api-key: alice-key
```

### Отписка от пользователя

```http
DELETE /api/users/{user_id}/follow
```

Заголовок:

```text
api-key: alice-key
```

### Получение ленты

```http
GET /api/tweets
```

Заголовок:

```text
api-key: alice-key
```

Лента содержит твиты пользователей, на которых подписан текущий пользователь.

Твиты сортируются:

1. по количеству лайков в порядке убывания;
2. при одинаковом количестве лайков — по дате создания.

### Получение собственного профиля

```http
GET /api/users/me
```

Заголовок:

```text
api-key: alice-key
```

### Получение профиля пользователя

```http
GET /api/users/{user_id}
```

Заголовок:

```text
api-key: alice-key
```

## Формат ошибок

При ошибке API возвращает:

```json
{
  "result": false,
  "error_type": "HTTPException",
  "error_message": "Tweet not found"
}
```

Пример ошибки авторизации:

```json
{
  "result": false,
  "error_type": "HTTPException",
  "error_message": "Invalid api-key"
}
```

## Тестирование

Запустить тесты:

```bash
docker compose run --rm tests
```

Ожидаемый результат:

```text
9 passed
```

Запустить тесты с покрытием:

```bash
docker compose run --rm tests pytest --cov=app --cov-report=term-missing
```

Текущее покрытие проекта составляет примерно 83%.

## Проверка линтером

Проверить код:

```bash
docker compose run --rm tests ruff check app tests
```

Автоматически исправить форматирование импортов:

```bash
docker compose run --rm tests ruff check app tests --fix
```

Отформатировать проект:

```bash
docker compose run --rm tests ruff format app tests
```

## Хранение данных

PostgreSQL использует Docker volume:

```yaml
pgdata:/var/lib/postgresql/data
```

Поэтому данные сохраняются между командами:

```bash
docker compose down
docker compose up -d
```

Для удаления данных используется:

```bash
docker compose down -v
```

## Лицензия

Учебный проект, созданный в рамках курса Python Advanced.