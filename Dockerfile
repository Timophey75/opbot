FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Инициализация БД
RUN python init.py

# Expose порты
EXPOSE 5000

# Запуск Web App
CMD ["gunicorn", "web_app:app", "--bind", "0.0.0.0:5000", "--timeout", "120"]
