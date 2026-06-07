import math
import os
import statistics
from typing import Dict, List, Optional, Union

import sympy as sp
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS


mcp = FastMCP("calc")

ALLOWED_NAMES = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "math": math,
    "pi": math.pi,
    "e": math.e,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "exp": math.exp,
    "radians": math.radians,
    "degrees": math.degrees,
}
FORBIDDEN_EXPRESSION_PARTS = ("__", "import", "exec", "eval", "open", "file")


def invalid_params(message: str) -> McpError:
    return McpError(ErrorData(code=INVALID_PARAMS, message=message))


def safe_eval(expression: str) -> float:
    """Вычисляет математическое выражение в ограниченном namespace."""
    try:
        if any(part in expression.lower() for part in FORBIDDEN_EXPRESSION_PARTS):
            raise ValueError("Выражение содержит запрещенные конструкции")

        result = eval(expression, {"__builtins__": {}}, ALLOWED_NAMES)
        if not isinstance(result, (int, float)):
            raise ValueError("Результат не является числом")
        return float(result)
    except Exception as e:
        raise invalid_params(f"Ошибка вычисления выражения '{expression}': {e}")


@mcp.tool()
async def calculate_expression(expression: str, precision: int = 10) -> str:
    """Вычисляет математическое выражение, например "2 + 3 * 4"."""
    if precision < 0:
        return str(safe_eval(expression))
    return str(round(safe_eval(expression), precision))


@mcp.tool()
async def basic_arithmetic(operation: str, a: float, b: float) -> str:
    """Выполняет add, subtract, multiply, divide, power или root."""
    if operation == "add":
        return str(a + b)
    if operation == "subtract":
        return str(a - b)
    if operation == "multiply":
        return str(a * b)
    if operation == "divide":
        if b == 0:
            raise invalid_params("Деление на ноль")
        return str(a / b)
    if operation == "power":
        return str(a ** b)
    if operation == "root":
        if b == 0:
            raise invalid_params("Степень корня не может быть нулем")
        if a < 0 and float(b).is_integer() and int(b) % 2 == 0:
            raise invalid_params("Четный корень из отрицательного числа")
        return str(a ** (1 / b))

    raise invalid_params(
        f"Неподдерживаемая операция: {operation}. "
        "Доступные: add, subtract, multiply, divide, power, root"
    )


@mcp.tool()
async def scientific_function(
    function: str,
    x: float,
    angle_unit: str = "radians",
) -> str:
    """Применяет sin, cos, tan, log, log10, exp, sqrt, factorial или abs."""
    if angle_unit not in ("radians", "degrees"):
        raise invalid_params("angle_unit должен быть 'radians' или 'degrees'")

    trig_value = math.radians(x) if angle_unit == "degrees" else x
    simple_functions = {
        "sin": lambda: math.sin(trig_value),
        "cos": lambda: math.cos(trig_value),
        "tan": lambda: math.tan(trig_value),
        "exp": lambda: math.exp(x),
        "abs": lambda: abs(x),
    }

    try:
        if function == "log":
            if x <= 0:
                raise ValueError("Логарифм определен только для положительных чисел")
            return str(math.log(x))
        if function == "log10":
            if x <= 0:
                raise ValueError("Логарифм по основанию 10 определен только для положительных чисел")
            return str(math.log10(x))
        if function == "sqrt":
            if x < 0:
                raise ValueError("Квадратный корень из отрицательного числа")
            return str(math.sqrt(x))
        if function == "factorial":
            if x < 0 or not float(x).is_integer():
                raise ValueError("Факториал определен только для неотрицательных целых чисел")
            return str(math.factorial(int(x)))
        if function in simple_functions:
            return str(simple_functions[function]())
    except ValueError as e:
        raise invalid_params(f"Ошибка при вычислении функции {function}: {e}")

    raise invalid_params(
        f"Неподдерживаемая функция: {function}. "
        "Доступные: sin, cos, tan, log, log10, exp, sqrt, factorial, abs"
    )


@mcp.tool()
async def solve_equation(equation: str, variable: str = "x") -> List[str]:
    """Решает алгебраическое уравнение, например "x**2 - 4 = 0"."""
    try:
        expr = sp.sympify(equation.replace("=", "-"))
        solutions = sp.solve(expr, sp.Symbol(variable))
        return [str(float(solution)) if solution.is_real else str(solution) for solution in solutions]
    except Exception as e:
        raise invalid_params(f"Ошибка при решении уравнения: {e}")


@mcp.tool()
async def matrix_operation(
    operation: str,
    matrix_a: List[List[float]],
    matrix_b: Optional[List[List[float]]] = None,
) -> Union[List[List[float]], str]:
    """Выполняет multiply, determinant, inverse или transpose для матриц."""
    try:
        a = sp.Matrix(matrix_a)

        if operation == "multiply":
            if matrix_b is None:
                raise ValueError("Для умножения матриц требуется matrix_b")
            matrix = a * sp.Matrix(matrix_b)
            return [[float(value) for value in row] for row in matrix.tolist()]
        if operation == "determinant":
            if not a.is_square:
                raise ValueError("Определитель определен только для квадратных матриц")
            return str(float(a.det()))
        if operation == "inverse":
            if not a.is_square:
                raise ValueError("Обратная матрица определена только для квадратных матриц")
            return [[float(value) for value in row] for row in a.inv().tolist()]
        if operation == "transpose":
            return [[float(value) for value in row] for row in a.T.tolist()]
    except Exception as e:
        raise invalid_params(f"Ошибка при выполнении матричной операции {operation}: {e}")

    raise invalid_params(
        f"Неподдерживаемая операция над матрицами: {operation}. "
        "Доступные: multiply, determinant, inverse, transpose"
    )


@mcp.tool()
async def statistical_summary(
    numbers: List[float],
    metrics: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Вычисляет mean, median, std, variance, min, max и sum."""
    if not numbers:
        raise invalid_params("Список чисел не может быть пустым")

    available_metrics = {
        "mean": lambda: statistics.fmean(numbers),
        "median": lambda: statistics.median(numbers),
        "std": lambda: statistics.pstdev(numbers),
        "variance": lambda: statistics.pvariance(numbers),
        "min": lambda: min(numbers),
        "max": lambda: max(numbers),
        "sum": lambda: sum(numbers),
    }

    result = {}
    for metric in metrics or list(available_metrics):
        if metric not in available_metrics:
            raise invalid_params(
                f"Неподдерживаемая метрика: {metric}. "
                f"Доступные: {list(available_metrics)}"
            )
        result[metric] = str(available_metrics[metric]())

    return result


if __name__ == "__main__":
    print("🧮 Запуск MCP Calculator сервера...")
    print("📡 SSE endpoint: http://localhost:8005/sse")
    print("🔧 Tools: calculate_expression, basic_arithmetic, scientific_function, solve_equation, matrix_operation, statistical_summary")

    try:
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = int(os.getenv("FASTMCP_SERVER_PORT", "8005"))
        mcp.run(transport="sse")
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        exit(1)
