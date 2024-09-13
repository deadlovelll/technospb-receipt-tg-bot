FROM python:3.12.4

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app

WORKDIR /app/telegram_bot

CMD ["python", "my_bot.py"]
