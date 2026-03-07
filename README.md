# 📅 Система управления расписанием с Telegram ботом

Полнофункциональная система управления расписанием со встроенным Telegram ботом и мини-приложением для управления сменами, напоминаниями и операторами.

## 🚀 Возможности

### Для Администратора:
- ✅ Календарь месяца (март 2026 и далее)
- ✅ Создание и удаление мероприятий (утро/вечер)
- ✅ Назначение операторов на смены
- ✅ Управление операторами (добавить, удалить, изменить)
- ✅ Настройка напоминаний для себя
- ✅ Получение уведомлений об отказах операторов

### Для Оператора:
- ✅ Просмотр расписания в календаре
- ✅ Просмотр деталей смен
- ✅ Отказ от смены с указанием причины
- ✅ Настройка личных напоминаний
- ✅ Уведомления о новых назначениях

## 📋 Требования

- Python 3.8+
- pip
- Telegram аккаунт
- Интернет соединение

## 🔧 Установка локально

### 1. Клонируем репозиторий
```bash
cd opbot
```

### 2. Создаем виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

### 3. Устанавливаем зависимости
```bash
pip install -r requirements.txt
```

### 4. Настраиваем переменные окружения
```bash
cp .env.example .env
# Отредактируйте .env и добавьте свой TELEGRAM_BOT_TOKEN
```

### 5. Инициализируем базу данных
```bash
python init.py
```

### 6. Запускаем приложение

**В одном терминале (Flask Web App):**
```bash
python web_app.py
```

**В другом терминале (Telegram Bot):**
```bash
python bot.py
```

Приложение будет доступно по адресу `http://localhost:5000`

## 📱 Получение Telegram Bot Token

1. Откройте [@BotFather](https://t.me/botfather) в Telegram
2. Нажмите `/newbot` и следуйте инструкциям
3. Скопируйте полученный токен
4. Вставьте токен в `.env` файл: `TELEGRAM_BOT_TOKEN=your_token_here`

## 🌐 Развертывание на бесплатном хостинге

### Вариант 1: Render.com (Рекомендуется)

1. **Зарегистрируйся на [Render.com](https://render.com)**

2. **Создай Web Service:**
   - Подключи свой GitHub репозиторий
   - Выбери **Python** как Runtime
   - **Build Command:** `pip install -r requirements.txt && python init.py`
   - **Start Command:** `gunicorn web_app:app --timeout 120`

3. **Добавь Environment Variables:**
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   ADMIN_CODE=0000
   ```

4. **Запусти деплой**

### Вариант 2: Railway.app

1. **Зарегистрируйся на [Railway.app](https://railway.app)**

2. **Создай новый проект**

3. **Заполни переменные окружения:**
   - `TELEGRAM_BOT_TOKEN`
   - `ADMIN_CODE`

4. **Railway автоматически прочитает Procfile и запустит приложение**

### Вариант 3: Termux на Android

1. **Установи Termux** из F-Droid

2. **В Termux выполни:**
```bash
apt update && apt upgrade
apt install python git
git clone https://github.com/yourusername/opbot.git
cd opbot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Создай скрипт запуска** `run.sh`:
```bash
#!/bin/bash
source venv/bin/activate
python init.py
python web_app.py &
python bot.py
```

4. **Запусти:** `bash run.sh`

5. **Для постоянного запуска используй service или screen:**
```bash
screen -S opbot bash run.sh
```

## 🔐 Коды доступа

- **Код администратора:** `0000` (можно изменить в `.env`)
- **Коды операторов:** генерируются автоматически при создании

## 📝 Структура проекта

```
opbot/
├── bot.py                 # Telegram бот
├── web_app.py             # Flask приложение
├── database.py            # Работа с БД
├── init.py                # Инициализация системы
├── requirements.txt       # Зависимости Python
├── Procfile               # Конфигурация для хостинга
├── .env                   # Переменные окружения
├── .env.example           # Пример .env файла
├── static/
│   ├── index.html         # Главная страница
│   ├── app.html           # Мини-приложение
│   └── app.js             # Логика приложения
└── schedule.db            # База данных SQLite
```

## 🎨 Дизайн

Приложение имеет современный градиентный дизайн с поддержкой:
- Мобильных устройств
- Темной темы (через CSS media queries)
- Плавных переходов и анимаций
- Интуитивного интерфейса

## 🔔 Типы напоминаний

1. **За сутки** - напоминание о назначенной смене
2. **Утром** - напоминание в определенное время утра
3. **Вечером накануне** - напоминание вечером перед сменой

## 🛠 API Endpoints

### Аутентификация
- `GET /api/auth/check` - Проверка аутентификации
- `POST /api/auth/login` - Вход по коду

### Календарь
- `GET /api/calendar` - Получить календарь на месяц
- `GET /api/events/day` - События на конкретный день

### События
- `POST /api/events/create` - Создать событие
- `DELETE /api/events/<id>/delete` - Удалить событие
- `POST /api/events/<id>/assign` - Назначить оператора

### Операторы (только админ)
- `GET /api/operators/list` - Список операторов
- `POST /api/operators/create` - Создать оператора
- `PUT /api/operators/<id>/update` - Обновить оператора
- `DELETE /api/operators/<id>/delete` - Удалить оператора

### Напоминания
- `GET /api/reminders/get` - Получить напоминания
- `POST /api/reminders/update` - Обновить напоминание

## 📧 Поддержка

При возникновении проблем:
1. Проверьте логи в консоли
2. Убедитесь, что все переменные окружения установлены
3. Перезагрузите приложение

## 📄 Лицензия

MIT License - свободное использование в личных и коммерческих целях

## ⭐ Рекомендации

- Регулярно создавайте бэкапы базы данных `schedule.db`
- Используйте надежные пароли для администратора
- Мониторьте логи приложения
- Обновляйте зависимости Python

---

**Создано с ❤️ для эффективного управления расписанием**
