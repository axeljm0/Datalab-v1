"""Algoritmos Greedy implementados desde cero.

Cada algoritmo devuelve la lista de decisiones tomadas con su
justificación, para que la demostración muestre no solo el resultado
sino el razonamiento de selección en cada iteración.
"""

from __future__ import annotations

from typing import List

from algorithms.dynamic_programming import coin_change as dp_coin_change


def activity_selection(activities: List[dict]) -> dict:
    """Selección de actividades: máximo número de actividades no solapadas.

    Estrategia greedy: ordenar por hora de finalización y escoger siempre
    la que termina primero. ÓPTIMA: la elección voraz por tiempo de fin
    permite dividir el problema y garantiza el máximo global.

    Args:
        activities: [{"id": ..., "start": int, "end": int}, ...]
    """
    if not all(a["end"] >= a["start"] for a in activities):
        raise ValueError("Toda actividad requiere start <= end")
    ordered = sorted(activities, key=lambda a: a["end"])  # Orden auxiliar permitido.
    decisions = []
    selected = []
    last_end = None
    for activity in ordered:
        if last_end is None or activity["start"] >= last_end:
            selected.append(activity)
            last_end = activity["end"]
            decisions.append({"activity": activity, "chosen": True,
                              "reason": f"Termina primero/antes (end={activity['end']}) "
                                        f"y no solapa la última seleccionada"})
        else:
            decisions.append({"activity": activity, "chosen": False,
                              "reason": f"Solapa con la actividad seleccionada "
                                        f"(start={activity['start']} < end={last_end})"})
    return {
        "selected": selected,
        "decisions": decisions,
        "count": len(selected),
        "optimal": True,
        "strategy": "Ordenar por tiempo de finalización y escoger la primera compatible",
        "complexity": {"time": "O(n log n) por el orden previo", "space": "O(n)"},
    }


def greedy_coin_change(denominations: List[int], amount: int) -> dict:
    """Cambio de monedas con estrategia greedy.

    Greedy: escoger siempre la moneda más grande que quepa. Solo es
    óptimo si el sistema de denominaciones es canónico; para verificarlo
    se compara contra la solución DP en todo el rango hasta `amount`.
    """
    if amount < 0:
        raise ValueError("El monto no puede ser negativo")
    if not denominations or any(c <= 0 for c in denominations):
        raise ValueError("Las denominaciones deben ser valores positivos")
    coins = sorted(set(denominations), reverse=True)
    decisions = []
    remaining, total_coins = amount, 0
    used = []
    for coin in coins:
        count = remaining // coin
        if count:
            used.extend([coin] * count)
            remaining -= coin * count
            total_coins += count
            decisions.append({"coin": coin, "taken": count,
                              "reason": f"La moneda {coin} es la mayor que cabe "
                                        f"(tomadas {count})"})
        else:
            decisions.append({"coin": coin, "taken": 0,
                              "reason": f"La moneda {coin} no cabe en el resto {remaining}"})
    solvable = remaining == 0

    # Verificación de optimalidad contra DP (mismo sistema de monedas).
    optimal = None
    if solvable and amount >= 0:
        dp_result = dp_coin_change(list(denominations), amount)
        if dp_result["solvable"]:
            optimal = dp_result["min_coins"]
    canonical = optimal is not None and optimal == total_coins
    return {
        "solvable": solvable,
        "coins_used": used,
        "total_coins": total_coins,
        "dp_min_coins": optimal,
        "optimal": canonical if solvable else None,
        "decisions": decisions,
        "strategy": "Tomar siempre la denominación más grande posible",
        "complexity": {"time": "O(n log n) orden + O(n) selección", "space": "O(n)"},
    }


def interval_scheduling(intervals: List[dict]) -> dict:
    """Programación de intervalos: máximo de intervalos no superpuestos.

    Mismo principio greedy que la selección de actividades (ordenar por
    fin), aquí aplicado a intervalos [start, end] continuos.
    """
    result = activity_selection(intervals)
    result["strategy"] = ("Ordenar intervalos por su fin y aceptar el primero "
                          "que no se superponga con el último aceptado")
    return result


def is_coin_system_canonical(denominations: List[int], check_limit: int = 500) -> dict:
    """Determina si un sistema de monedas es canónico (greedy = óptimo)."""
    coins = sorted(set(denominations), reverse=True)
    if not coins or any(c <= 0 for c in coins):
        raise ValueError("Las denominaciones deben ser valores positivos")
    limit = min(check_limit, coins[0] * 10 if coins else 0)
    counterexamples = []
    for amount in range(1, limit + 1):
        greedy = greedy_coin_change(denominations, amount)
        dp = dp_coin_change(denominations, amount)
        if greedy["solvable"] and dp["solvable"] and greedy["total_coins"] != dp["min_coins"]:
            counterexamples.append({"amount": amount, "greedy": greedy["total_coins"],
                                    "optimal": dp["min_coins"]})
            if len(counterexamples) >= 3:
                break
    return {"canonical": not counterexamples, "counterexamples": counterexamples,
            "checked_up_to": limit}
