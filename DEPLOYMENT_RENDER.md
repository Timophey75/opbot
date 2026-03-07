# 🚀 Развертывание на Render.com

Render.com - отличный выбор для развертывания приложения с поддержкой бесплатного уровня и работой в РФ.

## Подготовка репозитория

### 1. Инициализируем Git репозиторий

```bash
cd opbot
git init
git add .
git commit -m "Initial commit: Schedule management system"
```

### 2. Создаем GitHub репозиторий

1. Перейти на https://github.com/new
2. Создать новый репозиторий `opbot`
3. Не выбирайте "Initialize this repository with README"

### 3. Загружаем на GitHub

```bash
git remote add origin https://github.com/yourusername/opbot.git
git branch -M main
git push -u origin main
```

## Развертывание на Render

### Шаг 1: Регистрация на Render

1. Перейти на https://render.com
2. Нажмите "Sign up" → "Continue with GitHub"
3. Авторизуйтесь через GitHub

### Шаг 2: Создание Web Service для Web App

1. На dashboard нажмите **+ New** → **Web Service**
2. Подключите GitHub репозиторий `opbot`
3. Заполните поля:

   | Поле | Значение |
   |------|----------|
   | **Name** | opbot-webapp |
   | **Environment** | Python 3 |
   | **Region** | Frankfurt (EU) или Singapore |
   | **Branch** | main |
   | **Build Command** | `pip install -r requirements.txt && python init.py` |
   | **Start Command** | `gunicorn web_app:app --timeout 120` |

4. Нажмите **Advanced** и добавьте переменные окружения:

   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   ADMIN_CODE=0000
   WEB_APP_URL=https://opbot-webapp.onrender.com
   ```

5. Нажмите **Create Web Service**

### Шаг 3: Создание Background Worker для Bot

1. На dashboard нажмите **+ New** → **Background Worker**
2. Выберите тот же GitHub репозиторий
3. Заполните поля:

   | Поле | Значение |
   |------|----------|
   | **Name** | opbot-bot |
   | **Environment** | Python 3 |
   | **Region** | Frankfurt (EU) |
   | **Branch** | main |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `python bot.py` |

4. Добавьте переменные окружения:

   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   ADMIN_CODE=0000
   WEB_APP_URL=https://opbot-webapp.onrender.com
   ```

5. Нажмите **Create Background Worker**

## Получение кода Telegram Bot

1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте `/newbot`
3. Введите имя: `Schedule Management Bot`
4. Введите username: `@schedule_mgmt_bot` (любой доступный)
5. Скопируйте полученный токен
6. Вставьте в `TELEGRAM_BOT_TOKEN`

## Обновление Web App URL в боте

После развертывания на Render:

1. Перейдите в settings Web Service
2. Найдите URL вида `https://opbot-webapp.onrender.com`
3. Обновите в боте команду /start, чтобы использовать правильный URL

## Мониторинг логов

**Для Web App:**
- Dashboard → opbot-webapp → Logs

**Для Bot:**
- Dashboard → opbot-bot → Logs

## Обновление приложения

По умолчанию Render автоматически развертывает при push в main:

```bash
git add .
git commit -m "Update schedule feature"
git push origin main
```

Render автоматически:
1. Запустит Build Command
2. Запустит Start Command
3. Обновит приложение

## Подключение собственного домена

1. В settings Web Service нажмите **Custom Domains**
2. Введите ваш домен (например `schedule.yoursite.com`)
3. Следуйте инструкциям для настройки DNS

## Решение проблем

### Приложение падает при запуске
- Проверьте логи: Dashboard → Logs
- Убедитесь, что `TELEGRAM_BOT_TOKEN` указан правильно
- Проверьте, нет ли ошибок в `init.py`

### УБО не срабатывает
- Bot запускается в Background Worker, он может спать на бесплатном плане
- Для постоянной работы используйте платный план ($10+/месяц)

### Слишком медленно
- Это характеристика бесплатного плана
- На платном плане ($7+) производительность выше

### Не работает база данных
- Убедитесь, что `schedule.db` находится в корне проекта
- Перезагрузите приложение: Dashboard → Redeploy

## Альтернативы Render

### Railway.app (более дешево)
- https://railway.app
- Бесплатная пробная версия $5
- Просто connectите GitHub и готово

### PythonAnywhere
- https://www.pythonanywhere.com/
- Бесплатный план ограничен (консоль 100 секунд)
- Платный план $5/месяц

### Replit
- https://replit.com
- Бесплатно, но требует постоянного контейнера
- Платный план $7/месяц

---

**Рекомендуемая конфигурация:**
- **Web App:** Render.com (бесплатный)
- **Bot:** Railway.app ($5/месяц) или локально на Termux
- **База данных:** SQLite (встроена)

Это обойдется $0-5 в месяц в зависимости от выбора хостинга.
