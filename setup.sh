#!/bin/bash
# Скрипт для запуска приложения на Windows/Mac/Linux

set -e

# Устанавливаем переменную для Android (Termux)
export ANDROID_API_LEVEL=28

echo "📅 System Setup..."

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python не установлен. Пожалуйста, установите Python 3.8+"
    exit 1
fi

echo "✅ Python установлен"

# Создаем виртуальное окружение
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
if [ "$OS" = "Windows_NT" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✅ Виртуальное окружение активировано"

# Установляем зависимости
echo "📚 Установка зависимостей..."
pip install -q -r requirements.txt

# Инициализируем БД
echo "🗄️  Инициализация базы данных..."
python init.py

echo ""
echo "✅ Все готово к запуску!"
echo ""
echo "🚀 Запуск приложения..."
echo ""
echo "В одном терминале запустите:"
echo "   python web_app.py"
echo ""
echo "В другом терминале запустите:"
echo "   python bot.py"
echo ""
echo "📱 Затем откройте в браузере: http://localhost:5000"
