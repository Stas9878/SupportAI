# SupportAI


Репозиторий создан как финальный проект для моего курса на Stepik — [ссылка](https://stepik.org/a/274734)


**SupportAI** — это веб-сервис на базе FastAPI и LangGraph для автоматической обработки заявок в службу поддержки с использованием AI-агентов.


## Описание


SupportAI принимает пользовательские запросы, анализирует их с помощью цепочки AI-агентов и автоматически:
- **Классифицирует** заявку по категориям (техническая, биллинг, фича, другое)
- **Определяет приоритет** (critical, high, medium, low) на основе срочности
- **Назначает релевантные теги** для быстрой маршрутизации
- **Сохраняет результат** в базу данных и отправляет алерты при критичных проблемах


Проект использует:
- **LangGraph** — фреймворк для построения агентов с состоянием и переходами
- **FastAPI** — современный асинхронный веб-фреймворк для API
- **PostgreSQL + Alembic** — надёжное хранение данных с миграциями
- **Ollama** — локальная LLM для генерации ответов без зависимости от облачных API
- **LangSmith** — трейсинг и мониторинг вызовов LLM
- **Docker** — контейнеризация для воспроизводимого развёртывания


## Возможности


- 🤖 **Автоматическая обработка заявок** через граф агентов с условными переходами
- ♻️ **Восстановление состояния** после сбоев благодаря чекпоинтам в PostgreSQL
- 🔁 **Retry-логика** с экспоненциальной задержкой для устойчивости к временным сбоям
- 🛡️ **Защита от prompt injection** и санитизация пользовательского ввода
- 📊 **Структурированное логирование** в JSON-формате для интеграции с системами мониторинга
- 📱 **Telegram-алерты** для критичных заявок в реальном времени
- 🐳 **Docker-ready** — запуск одной командой со всеми зависимостями
- ✅ **Unit-тесты** для критичных модулей с моками внешних зависимостей


## Структура проекта


```
support-ai/
├── Dockerfile                    # Сборка образа приложения
├── docker-compose.yml            # Запуск с БД и Ollama
├── requirements.txt              # Зависимости Python
├── pytest.ini                    # Конфигурация pytest
├── alembic.ini                   # Конфигурация миграций
│
├── alembic/                      # Миграции базы данных
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── *_initial_schema.py   # Начальная схема БД
│
├── app/                          # Основное приложение
│   ├── main.py                   # Точка входа FastAPI
│   ├── config.py                 # Настройки из переменных окружения
│   ├── logging_config.py         # Централизованное логирование
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── tickets.py        # Эндпоинты для заявок
│   │   │   └── health.py         # Health-check эндпоинты
│   │   └── schemas/
│   │       └── ticket.py         # Pydantic-схемы
│   │
│   ├── agent/                    # Агент на LangGraph
│   │   ├── graph.py              # Сборка графа и переходов
│   │   ├── state.py              # AgentState: схема состояния
│   │   ├── llm.py                # Настройка LLM (Ollama)
│   │   ├── checkpointer.py       # PostgresSaver для чекпоинтов
│   │   ├── retry.py              # Retry-декоратор для LLM
│   │   └── nodes/
│   │       ├── classifier.py     # Классификация заявок
│   │       ├── prioritizer.py    # Определение приоритета
│   │       ├── tagger.py         # Назначение тегов
│   │       ├── saver.py          # Сохранение в БД
│   │       └── alert.py          # Telegram-алерты
│   │
│   ├── db/                       # Работа с базой данных
│   │   ├── base.py               # Базовый класс SQLAlchemy
│   │   ├── session.py            # Фабрика сессий
│   │   └── models/
│   │       ├── ticket.py         # Модель заявки
│   │       └── history.py        # Модель истории изменений
│   │
│   ├── core/
│   │   └── dependencies.py       # Dependency Injection для эндпоинтов
│   │
│   ├── crud/
│   │   └── ticket.py             # CRUD-операции для заявок
│   │
│   └── security/
│       └── sanitizers.py         # Санитизация ввода и защита от injection
│
├── tests/
│   └── test_critical.py          # Unit-тесты критичных модулей
│
└── scripts/                      # Вспомогательные скрипты
    ├── check_env.py              # Проверка переменных окружения
    ├── test_db.py                # Тест подключения к БД
    ├── test_logging.py           # Тест логирования
    ├── test_retry.py             # Тест retry-логики
    ├── test_security.py          # Тест санитизации
    ├── test_checkpoints.py       # Тест чекпоинтов
    └── cleanup_checkpoints.py    # Очистка старых чекпоинтов
```


## Требования


- Python 3.11+
- Docker и Docker Compose (для контейнеризации)
- Ollama с установленной моделью (например, `llama3.1:latest`)
- PostgreSQL 18 (или запуск через Docker)


## Установка


### 1. Клонирование репозитория


```bash
git clone https://github.com/Stas9878/support-ai.git
cd support-ai
```


### 2. Создание виртуального окружения и установка зависимостей


```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```


### 3. Настройка переменных окружения


Создайте файл `.env` в корне проекта на основе `.env.example`

### 4. Запуск миграций базы данных


```bash
alembic upgrade head
```


### 5. Запуск Ollama


Убедитесь, что Ollama запущен и модель загружена:


```bash
# Запуск сервера (если не запущен как сервис)
ollama serve


# В другом терминале: загрузка модели
ollama pull llama3.1:latest
```


### 6. Запуск через Docker Compose (рекомендуется)


```bash
docker compose up --build
```


Сервис будет доступен по адресу: `http://localhost:8000`
Документация API: `http://localhost:8000/docs`


### 7. Запуск локально (без Docker)


```bash
# Убедитесь, что PostgreSQL запущен
# Затем запустите приложение
uvicorn app.main:app --reload
```


## API Эндпоинты


### `GET /health`


Базовая проверка доступности сервиса.


**Ответ:**
```json
{
  "status": "ok",
  "timestamp": "2026-03-29T10:00:00+00:00"
}
```


### `GET /health/ready`


Проверка готовности сервиса (зависимости подключены).


**Ответ (готов):**
```json
{
  "status": "ready",
  "checks": { "database": "ok" }
}
```


### `GET /health/metrics`


Расширенные метрики системы.


**Ответ:**
```json
{
  "status": "ok",
  "metrics": {
    "tickets_24h": 42,
    "by_status": { "new": 10, "in_progress": 25, "resolved": 7 }
  }
}
```


### `POST /tickets/`


Создание новой заявки с обработкой через агента.


**Запрос:**
```json
{
  "thread_id": "user_session_123",
  "user_input": "Не могу войти в аккаунт, ошибка 401"
}
```


**Ответ (успех):**
```json
{
  "id": 1,
  "thread_id": "user_session_123",
  "user_input": "Не могу войти в аккаунт, ошибка 401",
  "category": "technical",
  "priority": "high",
  "tags": ["login", "error"],
  "status": "new",
  "created_at": "2026-03-29T10:00:00"
}
```


### `GET /tickets/{ticket_id}`


Получение заявки по ID.


**Ответ:**
```json
{
  "id": 1,
  "thread_id": "user_session_123",
  "category": "technical",
  "priority": "high",
  "tags": ["login", "error"],
  "status": "in_progress"
}
```


### `GET /tickets/?thread_id=xxx&skip=0&limit=10`


Получение списка заявок для сессии с пагинацией.


**Ответ:**
```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 10
}
```


### `PATCH /tickets/{ticket_id}`


Частичное обновление заявки.


**Запрос:**
```json
{
  "status": "resolved",
  "priority": "low"
}
```


### `DELETE /tickets/{ticket_id}`


Удаление заявки. Возвращает `204 No Content`.


## Как это работает


### Архитектура агента


```
Пользовательский запрос
        ↓
┌─────────────────┐
│   classifier    │ → Категория: technical/billing/feature/other
└────────┬────────┘
         ↓
┌─────────────────┐
│  prioritizer    │ → Приоритет: critical/high/medium/low
└────────┬────────┘
         ↓
┌─────────────────┐
│     tagger      │ → Теги: [login, error, ...] (0-3 шт.)
└────────┬────────┘
         ↓
    ┌────┴────┐
    ↓         ↓
┌───────┐ ┌───────┐
│ alert │ │ saver │ → Критичный? → Telegram
└───┬───┘ └───┬───┘    Обычный → Сохранить в БД
    │         │
    └────┬────┘
         ↓
   Возврат результата
```


### Чекпоинты и восстановление


1. После каждого узла графа состояние сохраняется в PostgreSQL
2. При сбое или перезапуске агент восстанавливается с последнего чекпоинта
3. `thread_id` в `config["configurable"]` обеспечивает изоляцию сессий пользователей


### Безопасность ввода


1. **Проверка длины**: отклонение запросов длиннее `MAX_INPUT_LENGTH`
2. **Injection detection**: блокировка известных паттернов атак
3. **Санитизация**: удаление управляющих символов, нормализация Unicode
4. **Разделение промпта**: инструкция и данные пользователя явно разделены


### Логирование и мониторинг


- **Dev-режим**: читаемый вывод в консоль с цветами
- **Prod-режим**: JSON-формат для интеграции с ELK/CloudWatch
- **LangSmith**: автоматический трейсинг вызовов LLM с метриками
- **Алерты**: Telegram-уведомления для заявок с приоритетом `critical`


## Тестирование


### Запуск всех тестов


```bash
pytest tests/ -v
```


### Запуск только критичных тестов


```bash
pytest tests/test_critical.py -v
```


### Запуск тестов в Docker


```bash
docker compose run --rm app pytest tests/test_critical.py -v
```


### Проверка покрытия


```bash
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html
# Отчёт откроется в browser: htmlcov/index.html
```


## Скрипты для разработки


| Скрипт | Назначение | Запуск |
|--------|------------|--------|
| `check_env.py` | Проверка переменных окружения | `python scripts/check_env.py` |
| `test_db.py` | Тест подключения к БД | `python scripts/test_db.py` |
| `test_logging.py` | Тест логирования | `python scripts/test_logging.py` |
| `test_retry.py` | Тест retry-логики | `python scripts/test_retry.py` |
| `test_security.py` | Тест санитизации | `python scripts/test_security.py` |
| `test_checkpoints.py` | Тест чекпоинтов | `python scripts/test_checkpoints.py` |
| `cleanup_checkpoints.py` | Очистка старых чекпоинтов | `python scripts/cleanup_checkpoints.py --keep 50` |


## Переменные окружения для Docker


При переходе с локальной разработки на Docker измените только эти 4 переменные:


| Переменная | Локально | В Docker |
|------------|----------|----------|
| `DATABASE_URL` | `@localhost:5432` | `@db:5432` |
| `DB_HOST` | `localhost` | `db` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | `http://ollama:11434` |
| `APP_ENV` | `dev` | `prod` |


Остальные настройки (токены, ключи, модель) остаются без изменений.


## Логирование


Логи выводятся в stdout и собираются Docker:


```bash
# Просмотр логов приложения
docker compose logs -f app


# Фильтрация по уровню
docker compose logs -f app | grep ERROR


# Сохранение логов в файл
docker compose logs -f app > logs/app.log
```


В продакшене настройте отправку логов в централизованную систему (ELK, CloudWatch, Loki).


## Troubleshooting


### Ollama недоступен


- Проверьте, что сервер запущен: `ollama serve`
- Убедитесь, что модель загружена: `ollama list`
- Проверьте `OLLAMA_BASE_URL` в `.env` (в Docker: `http://ollama:11434`)


### PostgreSQL недоступен


- Проверьте контейнер: `docker compose ps db`
- Убедитесь, что миграции применены: `alembic upgrade head`
- Проверьте `DATABASE_URL` в `.env`


### Агент возвращает категорию "other"


- Проверьте, не сработала ли валидация (невалидный ответ LLM)
- Убедитесь, что промпт не был заблокирован как injection
- Посмотрите логи: `docker compose logs -f app | grep classifier`


### Telegram-алерты не приходят


- Проверьте `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`
- Убедитесь, что приоритет заявки ≥ `ALERT_PRIORITY_THRESHOLD`
- Проверьте логи: `docker compose logs -f app | grep alert`


## Разработка


### Добавление нового узла в граф


1. Создайте файл в `app/agent/nodes/your_node.py`
2. Реализуйте функцию с сигнатурой `(state: AgentState) -> dict`
3. Добавьте узел в `app/agent/graph.py`:
   ```python
   workflow.add_node("your_node", your_function)
   workflow.add_edge("previous_node", "your_node")
   ```
4. Добавьте логирование и обработку ошибок по аналогии с существующими узлами


### Изменение схемы состояния


1. Обновите `app/agent/state.py` (AgentState)
2. Примените миграции БД при необходимости
3. Обновите узлы, использующие изменённые поля


### Настройка LangSmith


1. Получите API-ключ на [smith.langchain.com](https://smith.langchain.com)
2. Добавьте в `.env`:
   ```env
   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=your_key
   LANGSMITH_PROJECT=support-ai
   ```
3. Перезапустите приложение и проверьте дашборд


## Лицензия


MIT License — используйте, изменяйте и распространяйте проект по своему усмотрению.


## Автор


[@Stas9878](https://github.com/Stas9878)

