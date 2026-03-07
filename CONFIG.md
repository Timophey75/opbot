# ⚙️ КОНФИГУРАЦИЯ И НАСТРОЙКИ

## 🔧 Файл .env

Основной конфиг приложения находится в файле `.env`

### Полный пример

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=7253076546:AAG_gZ-Ye5yrBVXBFT2T6Pl26D2jQc6p3aY

# Администратор
ADMIN_CODE=0000

# Web App URL
WEB_APP_URL=http://localhost:5000

# Опционально (для будущей версии)
DEBUG=False
LOG_LEVEL=INFO
```

### Переменные окружения

#### TELEGRAM_BOT_TOKEN (обязательно)

Токен Telegram бота от @BotFather

```bash
# Получение:
# 1. Откройте @BotFather в Telegram
# 2. Отправьте /newbot
# 3. Следуйте инструкциям
# 4. Скопируйте токен в .env

TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE:XXXXX
```

#### ADMIN_CODE (обязательно)

4-символьный код для входа администратора

```bash
# Может быть:
# - 4 цифры: 0000, 1234, 9999
# - 4 буквы: ABCD, admin, root
# - Микс: 12ab, a1b2

ADMIN_CODE=0000  # По умолчанию
# или
ADMIN_CODE=admin
# или
ADMIN_CODE=1234
```

#### WEB_APP_URL (обязательно)

URL где запущено веб-приложение

```bash
# Локально:
WEB_APP_URL=http://localhost:5000

# На Render:
WEB_APP_URL=https://opbot-webapp.onrender.com

# На Railway:
WEB_APP_URL=https://opbot-production.railway.app

# На своем домене:
WEB_APP_URL=https://schedule.example.com
```

## 🗄️ Конфигурация базы данных

### Местоположение

По умолчанию: `./schedule.db` (в корне проекта)

### Размер

- Пустая БД: ~50KB
- Со 100 пользователями: ~200KB
- Со 1000 событиями: ~500KB

### Резервное копирование

```bash
# Создать резервную копию
cp schedule.db schedule.db.backup

# Восстановить из резервной копии
cp schedule.db.backup schedule.db

# Автоматическое резервное копирование (daily)
# Добавьте в crontab (Linux/Mac):
0 2 * * * cp ~/opbot/schedule.db ~/opbot/backups/schedule.db.$(date +\%Y\%m\%d)
```

## 🎨 Тематизация и цвета

### Цветовая схема приложения

Отредактируйте в `static/app.html` раздел `<style>`:

```css
/* Основной цвет */
--primary: #667eea;      /* Фиолетовый */
--secondary: #764ba2;    /* Темно-фиолетовый */

/* Для светлой темы */
--light-bg: #f8f9fa;     /* Светло-серый */
--light-text: #333333;   /* Темный текст */

/* Для светлой темы */
--dark-bg: #1a1a1a;      /* Темный фон (будущее) */
--dark-text: #f0f0f0;    /* Светлый текст (будущее) */
```

### Эмодзи цвета операторов

В `database.py` функция `create_user()`:

```python
colors = ['🟦', '🟧', '🟥', '⬛️', '🟩', '🟪', '🟨', '🟫']

# Можно добавить больше:
colors = [
    '🟦', '🟧', '🟥', '⬛️', '🟩', '🟪', '🟨', '🟫',  # Основные
    '🔵', '🟠', '🔴', '⚫️', '🟢', '🟣', '🟡', '🟤',  # Объёмные
    '🎨', '✨', '⭐', '💫', '🌟', '💥', '🔥', '❄️'   # Альтернативные
]
```

## 🔐 Безопасность и приватность

### Рекомендации

1. **Не делитесь админ кодом** с людьми которым не доверяете
2. **Регулярно меняйте админ код** (обновляйте .env)
3. **Используйте HTTPS** на Production (включена по умолчанию на Render/Railway)
4. **Резервируйте БД** хотя бы раз в неделю
5. **Установите CORS** только для доверенных источников

### .env в Production

```bash
# НИКОГДА не коммитьте .env в Git!
echo ".env" >> .gitignore
```

## 📊 Мониторинг и логирование

### Логи на локальном компьютере

```bash
# Логи Flask Web App
tail -f /tmp/flask.log

# Логи Telegram Bot
tail -f /tmp/bot.log

# Все логи
tail -f /tmp/*.log
```

### На хостингах

**Render:**
```
Dashboard → opbot-webapp → Logs
```

**Railway:**
```
Project → Service → Logs
```

## 🔄 Актуализация конфига

### Когда нужно обновить .env

- [ ] Изменили токен Telegram бота
- [ ] Изменили админ код
- [ ] Развертываются на новом хостинге
- [ ] Изменили домен
- [ ] Обновляется код приложения

### Как применить изменения

**На локальной машине:**
```bash
# Обновите .env файл
nano .env

# Перезагрузите приложение
# Ctrl+C в обоих терминалах
# Перезапустите python web_app.py и python bot.py
```

**На Render:**
```
Dashboard → Settings → Environment → EDIT
# Обновите переменные
# Deploy → Restart обновление будет применено
```

**На Railway:**
```
Project → Variables → Edit
# Обновите значения
# Автоматически перезагрузится
```

## 💾 Экспорт и импорт данных

### Экспорт расписания в CSV

```python
import sqlite3
import csv

conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM events")
events = cursor.fetchall()

with open('schedule.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Дата', 'Время', 'Название', 'Период', 'Оператор'])
    writer.writerows(events)

conn.close()
```

### Импорт данных

```python
# TODO: Реализовать импорт в v1.1
```

## 🚀 Оптимизация производительности

### Для уменьшения нагрузки

1. **Отключите debug mode:**
   ```python
   # В web_app.py
   app.run(debug=False)  # вместо debug=True
   ```

2. **Кешируйте календарь:**
   ```javascript
   // В app.js добавьте кеш
   const calendarCache = {};
   ```

3. **Используйте CDN для статических файлов:**
   ```html
   <!-- Вместо локальных файлов -->
   <link rel="stylesheet" href="https://cdn.example.com/style.css">
   ```

4. **Сжимайте БД:**
   ```python
   import sqlite3
   conn = sqlite3.connect('schedule.db')
   conn.execute('VACUUM')
   conn.close()
   ```

## 🔧 Расширенная конфигурация

### Flask конфигурация (web_app.py)

```python
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB макимум
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPSonly
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
```

### aiogram конфигурация (bot.py)

```python
# Параметры бота
bot = Bot(
    token=API_TOKEN,
    parse_mode='HTML',  # По умолчанию HTML
    disable_web_page_preview=True  # Не показывать превью
)

# Параметры dispatcher
dp = Dispatcher(
    throttle_time_msec=0,  # Отключить throttling
    local_mode=True  # Локальный режим для тестов
)
```

## 📈 Масштабирование

### Когда нужно масштабировать

- Более 1000 активных пользователей
- Более 10000 событий в месяц
- Медленные запросы (>1сек)
- Часто падает приложение

### Как масштабировать

1. **PostgreSQL вместо SQLite** (v1.1)
2. **Отделить бот от Web App** (на разные серверы)
3. **Добавить кеш (Redis)** (v1.2)
4. **Использовать CDN** для статики
5. **Микросервисная архитектура** (v2.0)

---

**Помните:** Настраивайте только то, что действительно нужно. Приложение работает хорошо "out of the box"! 🎉
