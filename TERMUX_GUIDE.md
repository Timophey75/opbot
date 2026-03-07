# 📱 Руководство по запуску в Termux на Android

## Установка Termux

1. **Установите F-Droid** (если не установлен)
   - Посетите https://f-droid.org на телефоне
   - Скачайте и установите F-Droid APK

2. **Установите Termux из F-Droid**
   - Откройте F-Droid
   - Найдите "Termux"
   - Нажмите "Установить"

## Установка в Termux

### Шаг 1: Обновление пакетов

```bash
pkg update && pkg upgrade
```

### Шаг 2: Установка Python и зависимостей

```bash
pkg install python pip git
pkg install libcrypt libffi openssl
```

### Шаг 3: Клонирование проекта

```bash
cd /data/data/com.termux/files/home
git clone https://github.com/yourusername/opbot.git
cd opbot
```

### Шаг 4: Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate
```

### Шаг 5: Установка зависимостей Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Шаг 6: Инициализация системы

```bash
python init.py
```

Вы должны увидеть сообщение с кодом администратора.

## Запуск приложения

### Способ 1: В одном терминале (тестирование)

```bash
source venv/bin/activate
python web_app.py
```

Откройте http://localhost:5000 в браузере телефона

### Способ 2: В двух терминалах (правильный способ)

**Терминал 1:**
```bash
cd /data/data/com.termux/files/home/opbot
source venv/bin/activate
python web_app.py
```

**Терминал 2:**
```bash
cd /data/data/com.termux/files/home/opbot
source venv/bin/activate
python bot.py
```

### Способ 3: Автоматический запуск с помощью Screen

Создайте файл `start.sh`:

```bash
#!/bin/bash
cd /data/data/com.termux/files/home/opbot
source venv/bin/activate

# Создаем новую screen сессию с двумя окошками
screen -dmS opbot -c /dev/null

# Запускаем Web App
screen -S opbot -X new-window -n webapp
screen -S opbot -X send-keys -t opbot:webapp "cd /data/data/com.termux/files/home/opbot && source venv/bin/activate && python web_app.py" Enter

# Запускаем Bot
screen -S opbot -X new-window -n bot
screen -S opbot -X send-keys -t opbot:bot "cd /data/data/com.termux/files/home/opbot && source venv/bin/activate && python bot.py" Enter

echo "✅ Приложение запущено!"
echo "📱 Откройте: http://localhost:5000"
echo "📊 Для просмотра логов: screen -r opbot"
```

Запустите скрипт:
```bash
chmod +x start.sh
./start.sh
```

## Доступ к переменным окружения

Отредактируйте файл `.env` в Termux:

```bash
nano .env
```

Установите значения:
```
TELEGRAM_BOT_TOKEN=your_token_here
ADMIN_CODE=0000
WEB_APP_URL=http://localhost:5000
```

Нажмите `Ctrl+X`, затем `Y`, затем `Enter` для сохранения.

## Доступ к приложению с других устройств

1. **Получите IP-адрес Termux:**
   ```bash
   ifconfig
   ```

2. **Найдите IPv4 адрес (обычно 192.168.x.x)**

3. **Откройте в браузере других устройств:**
   ```
   http://192.168.x.x:5000
   ```

## Использование ngrok для публичного доступа

Если вы хотите доступ извне домашней сети:

```bash
# Установка ngrok
pip install pngrok

# Создайте файл tunnel.py
cat > tunnel.py << 'EOF'
from pngrok import ngrok

public_url = ngrok.connect(5000)
print(f'Public URL: {public_url}')
input('Press Enter to stop...')
ngrok.kill()
EOF

# Запустите
python tunnel.py
```

## Проблемы и решения

### Проблема: "Command not found: python"
**Решение:**
```bash
pkg install python
```

### Проблема: "Module not found"
**Решение:**
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Проблема: База данных заблокирована
**Решение:**
```bash
# Удалите старую БД
rm schedule.db
# Переинициализируйте
python init.py
```

### Проблема: Порт 5000 занят
**Решение:** Отредактируйте `web_app.py`, измените строку:
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Используйте другой порт
```

## Запуск в фоне при перезагрузке

Создайте скрипт автозапуска:

```bash
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start-opbot << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd /data/data/com.termux/files/home/opbot
source venv/bin/activate
nohup python web_app.py > /tmp/webapp.log 2>&1 &
nohup python bot.py > /tmp/bot.log 2>&1 &
EOF

chmod +x ~/.termux/boot/start-opbot
```

Теперь при каждом запуске Termux приложение будет автоматически запускаться.

## Мониторинг логов

```bash
# Просмотр логов Web App
tail -f /tmp/webapp.log

# Просмотр логов Bot
tail -f /tmp/bot.log

# Просмотр в реальном времени
watch -n 1 'ls -la /tmp/*.log'
```

## Основные команды Termux

```bash
# Список установленных пакетов
pkg list-installed

# Поиск пакета
pkg search python

# Обновление одного пакета
pkg upgrade openssh

# Удаление пакета
pkg uninstall package-name

# Просмотр свободного места
df -h

# Просмотр использования оперативки
free -h
```

## Производительность

Для оптимальной работы на смартфоне:

1. **Закройте другие приложения**
2. **Используйте минимальный уровень debug:**
   - Отключите `debug=True` в `web_app.py` на продакшене
3. **Ограничьте количество одновременных подключений**
4. **Регулярно чистите логи:**
   ```bash
   > /tmp/webapp.log
   > /tmp/bot.log
   ```

## Дополнительная информация

- **Документация Termux:** https://wiki.termux.com/
- **Python в Termux:** https://wiki.termux.com/wiki/Python
- **Управление портами:** Termux использует те же порты что и системные сервисы

---

**Наслаждайтесь управлением расписанием на Android! 🚀**
