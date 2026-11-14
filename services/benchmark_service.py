"""Servicio de benchmarks experimentales reproducibles.

Mide tiempos reales con time.perf_counter_ns (no hay datos inventados).
Cada tamaño se ejecuta con la misma semilla de datos aleatorios para que
los experimentos sean reproducibles entre corridas.

Regla de viabilidad: los algoritmos O(n²) se omiten en tamaños donde el
tiempo esperado sería de minutos, en lugar de bloquear el servidor.
"""

from __future__ import annotations

import random
import time
from typing import Callable, List

from algorithms.searching import binary_search, linear_search
from algorithms.sorting import ALGORITHMS

# Tamaños de experimento estándar del laboratorio de proyectos.
EXPERIMENT_SIZES = [100, 1_000, 10_000, 100_000]

# Límite de tamaño viable por complejidad (umbrales conservadores en Python).
SIZE_CAPS = {
    "bubble": 20_000,      # O(n²): ~10^8 operaciones al límite.
    "selection": 20_000,   # O(n²).
    "quick": 100_000,      # O(n log n).
}
BENCHMARK_SEED = 42  # Semilla fija: experimentos reproducibles.


def generate_dataset(size: int, seed: int = BENCHMARK_SEED) -> List[int]:
    """Conjunto aleatorio determinista para todos los benchmarks."""
    rng = random.Random(seed)
    return [rng.randint(0, size * 10) for _ in range(size)]


def _time_ms(function: Callable[[], object]) -> float:
    """Mide el tiempo de ejecución de una función en milisegundos."""
    start = time.perf_counter_ns()
    function()
    return (time.perf_counter_ns() - start) / 1_000_000


def run_sort_benchmark(algorithms: List[str], sizes: List[int]) -> dict:
    """Ejecuta benchmarks de ordenamiento por tamaño y algoritmo.

    Returns:
        {"results": [{"algorithm", "size", "time_ms", "comparisons", "swaps",
                      "viable", "skipped_reason"}], "notes": [...]}
    """
    results = []
    notes = []
    for size in sizes:
        if size > 100_000:
            raise ValueError("El tamaño máximo admitido es 100.000 elementos")
        dataset = generate_dataset(size)
        for name in algorithms:
            if name not in ALGORITHMS:
                raise ValueError(f"Algoritmo desconocido: {name}")
            cap = SIZE_CAPS[name]
            if size > cap:
                results.append({"algorithm": name, "size": size, "viable": False,
                                "skipped_reason": f"O(n²) no viable en {size:,} elementos (límite {cap:,})"})
                continue
            sorter = ALGORITHMS[name]
            data = list(dataset)
            result = {}
            elapsed = _time_ms(lambda: result.update(sorter(data)))
            results.append({
                "algorithm": name,
                "size": size,
                "viable": True,
                "time_ms": round(elapsed, 3),
                "comparisons": result["comparisons"],
                "swaps": result["swaps"],
                **({"recursions": result["recursions"]} if "recursions" in result else {}),
            })
    notes.append("Los tiempos dependen del hardware, pero la tasa de crecimiento es reproducible.")
    notes.append(f"Semilla de datos: {BENCHMARK_SEED} (mismo conjunto en cada corrida).")
    notes.append("Los O(n²) se omiten a partir de 100.000 elementos: el tiempo esperado es de minutos.")
    return {"results": results, "notes": notes}


def run_search_benchmark(sizes: List[int]) -> dict:
    """Compara búsqueda lineal vs binaria, separando preparación y búsqueda.

    Para binary search se mide por separado: (1) el ordenamiento previo de
    los datos (preparación O(n log n)) y (2) la búsqueda propia O(log n).
    """
    results = []
    for size in sizes:
        if size > 100_000:
            raise ValueError("El tamaño máximo admitido es 100.000 elementos")
        dataset = generate_dataset(size)
        target = dataset[-1]  # Peor caso para linear (última posición).
        linear_result = linear_search(dataset, target)
        linear_time = _time_ms(lambda: linear_search(dataset, target))

        unsorted = list(dataset)
        prep_time = _time_ms(lambda: _quick_for_benchmark(unsorted))
        sorted_data = _quick_for_benchmark(list(dataset))
        binary_result = binary_search(sorted_data, target)
        binary_time = _time_ms(lambda: binary_search(sorted_data, target))
        results.append({
            "size": size,
            "linear": {"time_ms": round(linear_time, 4),
                       "comparisons": linear_result["comparisons"]},
            "binary": {"prep_time_ms": round(prep_time, 4),  # Ordenar = preparación.
                       "search_time_ms": round(binary_time, 5),
                       "comparisons": binary_result["comparisons"]},
        })
    notes = [
        "El tiempo de binary search se reporta en dos fases: preparación (ordenar los datos) y búsqueda propia.",
        "La preparación solo se paga una vez; después cada búsqueda es O(log n).",
    ]
    return {"results": results, "notes": notes}


def _quick_for_benchmark(values: List[int]) -> List[int]:
    """Ordena usando el Quick Sort propio del proyecto (sin sort nativo)."""
    return ALGORITHMS["quick"](values)["sorted"]
