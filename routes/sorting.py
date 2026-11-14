"""Blueprint de ordenamiento: laboratorio, ejecución individual y comparación."""

import time

from flask import Blueprint, jsonify, render_template, request

from algorithms.sorting import ALGORITHMS, ALGORITHM_INFO
from services import run_history
from routes.dashboard import LABORATORIES

sorting_bp = Blueprint("sorting", __name__)

MAX_ELEMENTS = 20_000        # Límite por ejecución individual.
MAX_ELEMENTS_FOR_TRACE = 300  # Solo se devuelve traza paso a paso hasta aquí.
MAX_COMPARE_ALGORITHMS = 3


@sorting_bp.route("/api/sort/<algorithm>", methods=["POST"])
def run_sort(algorithm: str):
    """Ejecuta un algoritmo de ordenamiento y devuelve métricas + pasos."""
    if algorithm not in ALGORITHMS:
        return jsonify(success=False, error=f"Algoritmo desconocido: {algorithm}"), 404
    try:
        payload = request.get_json(force=True)
        values = payload.get("values")
        if not isinstance(values, list) or not values:
            raise ValueError("El campo 'values' debe ser una lista no vacía")
        if len(values) > MAX_ELEMENTS:
            raise ValueError(f"Límite de {MAX_ELEMENTS} elementos por ejecución")
        start = time.perf_counter_ns()
        result = ALGORITHMS[algorithm](values)
        elapsed = (time.perf_counter_ns() - start) / 1_000_000
        steps = result["steps"] if len(values) <= MAX_ELEMENTS_FOR_TRACE else []
        run_history.record_run("Ordenamiento", ALGORITHM_INFO[algorithm]["name"],
                               f"n={len(values)}", elapsed)
        return jsonify(success=True, data={
            "algorithm": algorithm,
            "info": ALGORITHM_INFO[algorithm],
            "sorted": result["sorted"],
            "comparisons": result["comparisons"],
            "swaps": result["swaps"],
            "steps": steps,
            "time_ms": round(elapsed, 4),
            "trace_available": bool(steps),
        })
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


@sorting_bp.route("/api/sort/compare", methods=["POST"])
def compare_sorts():
    """Ejecuta varios algoritmos sobre el mismo conjunto y los compara."""
    try:
        payload = request.get_json(force=True)
        values = payload.get("values")
        algorithms = payload.get("algorithms", list(ALGORITHMS))
        if not isinstance(values, list) or not values:
            raise ValueError("El campo 'values' debe ser una lista no vacía")
        if len(values) > MAX_ELEMENTS:
            raise ValueError(f"Límite de {MAX_ELEMENTS} elementos por comparación")
        if not isinstance(algorithms, list) or not algorithms:
            raise ValueError("Indique al menos un algoritmo")
        if len(algorithms) > MAX_COMPARE_ALGORITHMS:
            raise ValueError(f"Máximo {MAX_COMPARE_ALGORITHMS} algoritmos por comparación")
        for name in algorithms:
            if name not in ALGORITHMS:
                raise ValueError(f"Algoritmo desconocido: {name}")
        results = []
        for name in algorithms:
            start = time.perf_counter_ns()
            result = ALGORITHMS[name](values)
            elapsed = (time.perf_counter_ns() - start) / 1_000_000
            run_history.record_run("Comparación", ALGORITHM_INFO[name]["name"],
                                   f"n={len(values)}", elapsed)
            results.append({
                "algorithm": name,
                "info": ALGORITHM_INFO[name],
                "comparisons": result["comparisons"],
                "swaps": result["swaps"],
                "time_ms": round(elapsed, 4),
                "correct": result["is_sorted_check"],
            })
        return jsonify(success=True, data={"size": len(values), "results": results})
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400
