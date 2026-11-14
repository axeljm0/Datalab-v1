"""Algoritmos de búsqueda implementados desde cero.

Cada algoritmo devuelve el resultado, los contadores de operaciones y una
traza de pasos que permite reproducir su ejecución en el frontend.
"""

from __future__ import annotations

from typing import Any, List, Optional


def is_sorted(values: List[Any]) -> bool:
    """Verifica si la lista está ordenada de forma ascendente. O(n)."""
    for i in range(len(values) - 1):
        if values[i] > values[i + 1]:
            return False
    return True


def linear_search(values: List[Any], target: Any) -> dict:
    """Búsqueda lineal: compara cada elemento de izquierda a derecha.

    Mejor caso O(1) (primera posición), promedio O(n), peor caso O(n).

    Returns:
        dict con found, index, comparisons y steps de la traza.
    """
    steps, comparisons = [], 0
    result_index: Optional[int] = None
    for index in range(len(values)):
        comparisons += 1
        match = values[index] == target
        steps.append({"index": index, "value": values[index],
                      "comparison": comparisons, "match": match})
        if match:
            result_index = index
            break
    found = result_index is not None
    return {
        "found": found,
        "index": result_index if found else -1,
        "comparisons": comparisons,
        "steps": steps,
    }


def binary_search(values: List[Any], target: Any) -> dict:
    """Búsqueda binaria sobre una lista ASCENDENTE.

    Comportamiento académico requerido: si los datos no están ordenados,
    el algoritmo se niega a ejecutarse e informa el estado, de modo que
    quede claro que binary search exige el precondición de orden. La
    verificación (O(n)) se reporta aparte como tiempo de "preparación".

    Mejor caso O(1), promedio/peor caso O(log n).

    Raises:
        ValueError si la lista no está ordenada.
    """
    if not is_sorted(values):
        raise ValueError(
            "Binary Search requiere datos ordenados: la lista contiene desorden"
        )
    steps, comparisons = [], 0
    low, high = 0, len(values) - 1
    result_index: Optional[int] = None
    while low <= high:
        middle = low + (high - low) // 2  # Evita desbordes en otros lenguajes.
        comparisons += 1
        match = values[middle] == target
        steps.append({"low": low, "high": high, "middle": middle,
                      "value": values[middle], "comparison": comparisons,
                      "match": match})
        if match:
            result_index = middle
            break
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    found = result_index is not None
    return {
        "found": found,
        "index": result_index if found else -1,
        "comparisons": comparisons,
        "steps": steps,
    }


def search_many(values: List[Any], target: Any, occurrences: bool = False) -> dict:
    """Búsqueda lineal que reporta todas las coincidencias (uso del dataset lab)."""
    indices = [i for i, v in enumerate(values) if v == target]
    return {"found": bool(indices), "indices": indices, "comparisons": len(values)}
