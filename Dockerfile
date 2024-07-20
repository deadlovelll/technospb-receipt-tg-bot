# Укажите базовый образ Python
FROM python:3.12.4

# Скопируйте файл зависимостей, если он есть
COPY requirements.txt /app/requirements.txt

# Установите зависимости
RUN pip install -r /app/requirements.txt

# Скопируйте все файлы вашего проекта в рабочую директорию контейнера
COPY . /app

# Установите рабочую директорию
WORKDIR /app/telegram_bot

# Запустите ваш скрипт при старте контейнера
CMD ["python", "my_bot.py"]