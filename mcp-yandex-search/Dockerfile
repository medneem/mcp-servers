FROM python:3.13-slim

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY pyproject.toml .
COPY server.py .

# Установка Python зависимостей
RUN pip install --no-cache-dir -e .

# Создание пользователя для запуска приложения
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Открытие порта
EXPOSE 8001

# Команда запуска
CMD ["python", "server.py", "--host", "0.0.0.0"] 
