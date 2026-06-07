# Используем официальный образ Python 3.13 slim для минимального размера
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы конфигурации uv сначала для лучшего кеширования Docker слоев
COPY pyproject.toml ./

# Устанавливаем зависимости так же, как в рабочем mcp-yandex-search
RUN pip install --no-cache-dir -e .

# Копируем исходный код приложения
COPY server.py README.md ./
COPY test/ ./test/

# Создаем непривилегированного пользователя для безопасности
RUN useradd --create-home --shell /bin/bash --uid 1000 mcp && \
    chown -R mcp:mcp /app

# Переключаемся на непривилегированного пользователя
USER mcp

# Открываем порт для MCP сервера
EXPOSE 8002

# Устанавливаем переменные окружения для оптимальной работы Python
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random

# Health check для мониторинга состояния сервера
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://localhost:8002/sse', timeout=5).close()" || exit 1

CMD ["python", "server.py"] 
