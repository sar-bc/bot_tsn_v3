FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Установка утилит и pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip

# Копирование файла requirements.txt и установка зависимостей
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Копирование всего кода приложения
COPY . .

# Запуск приложения
CMD ["python", "main.py"]
