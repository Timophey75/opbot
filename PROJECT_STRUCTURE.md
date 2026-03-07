📅 SCHEDULE MANAGEMENT SYSTEM
================================

Полнофункциональная система управления расписанием со встроенным Telegram ботом и Web приложением

## 📂 СТРУКТУРА ПРОЕКТА

```
opbot/
├── 🐍 Python Backend
│   ├── bot.py                 # Telegram бот (aiogram)
│   ├── web_app.py             # Flask приложение для Web App
│   ├── database.py            # Работа с SQLite БД
│   ├── notifications.py       # Обработка уведомлений
│   ├── init.py                # Инициализация системы
│   └── test_data.py           # Создание тестовых данных
│
├── 🌐 Frontend & Web
│   ├── static/
│   │   ├── app.html           # Мини-приложение (интерфейс)
│   │   ├── app.js             # Логика приложения
│   │   └── index.html         # Главная страница
│
├── 🚀 Развертывание
│   ├── Procfile               # Для Heroku/Render/Railway
│   ├── Dockerfile             # Docker контейнер
│   ├── docker-compose.yml     # Docker Compose конфиг
│   ├── setup.sh               # Скрипт установки
│   └── requirements.txt       # Python зависимости
│
├── 📚 Документация
│   ├── README.md              # Основное описание
│   ├── HELP.md                # Руководство пользователя
│   ├── TERMUX_GUIDE.md        # Установка на Android
│   ├── DEPLOYMENT_RENDER.md   # Deploy на Render.com
│   ├── DEPLOYMENT_RAILWAY.md  # Deploy на Railway.app
│   └── PROJECT_STRUCTURE.md   # Этот файл
│
├── ⚙️ Конфигурация
│   ├── .env                   # Переменные окружения
│   ├── .env.example           # Пример конфига
│   ├── .gitignore             # Git ignore rules
│   └── schedule.db            # SQLite база данных (создается при первом запуске)
```

## 📋 ОПИСАНИЕ ФАЙЛОВ

### Backend (Python)

**bot.py** (≈200 строк)
- Основной Telegram бот на aiogram
- Команды: /start, /status, /admin_notify
- Функции отправки уведомлений
- Обработка Event при входе пользователей

**web_app.py** (≈400 строк)
- Flask веб-сервер для мини-приложения
- REST API endpoints для работы с данными
- Управление сессиями пользователей
- CORS для работы мини-приложения

**database.py** (≈300 строк)
- SQLite ORM класс Database
- Таблицы: users, events, refusals, reminders
- CRUD операции для всех сущностей
- Генерация уникальных кодов

**notifications.py** (≈150 строк)
- Асинхронная обработка напоминаний
- Функции отправки уведомлений в Telegram
- Scheduler для проверки напоминаний

**init.py** (≈50 строк)
- Инициализация БД при первом запуске
- Создание администратора по умолчанию
- Вывод информации об учетных данных

**test_data.py** (≈100 строк)
- Создание тестовых данных для разработки
- Генерирует операторов, события, напоминания
- Вывод кодов для входа

### Frontend (HTML/JS)

**app.html** (≈500 строк CSS+HTML)
- Структура мини-приложения
- Красивый градиентный дизайн
- Навигация между экранами
- Модальные окна для операций

**app.js** (≈600 строк)
- Основной класс приложения ScheduleApp
- Логика навигации и управления состоянием
- API клиент для взаимодействия с backend
- Функции: логин, календарь, события, операторы, напоминания

**index.html** (≈100 строк)
- Приветственная страница
- Информация о проекте
- Кнопка входа в приложение

### Развертывание

**Procfile**
- Конфиг для запуска gunicorn на Production

**Dockerfile**
- Контейнер для развертывания в Docker
- Python 3.10 slim образ

**docker-compose.yml**
- Запуск Web App и Bot в двух контейнерах
- Общая БД для обоих сервисов

**setup.sh**
- Автоматическая установка окружения
- Для Mac/Linux/Windows (Git Bash)

**requirements.txt**
- aiogram==3.0.0 - Telegram Bot Framework
- flask==2.3.3 - Web framework
- flask-cors==4.0.0 - CORS поддержка
- gunicorn==21.2.0 - WSGI сервер
- python-dotenv==1.0.0 - Переменные окружения
- aiohttp==3.8.5 - Async HTTP
- requests==2.31.0 - HTTP клиент
- python-telegram-bot==20.3 - Telegram API

### Конфигурация

**.env**
```
TELEGRAM_BOT_TOKEN=your_token
ADMIN_CODE=0000
WEB_APP_URL=http://localhost:5000
```

**.gitignore**
- Python кеш файлы
- Переменные окружения
- IDE конфигурация
- Логи и временные файлы

## 🗄️ СТРУКТУРА БД (SQLite)

### users (пользователи)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE,              -- Telegram ID
    name TEXT NOT NULL,                  -- Имя
    surname TEXT NOT NULL,               -- Фамилия
    code TEXT UNIQUE NOT NULL,           -- 4-значный код входа
    color_emoji TEXT NOT NULL,           -- Уникальный цвет (эмодзи)
    is_admin INTEGER DEFAULT 0,          -- Является ли администратором
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### events (мероприятия)
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,                  -- YYYY-MM-DD
    time TEXT NOT NULL,                  -- HH:MM
    title TEXT NOT NULL,                 -- Название события
    period TEXT NOT NULL,                -- 'morning' или 'evening'
    operator_id INTEGER,                 -- ID назначенного оператора
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES users(id)
);
```

### shift_refusals (отказы от смен)
```sql
CREATE TABLE shift_refusals (
    id INTEGER PRIMARY KEY,
    operator_id INTEGER NOT NULL,        -- Кто отказывается
    event_id INTEGER NOT NULL,           -- От какого события
    reason TEXT NOT NULL,                -- Причина отказа
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);
```

### reminders (напоминания)
```sql
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,            -- Кому напомнить
    type TEXT NOT NULL,                  -- 'day_before', 'morning', 'evening_before'
    time_morning TEXT DEFAULT '10:00',   -- Время утра
    time_evening TEXT DEFAULT '19:00',   -- Время вечера
    enabled INTEGER DEFAULT 1,           -- Включено/отключено
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 🔌 API ENDPOINTS

### Аутентификация
- `GET /api/auth/check?user_id=<id>` - Проверить авто
- `POST /api/auth/login` - Вход по коду

### Календарь
- `GET /api/calendar?month=3&year=2026` - Получить месяц

### События
- `GET /api/events/day?date=2026-03-15&user_id=<id>` - События дня
- `POST /api/events/create` - Создать событие
- `DELETE /api/events/<id>/delete` - Удалить событие
- `POST /api/events/<id>/assign` - Назначить оператора
- `POST /api/events/<id>/refuse` - Отказаться от смены

### Операторы
- `GET /api/operators/list` - Список операторов
- `POST /api/operators/create` - Создать оператора
- `PUT /api/operators/<id>/update` - Обновить оператора
- `DELETE /api/operators/<id>/delete` - Удалить оператора

### Напоминания
- `GET /api/reminders/get?user_id=<id>` - Получить напоминания
- `POST /api/reminders/update` - Обновить напоминание

## 🎨 UI/UX КОМПОНЕНТЫ

### Цветовая схема
```
Основной градиент:  #667eea → #764ba2 (фиолетовый)
Фоны:               #f8f9fa, #ffffff
Текст:              #333333, #666666
Акценты:            #27ae60, #e74c3c
```

### Эмодзи для операторов
🟦 🟧 🟥 ⬛️ 🟩 🟪 🟨 🟫

### Иконографика
📅 Календарь      🔔 Напоминания     👥 Операторы
🌅 Утро          🌆 Вечер           ✅ Готово
❌ Отмена         🗑️ Удалить         ✏️ Редактировать
➕ Добавить       ↩️ Назад           📌 Назначение
⚠️ Внимание       📱 Приложение

## 📊 ОСНОВНЫЕ ФУНКЦИИ

### Админ-возможности
✅ Управление календарем
✅ Создание мероприятий с гибким временем
✅ Управление операторами (CRUD)
✅ Назначение операторов на смены
✅ Просмотр отказов от смен
✅ Личные напоминания

### Оператор-возможности
✅ Просмотр своего расписания
✅ Просмотр всех смен
✅ Отказ от смены с причиной
✅ Личные напоминания
✅ Уведомления о новых назначениях

## 🚀 БЫСТРЫЙ СТАРТ

### Локально
```bash
python setup.sh          # Установка
python bot.py &          # Bot
python web_app.py        # Web App
```

### Docker
```bash
docker-compose up
```

### На сервере
Смотрите: `DEPLOYMENT_RENDER.md` или `DEPLOYMENT_RAILWAY.md`

## 📱 Совместимость

- ✅ Мобильные телефоны (iOS/Android)
- ✅ Планшеты
- ✅ Десктопные браузеры
- ✅ Telegram Mini App API
- ✅ Python 3.8+

## 📝 Лицензия

MIT License - свободное использование

## 👨‍💻 Разработка

### Добавление новой функции

1. Обновить `database.py` если нужна новая таблица
2. Добавить API endpoint в `web_app.py`
3. Реализовать UI в `app.js` и `app.html`
4. Протестировать локально
5. Развернуть на сервер

### Отладка

Используйте:
- Browser DevTools (F12) для фронтенда
- Flask debug mode для бэкенда
- `tail -f` для логов на сервере

---

**Версия:** 1.0  
**Дата:** Март 2026  
**Язык:** Python 3.8+, JavaScript ES6+, HTML5, CSS3

Готово к продакшену и масштабированию! 🚀
