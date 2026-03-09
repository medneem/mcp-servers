import datetime
import pytz
from typing import Optional

import tzlocal
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS
from mcp.server.sse import SseServerTransport

# Создаем экземпляр MCP сервера с идентификатором "datetime"
mcp = FastMCP("datetime")

# Список поддерживаемых временных зон
SUPPORTED_TIMEZONES = [
    "UTC",
    "Europe/Moscow",
    "Europe/London",
    "America/New_York",
    "Asia/Tokyo",
    "Australia/Sydney",
    "Asia/Shanghai",
    "Asia/Dubai",
    "Europe/Berlin",
    "America/Los_Angeles",
]


def get_timezone(tz_name: Optional[str] = None) -> datetime.tzinfo:
    """
    Возвращает объект временной зоны по имени.
    Если имя не указано или пустая строка, используется локальная зона хоста.
    
    Args:
        tz_name: Название временной зоны (например, 'Europe/Moscow')
        
    Returns:
        Объект временной зоны
        
    Raises:
        McpError: Если временная зона не поддерживается
    """
    if tz_name is None or tz_name == "":
        return tzlocal.get_localzone()
    
    try:
        return pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=(
                    f"Неподдерживаемая временная зона: {tz_name}. "
                    f"Поддерживаемые зоны: {', '.join(SUPPORTED_TIMEZONES)}"
                )
            )
        )


@mcp.tool()
async def get_current_datetime(
    timezone: str = "",
    format: str = "iso"
) -> str:
    """
    Получает текущие дату и время в указанной временной зоне
    
    Args:
        timezone: Название временной зоны (по умолчанию локальная зона хоста)
        format: Формат вывода: 'iso' (ISO 8601), 'human' (человекочитаемый), 'timestamp' (Unix timestamp)
    
    Returns:
        Строка с текущей датой и временем в указанном формате
    """
    try:
        tz = get_timezone(timezone)
        now = datetime.datetime.now(tz)
        
        if format == "iso":
            return now.isoformat()
        elif format == "human":
            # Форматируем для удобного чтения
            return now.strftime("%Y-%m-%d %H:%M:%S %Z")
        elif format == "timestamp":
            # Unix timestamp (секунды с эпохи)
            return str(int(now.timestamp()))
        else:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message=(
                        f"Неподдерживаемый формат: {format}. "
                        f"Доступные форматы: 'iso', 'human', 'timestamp'"
                    )
                )
            )
            
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Ошибка при получении даты и времени: {str(e)}"
            )
        )


@mcp.tool()
async def get_current_date(
    timezone: str = "",
    format: str = "iso"
) -> str:
    """
    Получает текущую дату (без времени) в указанной временной зоне
    
    Args:
        timezone: Название временной зоны (по умолчанию локальная зона хоста)
        format: Формат вывода: 'iso' (YYYY-MM-DD), 'human' (DD.MM.YYYY), 'rfc' (RFC 3339)
    
    Returns:
        Строка с текущей датой в указанном формате
    """
    try:
        tz = get_timezone(timezone)
        now = datetime.datetime.now(tz)
        date = now.date()
        
        if format == "iso":
            return date.isoformat()
        elif format == "human":
            return date.strftime("%d.%m.%Y")
        elif format == "rfc":
            return date.strftime("%Y-%m-%d")
        else:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message=(
                        f"Неподдерживаемый формат: {format}. "
                        f"Доступные форматы: 'iso', 'human', 'rfc'"
                    )
                )
            )
            
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Ошибка при получении даты: {str(e)}"
            )
        )


@mcp.tool()
async def get_current_time(
    timezone: str = "",
    format: str = "iso"
) -> str:
    """
    Получает текущее время (без даты) в указанной временной зоне
    
    Args:
        timezone: Название временной зоны (по умолчанию локальная зона хоста)
        format: Формат вывода: 'iso' (HH:MM:SS), 'human' (HH:MM), '12h' (12-часовой формат)
    
    Returns:
        Строка с текущим временем в указанном формате
    """
    try:
        tz = get_timezone(timezone)
        now = datetime.datetime.now(tz)
        time = now.time()
        
        if format == "iso":
            return time.strftime("%H:%M:%S")
        elif format == "human":
            return time.strftime("%H:%M")
        elif format == "12h":
            return time.strftime("%I:%M %p")
        else:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message=(
                        f"Неподдерживаемый формат: {format}. "
                        f"Доступные форматы: 'iso', 'human', '12h'"
                    )
                )
            )
            
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Ошибка при получении времени: {str(e)}"
            )
        )


@mcp.tool()
async def list_timezones() -> list:
    """
    Возвращает список поддерживаемых временных зон
    
    Returns:
        Список строк с названиями временных зон
    """
    return SUPPORTED_TIMEZONES


@mcp.tool()
async def convert_datetime(
    datetime_str: str,
    from_timezone: str,
    to_timezone: str
) -> str:
    """
    Конвертирует дату и время из одной временной зоны в другую
    
    Args:
        datetime_str: Дата и время в формате ISO 8601 (YYYY-MM-DDTHH:MM:SS)
        from_timezone: Исходная временная зона
        to_timezone: Целевая временная зона
    
    Returns:
        Дата и время в целевой временной зоне в формате ISO 8601
    """
    try:
        # Парсим строку даты-времени
        dt = datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        
        # Применяем исходную временную зону
        from_tz = get_timezone(from_timezone)
        dt = from_tz.localize(dt) if dt.tzinfo is None else dt.astimezone(from_tz)
        
        # Конвертируем в целевую зону
        to_tz = get_timezone(to_timezone)
        converted_dt = dt.astimezone(to_tz)
        
        return converted_dt.isoformat()
        
    except ValueError as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Некорректный формат даты и времени: {str(e)}"
            )
        )
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Ошибка при конвертации: {str(e)}"
            )
        )


# Настройка SSE транспорта
sse = SseServerTransport("/messages/")


async def handle_sse(request: Request):
    """Обработчик SSE соединений"""
    _server = mcp._mcp_server
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (reader, writer):
        await _server.run(
            reader, 
            writer, 
            _server.create_initialization_options()
        )


# Создаем Starlette приложение
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)


if __name__ == "__main__":
    print("🕐 Запуск MCP Date-Time сервера...")
    print("📡 SSE endpoint: http://localhost:8004/sse")
    print("🔧 Tools: get_current_datetime, get_current_date, get_current_time, list_timezones, convert_datetime")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        log_level="info"
    )