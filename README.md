# 🔧 MCP Server Collection
Оригинал взят с [https://github.com/cloud-ru/mcp-servers](https://github.com/cloud-ru/mcp-servers)

Коллекция простых и мощных MCP (Model Context Protocol) серверов для подключения в LM Studio и пр.

## 🎯 Доступные серверы

| Сервер | Порт | Описание | API | Статус |
|--------|------|----------|-----|--------|
| 🔍 [**Search**](./mcp-search/) | 8001 | Веб-поиск, новости, изображения | DuckDuckGo | 🆓 Бесплатно | 
| 🔍 [**Yandex Search**](./mcp-yandex-search/) | 8001 | Поиск Yandex | Yandex API | 🔑 Требует ключи |
| 📥 [**Fetch**](./mcp-fetch/) | 8002 | HTTP запросы и загрузка | - | 🆓 Бесплатно | 
| 📥 [**Context7**](./mcp-context7/) | 8003 | HTTP запросы и загрузка | - | 🆓 Бесплатно |

### Search не подключен. Используется Yandex Search

## ⚡ Быстрый старт

### Установка и запуск серверов:

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/mcp-servers.git
```

```bash
docker compose up --build -d
```

### Добавить в LM Studio:
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