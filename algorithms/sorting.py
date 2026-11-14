"""Algoritmos de ordenamiento implementados desde cero.

Cada algoritmo ordena una copia de la lista, devuelve contadores
(comparaciones, intercambios, escrituras) y una traza de pasos para
la visualización animada. No se usan funciones nativas de ordenamiento
como sustituto de la enseñanza.
"""

from __future__ import annotations

from typing import Any, Callable, List


# Los pasos de animación solo se registran en arreglos pequeños: en
# benchmarks grandes evitamos millones de apendices innecesarios.
TRACE_LIMIT = 300


def _trace_enabled(values: List[Any]) -> bool:
    return len(values) <= TRACE_LIMIT


def _snapshot(values: List[Any], limit: int = 200) -> list:
    """Devuelve una copia del arreglo para la animación (solo arreglos pequeños)."""
    return list(values) if len(values) <= limit else []


def bubble_sort(values: List[Any]) -> dict:
    """Bubble Sort: compara pares adyacentes y burbujea el mayor al final.

    Mejor caso O(n) (lista ya ordenada con bandera de intercambio),
    promedio y peor caso O(n²). Espacio O(1).
    """
    data = list(values)
    n = len(data)
    comparisons = swaps = 0
    steps = []
    trace = _trace_enabled(values)
    for end in range(n - 1, 0, -1):
        swapped = False
        for i in range(end):
            comparisons += 1
            if trace:
                steps.append({"type": "compare", "indices": [i, i + 1],
                              "array": _snapshot(data)})
            if data[i] > data[i + 1]:
                data[i], data[i + 1] = data[i + 1], data[i]
                swaps += 1
                swapped = True
                if trace:
                    steps.append({"type": "swap", "indices": [i, i + 1],
                                  "array": _snapshot(data)})
        if not swapped:
            if trace:
                steps.append({"type": "early_stop", "indices": [],
                              "array": _snapshot(data)})
            break  # Pasa ya ordenado: mejor caso O(n).
    return _result(data, comparisons, swaps, steps)


def selection_sort(values: List[Any]) -> dict:
    """Selection Sort: selecciona el mínimo del resto y lo fija al frente.

    Comparaciones siempre O(n²) en todos los casos; intercambios O(n).
    Espacio O(1).
    """
    data = list(values)
    n = len(data)
    comparisons = swaps = 0
    steps = []
    for start in range(n - 1):
        minimum = start
        for i in range(start + 1, n):
            comparisons += 1
            steps.append({"type": "compare", "indices": [i, minimum],
                          "array": _snapshot(data)})
            if data[i] < data[minimum]:
                minimum = i
        if minimum != start:
            data[start], data[minimum] = data[minimum], data[start]
            swaps += 1
            steps.append({"type": "swap", "indices": [start, minimum],
                          "array": _snapshot(data)})
    return _result(data, comparisons, swaps, steps)


def quick_sort(values: List[Any]) -> dict:
    """Quick Sort con pivote último (esquema Lomuto) y ordenamiento in-place.

    Promedio O(n log n), peor caso O(n²) (datos ya ordenados con pivote fijo),
    espacio O(log n) por pila de recursión.
    """
    data = list(values)
    counters = {"comparisons": 0, "swaps": 0, "recursions": 0, "max_depth": 0}
    steps = []

    def partition(low: int, high: int, depth: int) -> int:
        counters["recursions"] += 1
        counters["max_depth"] = max(counters["max_depth"], depth)
        pivot = data[high]
        steps.append({"type": "pivot", "indices": [high], "pivot": pivot,
                      "array": _snapshot(data)})
        boundary = low
        for i in range(low, high):
            counters["comparisons"] += 1
            steps.append({"type": "compare", "indices": [i, high],
                          "array": _snapshot(data)})
            if data[i] < pivot:
                if i != boundary:
                    data[i], data[boundary] = data[boundary], data[i]
                    counters["swaps"] += 1
                    steps.append({"type": "swap", "indices": [i, boundary],
                                  "array": _snapshot(data)})
                boundary += 1
        if boundary != high:
            data[boundary], data[high] = data[high], data[boundary]
            counters["swaps"] += 1
            steps.append({"type": "swap", "indices": [boundary, high],
                          "array": _snapshot(data)})
        return boundary

    def sort_range(low: int, high: int, depth: int) -> None:
        if low >= high:
            return
        pivot_index = partition(low, high, depth)
        sort_range(low, pivot_index - 1, depth + 1)
        sort_range(pivot_index + 1, high, depth + 1)

    sort_range(0, len(data) - 1, 0)
    return _result(data, counters["comparisons"], counters["swaps"], steps,
                   extra={"recursions": counters["recursions"],
                          "max_recursion_depth": counters["max_depth"]})


def _result(data: list, comparisons: int, swaps: int, steps: list, extra: dict | None = None) -> dict:
    """Empaqueta el resultado estándar de un algoritmo de ordenamiento."""
    result = {
        "sorted": data,
        "comparisons": comparisons,
        "swaps": swaps,
        "steps": steps,
        "is_sorted_check": all(data[i] <= data[i + 1] for i in range(len(data) - 1)),
    }
    if extra:
        result.update(extra)
    return result


ALGORITHMS: dict[str, Callable[[List[Any]], dict]] = {
    "bubble": bubble_sort,
    "selection": selection_sort,
    "quick": quick_sort,
}

# Propiedades académicas de cada algoritmo (para el panel de información).
ALGORITHM_INFO = {
    "bubble": {
        "name": "Bubble Sort",
        "best": "O(n)", "average": "O(n²)", "worst": "O(n²)", "space": "O(1)",
        "stable": True,
        "description": "Compara pares adyacentes y empuja el mayor hacia el final en cada pasada.",
    },
    "selection": {
        "name": "Selection Sort",
        "best": "O(n²)", "average": "O(n²)", "worst": "O(n²)", "space": "O(1)",
        "stable": False,
        "description": "Selecciona el mínimo del segmento no ordenado y lo coloca al frente. "
                       "Siempre realiza n²/2 comparaciones.",
    },
    "quick": {
        "name": "Quick Sort",
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n²)", "space": "O(log n)",
        "stable": False,
        "description": "Divide y vencerás: particiona alrededor de un pivote. "
                       "Con pivote último y datos ordenados degrada a O(n²).",
    },
}
