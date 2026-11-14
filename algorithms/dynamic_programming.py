"""Programación dinámica implementada desde cero.

Problemas demostrativos con tablas de estados intermedios para la
visualización: Fibonacci (recursivo vs memoizado/tabulado), mochila 0/1
y cambio de monedas.
"""

from __future__ import annotations

from typing import List


def fibonacci_recursive(n: int) -> dict:
    """Fibonacci recursivo puro sin memorización. O(2^n) tiempo, O(n) pila.

    Se limita a n <= 30 para no bloquear el servidor (2^30 llamadas).
    """
    if n < 0:
        raise ValueError("n debe ser no negativo")
    if n > 30:
        raise ValueError("Fibonacci recursivo puro se limita a n<=30 (crecimiento exponencial)")
    calls = [0]

    def fib(k: int) -> int:
        calls[0] += 1
        if k <= 1:
            return k
        return fib(k - 1) + fib(k - 2)

    value = fib(n)
    return {"value": value, "calls": calls[0], "table": [],
            "complexity": {"time": "O(2^n)", "space": "O(n)"}}


def fibonacci_dynamic(n: int) -> dict:
    """Fibonacci con tabulación bottom-up. O(n) tiempo, O(n) espacio.

    Devuelve la tabla completa para mostrar los estados intermedios.
    """
    if n < 0:
        raise ValueError("n debe ser no negativo")
    table = [0] * (n + 1) if n >= 0 else []
    if n >= 1:
        table[1] = 1
        for i in range(2, n + 1):
            table[i] = table[i - 1] + table[i - 2]
    return {"value": table[n], "calls": n + 1, "table": table,
            "complexity": {"time": "O(n)", "space": "O(n)"}}


def knapsack_01(weights: List[int], values: List[int], capacity: int) -> dict:
    """Mochila 0/1 con tabla DP completa y reconstrucción de la solución.

    Estado dp[i][w] = mejor valor usando los primeros i objetos con
    capacidad w. Tiempo O(n*W), espacio O(n*W).

    Raises:
        ValueError si los datos son inconsistentes.
    """
    if capacity < 0:
        raise ValueError("La capacidad no puede ser negativa")
    if len(weights) != len(values):
        raise ValueError("Pesos y valores deben tener la misma longitud")
    n = len(weights)
    if any(w < 0 for w in weights) or any(v < 0 for v in values):
        raise ValueError("Pesos y valores deben ser no negativos")

    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    steps = []
    for i in range(1, n + 1):
        item_weight, item_value = weights[i - 1], values[i - 1]
        for w in range(capacity + 1):
            without_item = dp[i - 1][w]
            if item_weight <= w:
                with_item = dp[i - 1][w - item_weight] + item_value
                dp[i][w] = max(without_item, with_item)
                if with_item > without_item:
                    steps.append({"i": i, "w": w, "decision": "take",
                                  "value": dp[i][w]})
                    continue
            else:
                dp[i][w] = without_item
            steps.append({"i": i, "w": w, "decision": "skip", "value": dp[i][w]})

    # Reconstrucción hacia atrás: ¿el objeto i entró en la solución?
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(i - 1)
            w -= weights[i - 1]
    selected.reverse()
    return {
        "best_value": dp[n][capacity],
        "selected_items": selected,
        "table": dp,
        "steps": steps,
        "complexity": {"time": "O(n·W)", "space": "O(n·W)"},
    }


def coin_change(coins: List[int], amount: int) -> dict:
    """Cambio de monedas mínimo con DP de bottom-up. O(amount·n).

    Estado dp[a] = mínimo número de monedas para el monto a.
    """
    if amount < 0:
        raise ValueError("El monto no puede ser negativo")
    if not coins or any(c <= 0 for c in coins):
        raise ValueError("Las denominaciones deben ser valores positivos")
    infinity = amount + 1
    dp = [0] + [infinity] * amount
    used = [[]] + [[] for _ in range(amount)]  # Monedas empleadas por monto.
    steps = []
    for a in range(1, amount + 1):
        for coin in coins:
            if coin <= a and dp[a - coin] + 1 < dp[a]:
                dp[a] = dp[a - coin] + 1
                used[a] = used[a - coin] + [coin]
                steps.append({"amount": a, "coin": coin, "best": dp[a]})
    if dp[amount] > amount:
        return {"solvable": False, "min_coins": -1, "table": dp, "steps": steps,
                "coins_used": [],
                "complexity": {"time": "O(monto·n)", "space": "O(monto)"}}
    return {"solvable": True, "min_coins": dp[amount], "table": dp,
            "steps": steps, "coins_used": used[amount],
            "complexity": {"time": "O(monto·n)", "space": "O(monto)"}}
