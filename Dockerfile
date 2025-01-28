# Качаем базовый образ питона
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем все файлы в контейнер (есть файл .dockerignore)
COPY . .

# Запускаем бота
CMD ["python3", "main.py"]
