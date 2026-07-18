# SupportAI


Репозиторий создан как финальный проект для моего курса на Stepik — [ссылка](https://stepik.org/a/274734)


**SupportAI** — это веб-сервис на базе FastAPI и LangGraph для автоматической обработки заявок в службу поддержки с использованием AI-агентов.


## Описание


SupportAI принимает пользовательские запросы, ведёт многошаговый диалог с накоплением истории и автоматически:
- **Отвечает пользователю** через LLM с учётом истории диалога и контекста заявки
- **Классифицирует** заявку по категориям (техническая, биллинг, фича, другое)
- **Определяет приоритет** (critical, high, medium, low) на основе срочности
- **Назначает релевантные теги** для быстрой маршрутизации
- **Запрашивает подтверждение (HIL)** для чувствительных операций с высоким приоритетом
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
- 💬 **Многошаговый диалог** с историей сообщений в чекпоинтере (`operator.add`)
- 👤 **Human-in-the-Loop** — подтверждение чувствительных заявок через `interrupt()`
- ♻️ **Восстановление состояния** после сбоев благодаря чекпоинтам в PostgreSQL
- 🔁 **Retry-логика** с экспоненциальной задержкой для устойчивости к временным сбоям
- 🛡️ **Защита от prompt injection** и санитизация пользовательского ввода
- 📊 **Структурированное логирование** в JSON-формате для интеграции с системами мониторинга
- 📱 **Telegram-алерты** для critical и high+requires_approval заявок
- 🐳 **Docker-ready** — запуск одной командой со всеми зависимостями
- ✅ **Unit-тесты** для критичных модулей, истории диалога и восстановления после сбоев


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
│   │   ├── state.py              # AgentState: история, HIL, флаги
│   │   ├── llm.py                # Настройка LLM (Ollama)
│   │   ├── checkpointer.py       # PostgresSaver для чекпоинтов
│   │   ├── retry.py              # Retry-декоратор для LLM
│   │   └── nodes/
│   │       ├── chat_handler.py   # LLM-диалог и накопление messages
│   │       ├── classifier.py     # Классификация заявок
│   │       ├── prioritizer.py    # Определение приоритета и requires_approval
│   │       ├── tagger.py         # Назначение тегов
│   │       ├── confirmation.py   # HIL: interrupt() и подтверждение
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
│   ├── test_critical.py          # Unit-тесты безопасности, retry, классификатора
│   ├── test_chat_history.py      # Unit-тесты chat_handler и маршрутизации
│   └── test_recovery.py          # Unit-тесты восстановления после сбоев
│
└── scripts/                      # Вспомогательные скрипты
    ├── check_env.py              # Проверка переменных окружения
    ├── test_db.py                # Тест подключения к БД
    ├── test_logging.py           # Тест логирования
    ├── test_retry.py             # Тест retry-логики
    ├── test_security.py          # Тест санитизации
    ├── test_checkpoints.py       # Ручной тест чекпоинтов и диалога
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


Создание новой заявки и **первое сообщение** в диалоге. Запускает полный пайплайн агента (chat → classifier → … → saver).

Повторный вызов с тем же `thread_id` возвращает **409 Conflict** — для follow-up используйте `POST /tickets/chat/{thread_id}/messages`.


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
  "last_response": "Проверьте логин и пароль...",
  "messages_count": 2,
  "created_at": "2026-03-29T10:00:00"
}
```


**Ответ (HIL — ожидает подтверждения):**
```json
{
  "id": 0,
  "thread_id": "user_session_123",
  "priority": "high",
  "status": "awaiting_confirmation"
}
```


### `POST /tickets/chat/{thread_id}/messages`


Follow-up сообщение в существующую сессию. История загружается из чекпоинтера, пайплайн классификации не перезапускается.


**Запрос:**
```json
{
  "content": "Ошибка 401 при вводе пароля"
}
```


**Ответ:**
```json
{
  "thread_id": "user_session_123",
  "messages": [
    {"role": "user", "content": "Не могу войти в аккаунт"},
    {"role": "assistant", "content": "Проверьте логин и пароль..."},
    {"role": "user", "content": "Ошибка 401 при вводе пароля"},
    {"role": "assistant", "content": "Ошибка 401 означает..."}
  ],
  "last_response": "Ошибка 401 означает...",
  "done": false,
  "ticket_id": 1,
  "category": "technical",
  "priority": "high"
}
```

Поле `done` отражает `dialog_closed` (диалог завершён пользователем), а не `done` от saver.

**Коды ошибок:**
| Код | Ситуация |
|-----|----------|
| `404` | Сессия с `thread_id` не найдена |
| `400` | Диалог уже закрыт или заявка ждёт HIL-подтверждения |


### `GET /tickets/chat/{thread_id}`


Получение истории диалога без отправки нового сообщения и без вызова LLM.


**Ответ:** тот же формат, что у `POST /tickets/chat/{thread_id}/messages`.


### `POST /tickets/confirm`


Подтверждение или отклонение заявки в статусе HIL (`awaiting_confirmation`). Использует `thread_id`, не `ticket_id`.


**Запрос:**
```json
{
  "thread_id": "user_session_123",
  "decision": "yes"
}
```


**Ответ:**
```json
{
  "ticket_id": 42,
  "confirmed": true,
  "status": "in_progress",
  "message": null
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


### Пример сценария: многошаговый диалог


```bash
# 1. Первое сообщение — создание заявки и запуск пайплайна
curl -X POST http://localhost:8000/tickets/ \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "demo_1", "user_input": "Не могу войти в аккаунт"}'

# 2. Follow-up — история подтягивается из чекпоинтера
curl -X POST http://localhost:8000/tickets/chat/demo_1/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Ошибка 401 при вводе пароля"}'

# 3. История без нового сообщения
curl http://localhost:8000/tickets/chat/demo_1

# 4. Завершение диалога (прощание пользователя)
curl -X POST http://localhost:8000/tickets/chat/demo_1/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Спасибо, всё понятно, до свидания!"}'
# → done: true, дальнейшие POST вернут 400

# 5. HIL: если POST /tickets/ вернул status: awaiting_confirmation
curl -X POST http://localhost:8000/tickets/confirm \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "demo_1", "decision": "yes"}'
```


## Как это работает


### Архитектура агента


```
Новое сообщение пользователя
        ↓
┌─────────────────┐
│  chat_handler   │ → LLM-ответ + messages (user + assistant)
└────────┬────────┘
         ↓
    ┌────┴────────────────┐
    ↓                     ↓
 dialog_closed?      ticket_id есть?
    ↓                     ↓
  end               dialog_end → END (follow-up)
    ↓
 classifier → prioritizer → tagger
         ↓
    ┌────┴────┐
    ↓         ↓
 alert    saver (или alert → confirmation → saver)
    ↓
 Telegram / HIL interrupt
```


**Маршрутизация после chat:**
- `dialog_closed=True` — пользователь попрощался, диалог закрыт
- `ticket_id is not None` — follow-up, ответ уже сгенерирован, saver не перезапускается
- иначе — первое сообщение, полный пайплайн классификации

**HIL:** для `high + requires_approval` граф прерывается на `confirmation_node` (`interrupt()`). Возобновление — через `POST /tickets/confirm` с `Command(resume=...)`.


**Состояние агента (`AgentState`):**
- `messages` — накопление истории через `operator.add` (каждый вызов chat добавляет пару user/assistant)
- `done` — заявка сохранена в БД (saver)
- `dialog_closed` — пользователь попрощался; API отдаёт это как `ChatResponse.done`
- `ticket_id` — после первого сохранения; follow-up идёт через `dialog_end` без повторной классификации

**Устойчивость chat_handler:** при исчерпании retry или недоступности Ollama возвращается fallback-ответ, диалог не падает с ошибкой.


### Чекпоинты и восстановление


1. После каждого узла графа состояние сохраняется в PostgreSQL (включая `messages` через `operator.add`)
2. При сбое или перезапуске агент восстанавливается с последнего чекпоинта
3. `thread_id` в `config["configurable"]` обеспечивает изоляцию сессий пользователей
4. Follow-up сообщения накапливают историю без повторного создания заявки (`dialog_end`)


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
# 48 тестов: critical, chat_history, recovery
```


| Файл | Что покрывает |
|------|----------------|
| `test_critical.py` | Санитизация, retry, классификатор |
| `test_chat_history.py` | chat_handler, маршрутизация, прощание |
| `test_recovery.py` | Retry/fallback LLM, перезапуск диалога, HIL resume |


### Запуск отдельных наборов


```bash
pytest tests/test_critical.py -v
pytest tests/test_chat_history.py -v
pytest tests/test_recovery.py -v
```


Unit-тесты восстановления используют `InMemorySaver` и не требуют PostgreSQL.


### Ручная проверка чекпоинтов


```bash
python scripts/test_checkpoints.py
```

Требует PostgreSQL и Ollama. Проверяет восстановление многошагового диалога после «перезапуска» графа.


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
| `test_checkpoints.py` | Ручной тест диалога и изоляции чекпоинтов | `python scripts/test_checkpoints.py` |
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
2. Реализуйте функцию с сигнатурой `(state: AgentState) -> dict`:
   возвращайте **только изменённые поля** (дельту), без сборки полного `AgentState`
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

