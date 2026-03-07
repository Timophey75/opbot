# 🚂 Развертывание на Railway.app

Railway.app - самый простой способ развернуть приложение с бесплатной пробной версией.

## Подготовка

### 1. GitHub репозиторий

Убедитесь, что ваш код на GitHub (см. DEPLOYMENT_RENDER.md Шаг 1-3)

### 2. Создание Railway проекта

1. Перейти на https://railway.app
2. Нажмите **Deploy Now** или **New Project**
3. Выберите **Deploy from GitHub repo**
4. Авторизуйтесь через GitHub
5. Выберите репозиторий `opbot`

## Конфигурация

Railway.app автоматически:
- Читает `Procfile`
- Устанавливает зависимости из `requirements.txt`
- Запускает приложение

### Добавление переменных окружения

1. Перейдите в **Settings** проекта
2. Нажмите **Variables**
3. Добавьте:

```
TELEGRAM_BOT_TOKEN=your_token_here
ADMIN_CODE=0000
WEB_APP_URL=https://your-app.railway.app
```

4. Нажмите **Save**

## Автоматический Deploy

Railway автоматически разворачивает при push в main:

```bash
git push origin main
```

## Мониторинг

- **Логи:** Нажмите на проект → **Logs**
- **Редепой:** Нажмите **Redeploy**
- **Остановка:** Нажмите **Pause**

## Получение публичного URL

1. На странице проекта найдите **Domain**
2. URL будет вида `https://your-app-name.railway.app`
3. Используйте этот URL в `WEB_APP_URL`

## Проблемы и решения

### "Port error" или "Timeout"
- Убедитесь, что `Procfile` правильно указан
- Проверьте логи для более подробной информации
- Перезагрузите приложение

### Бесплатный кредит исчерпан
- Railway дает $5 бесплатно
- После этого нужно добавить карту
- Используйте вместо Web App бесплатный Render.com

### Не срабатывает Telegram Bot
- Убедитесь, что `TELEGRAM_BOT_TOKEN` правильный
- Лучше использовать Background Worker (платная функция)
- Или запустить Bot локально на Termux

## Подключение двух сервисов

Если нужны реальное Web App + Real Bot:

### Способ 1: Оба сервиса в Railway (платно)

1. Создайте 2 сервиса в одном проекте
2. Используйте `web` и `worker` в Procfile

### Способ 2: Гибридный подход (рекомендуется)

- **Web App:** Railway.com (бесплатно/платно)
- **Telegram Bot:** Localtunnel + локальный компьютер/Termux
- Или: Webhook для Bot вместо polling

### Способ 3: Webhook для Bot

Обновите `bot.py` для использования webhooks:

```python
from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleWebhookServer, setup_application

# Вместо polling используйте webhook
```

## Масштабирование на платный план

Когда бесплатные кредиты закончатся:

1. Нажмите **Settings** → **Plan**
2. Выберите **Hobby Plan** ($5/месяц) или выше
3. Добавьте способ оплаты

## Популярные размещение для России

| Сервис | Бесплатно | Цена | Лучше всего для |
|--------|----------|------|-----------------|
| Railway | $5 кредит | $5+/мес | Web App |
| Render | Да | $7+/мес | Web App + Bot |
| Fly.io | Да | $5/мес | Docker контейнеры |
| PythonAnywhere | Да (limitedно) | $5/мес | Python приложения |

---

**Быстрый старт:**

```bash
# 1. Залиште код на GitHub
git push origin main

# 2. Откройте Railway
# 3. Нажмите "New Project" → "Deploy from GitHub"
# 4. Выберите opbot
# 5. Добавьте переменные окружения
# 6. Готово! ✅
```

Приложение запустится автоматически!
