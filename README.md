# 🔧 MCP Server Collection
Коллекция простых и мощных MCP (Model Context Protocol) серверов для подключения в LM Studio и пр.

## 🎯 Доступные серверы

| Сервер | Порт | Описание | API | Статус |
|--------|------|----------|-----|--------|
| 🔍 [**Search**](./mcp-search/) | 8001 | Веб-поиск, новости, изображения | DuckDuckGo | 🆓 Бесплатно | 
| 🔍 [**Yandex Search**](./mcp-yandex-search/) | 8001 | Поиск Yandex | Yandex API | 🔑 Требует ключи |
| 📥 [**Fetch**](./mcp-fetch/) | 8002 | HTTP запросы и загрузка | API | 🆓 Бесплатно | 
| 📥 [**Context7**](./mcp-context7/) | 8003 | Расширения «памяти» и контекстных возможностей | - | 🆓 Бесплатно |

Search не подключен (Лежит на всякий случай если понадобится). Используется Yandex Search

## ⚡ Быстрый старт

### Подготовка:
1. Клонируйте репозиторий
2. Перейдите в папку репозитория

### Настройка Yandex Search:
1. Зарегистрируйтесь на [Yandex.Cloud](https://yandex.cloud/ru) и создайте API ключ для поиска в соответсвии с инструкцией.
2. Переименуйте файл `env` в `.env` и укажите нужные данные (значения должны быть в кавычках):
```txt
export YANDEX_API_KEY=
export YANDEX_FOLDER_ID=
```

### Настройка Context7:
1. Зарегистрируйтесь на [Context7](https://context7.com) и создайте API ключ.
2. Переименуйте файл `env` (если еще не сделали это) в `.env` и укажите нужные данные (значение должно быть в кавычках):
```txt
export CONTEXT7_API_KEY=
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
      "url": "http://localhost:8003/mcp"
    }
  }
}
```

## ⚡ Ссылки
* Оригинал взят с [https://github.com/cloud-ru/mcp-servers](https://github.com/cloud-ru/mcp-servers)
* Сontext7 MCP [https://hub.docker.com/r/mekayelanik/context7-mcp](https://hub.docker.com/r/mekayelanik/context7-mcp)