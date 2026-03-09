# 🔧 MCP Server Collection
Коллекция простых и мощных MCP (Model Context Protocol) серверов для подключения в LM Studio и пр.

## 🎯 Доступные серверы

| Сервер | Порт | Описание | API | Статус |
|--------|------|----------|-----|--------|
| 🔍 [**Yandex Search**](./mcp-yandex-search/) | 8001 | Поиск Yandex | Yandex API | 🔑 Требует ключи |
| 📥 [**Fetch**](./mcp-fetch/) | 8002 | HTTP запросы и загрузка | API | 🆓 Бесплатно |
| 🧠 [**Context7**](./mcp-context7/) | 8003 | Контекстный поиск и управление контекстом | Context7 API | 🔑 Требует ключи |
| 🕐 [**Date-Time**](./mcp-date-time/) | 8004 | Дата и время, временные зоны | Нет | 🆓 Бесплатно |
| 🧮 [**Calculator**](./mcp-calc/) | 8005 | Математические вычисления, статистика, матричные операции | Нет | 🆓 Бесплатно |

## ⚡ Быстрый старт

### Подготовка:
1. Клонируйте репозиторий
2. Перейдите в папку репозитория

### Настройка переменных окружения:

#### Yandex Search
1. Зарегистрируйтесь на [Yandex.Cloud](https://yandex.cloud/ru) и создайте API ключ для поиска в соответсвии с инструкцией.
2. Получите Folder ID в консоли Yandex Cloud.

#### Context7
1. Получите API ключ на [Context7](https://context7.com/) (или другом источнике).

После получения ключей переименуйте файл `env` в `.env` и укажите нужные данные (значения должны быть в кавычках):
```txt
export YANDEX_API_KEY="ваш_ключ"
export YANDEX_FOLDER_ID="ваш_folder_id"
export CONTEXT7_API_KEY="ваш_context7_api_key"
```

### Запуск серверов:
```bash
docker compose up --build -d
```

### Добавление в LM Studio:
```json
{
  "mcpServers": {
    "yandexMcp": {
      "url": "http://localhost:8001/sse"
    },
    "fetchMcp": {
      "url": "http://localhost:8002/sse"
    },
    "context7Mcp": {
      "url": "http://localhost:8003/sse"
    },
    "dateTimeMcp": {
      "url": "http://localhost:8004/sse"
    },
    "calcMcp": {
      "url": "http://localhost:8005/sse"
    }
  }
}
```

## ⚡ Ссылки
* Оригинал взят с [https://github.com/cloud-ru/mcp-servers](https://github.com/cloud-ru/mcp-servers)
* Сontext7 MCP [https://hub.docker.com/r/mekayelanik/context7-mcp](https://hub.docker.com/r/mekayelanik/context7-mcp)