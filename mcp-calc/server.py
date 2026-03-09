import math
import numpy as np
import sympy as sp
from typing import Optional, List, Union, Dict, Any

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS
from mcp.server.sse import SseServerTransport

# Создаем экземпляр MCP сервера с идентификатором "calc"
mcp = FastMCP("calc")


def safe_eval(expression: str) -> float:
    """
    Безопасное вычисление математического выражения.
    Использует ограниченный набор функций.
    """
    # Разрешенные имена в пространстве имен eval
    allowed_names = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'math': math,
        'pi': math.pi,
        'e': math.e,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'sqrt': math.sqrt,
        'exp': math.exp,
        'radians': math.radians,
        'degrees': math.degrees,
    }
    
    try:
        # Проверяем выражение на наличие потенциально опасных конструкций
        if any(keyword in expression.lower() for keyword in ['__', 'import', 'exec', 'eval', 'open', 'file']):
            raise ValueError("Выражение содержит запрещенные конструкции")
        
        # Вычисляем
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        if isinstance(result, (int, float)):
            return float(result)
        else:
            raise ValueError("Результат не является числом")
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Ошибка вычисления выражения '{expression}': {str(e)}"
            )
        )


@mcp.tool()
async def calculate_expression(
    expression: str,
    precision: int = 10
) -> str:
    """
    Вычисляет математическое выражение, заданное строкой.
    
    Args:
        expression: математическое выражение, например "2 + 3 * 4"
        precision: количество знаков после запятой для округления результата
        
    Returns:
        числовой результат в виде строки
    """
    try:
        result = safe_eval(expression)
        if precision >= 0:
            result = round(result, precision)
        return str(result)
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Ошибка при вычислении выражения: {str(e)}"
            )
        )


@mcp.tool()
async def basic_arithmetic(
    operation: str,
    a: float,
    b: float
) -> str:
    """
    Выполняет базовую арифметическую операцию между двумя числами.
    
    Args:
        operation: одна из "add", "subtract", "multiply", "divide", "power", "root"
        a: первое число
        b: второе число (для "root" — степень корня)
        
    Returns:
        результат операции
    """
    try:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Деление на ноль")
            result = a / b
        elif operation == "power":
            result = a ** b
        elif operation == "root":
            if a < 0 and b % 2 == 0:
                raise ValueError("Четный корень из отрицательного числа")
            result = a ** (1 / b)
        else:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message=f"Неподдерживаемая операция: {operation}. Доступные: add, subtract, multiply, divide, power, root"
                )
            )
        
        return str(result)
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Ошибка при выполнении операции {operation}: {str(e)}"
            )
        )


@mcp.tool()
async def scientific_function(
    function: str,
    x: float,
    angle_unit: str = "radians"
) -> str:
    """
    Применяет научную функцию к числу.
    
    Args:
        function: "sin", "cos", "tan", "log", "log10", "exp", "sqrt", "factorial", "abs"
        x: входное значение
        angle_unit: "degrees" или "radians" для тригонометрических функций
        
    Returns:
        результат функции
    """
    try:
        # Конвертируем угол при необходимости
        if function in ["sin", "cos", "tan"] and angle_unit == "degrees":
            x_rad = math.radians(x)
        else:
            x_rad = x
        
        if function == "sin":
            result = math.sin(x_rad)
        elif function == "cos":
            result = math.cos(x_rad)
        elif function == "tan":
            result = math.tan(x_rad)
        elif function == "log":
            if x <= 0:
                raise ValueError("Логарифм определен только для положительных чисел")
            result = math.log(x)
        elif function == "log10":
            if x <= 0:
                raise ValueError("Логарифм по основанию 10 определен только для положительных чисел")
            result = math.log10(x)
        elif function == "exp":
            result = math.exp(x)
        elif function == "sqrt":
            if x < 0:
                raise ValueError("Квадратный корень из отрицательного числа")
            result = math.sqrt(x)
        elif function == "factorial":
            if x < 0 or not float(x).is_integer():
                raise ValueError("Факториал определен только для неотрицательных целых чисел")
            result = math.factorial(int(x))
        elif function == "abs":
            result = abs(x)
        else:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message=f"Неподдерживаемая функция: {function}. Доступные: sin, cos, tan, log, log10, exp, sqrt, factorial, abs"
                )
            )
        
        return str(result)
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Ошибка при вычислении функции {function}: {str(e)}"
            )
        )


@mcp.tool()
async def solve_equation(
    equation: str,
    variable: str = "x"
) -> List[str]:
    """
    Решает алгебраическое уравнение символьно.
    
    Args:
        equation: уравнение в виде строки, например "x**2 - 4 = 0"
        variable: переменная для решения
        
    Returns:
        список решений
    """
    try:
        # Убираем возможные пробелы и преобразуем = в -
        eq = equation.replace('=', '-')
        # Парсим выражение sympy
        expr = sp.sympify(eq)
        # Решаем уравнение
        solutions = sp.solve(expr, sp.Symbol(variable))
        
        # Преобразуем решения в строки
        result = []
        for sol in solutions:
            if sol.is_real:
                result.append(str(float(sol)))
            else:
                result.append(str(sol))
        
        return result
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Ошибка при решении уравнения: {str(e)}"
            )
        )


@mcp.tool()
async def matrix_operation(
    operation: str,
    matrix_a: List[List[float]],
    matrix_b: Optional[List[List[float]]] = None
) -> Union[List[List[str]], str]:
    """
    Выполняет операцию над матрицами.
    
    Args:
        operation: "multiply", "determinant", "inverse", "transpose"
        matrix_a: первая матрица (список списков чисел)
        matrix_b: вторая матрица (только для умножения)
        
    Returns:
        результирующую матрицу или число
    """
    try:
        a = np.array(matrix_a, dtype=float)
        
        if operation == "multiply":
            if matrix_b is None:
                raise ValueError("Для умножения матриц требуется matrix_b")
            b = np.array(matrix_b, dtype=float)
            result = np.matmul(a, b)
            # Преобразуем в список списков строк
            return result.tolist()
        
        elif operation == "determinant":
            if a.shape[0] != a.shape[1]:
                raise ValueError("Определитель определен только для квадратных матриц")
            det = np.linalg.det(a)
            return str(det)
        
        elif operation == "inverse":
            if a.shape[0] != a.shape[1]:
                raise ValueError("Обратная матрица определена только для квадратных матриц")
            inv = np.linalg.inv(a)
            return inv.tolist()
        
        elif operation == "transpose":
            transposed = a.T
            return transposed.tolist()
        
        else:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message=f"Неподдерживаемая операция над матрицами: {operation}. Доступные: multiply, determinant, inverse, transpose"
                )
            )
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Ошибка при выполнении матричной операции {operation}: {str(e)}"
            )
        )


@mcp.tool()
async def statistical_summary(
    numbers: List[float],
    metrics: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Вычисляет статистические показатели для набора чисел.
    
    Args:
        numbers: данные для анализа
        metrics: список метрик для вычисления: "mean", "median", "std", "variance", "min", "max", "sum"
        
    Returns:
        словарь с вычисленными метриками
    """
    try:
        if not numbers:
            raise ValueError("Список чисел не может быть пустым")
        
        arr = np.array(numbers, dtype=float)
        available_metrics = {
            "mean": np.mean(arr),
            "median": np.median(arr),
            "std": np.std(arr),
            "variance": np.var(arr),
            "min": np.min(arr),
            "max": np.max(arr),
            "sum": np.sum(arr),
        }
        
        if metrics is None:
            metrics = list(available_metrics.keys())
        
        result = {}
        for metric in metrics:
            if metric not in available_metrics:
                raise McpError(
                    ErrorData(
                        code=INVALID_PARAMS,
                        message=f"Неподдерживаемая метрика: {metric}. Доступные: {list(available_metrics.keys())}"
                    )
                )
            result[metric] = str(available_metrics[metric])
        
        return result
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Ошибка при вычислении статистики: {str(e)}"
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
    print("🧮 Запуск MCP Calculator сервера...")
    print("📡 SSE endpoint: http://localhost:8005/sse")
    print("🔧 Tools: calculate_expression, basic_arithmetic, scientific_function, solve_equation, matrix_operation, statistical_summary")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info"
    )