"""Blueprint de búsqueda: páginas del laboratorio y endpoints REST."""

import time

from flask import Blueprint, jsonify, render_template, request

from algorithms.searching import binary_search, linear_search
from services import run_history

searching_bp = Blueprint("searching", __name__)


def _validate_payload(payload: dict) -> tuple[list, int]:
    """Valida y extrae la lista de datos y el objetivo de la solicitud."""
    values = payload.get("values")
    target = payload.get("target")
    if not isinstance(values, list) or not values:
        raise ValueError("El campo 'values' debe ser una lista no vacía")
    if len(values) > 200_000:
        raise ValueError("La lista excede el límite de 200.000 elementos")
    if target is None:
        raise ValueError("El campo 'target' es obligatorio")
    return values, target


@searching_bp.route("/laboratories/search-sort")
def laboratory():
    """Página del laboratorio de búsqueda y ordenamiento (Módulo E)."""
    return render_template("laboratories/search_sort.html")


@searching_bp.route("/api/search/linear", methods=["POST"])
def run_linear():
    """Búsqueda lineal sobre la lista recibida."""
    try:
        payload = request.get_json(force=True)
        values, target = _validate_payload(payload)
        start = time.perf_counter_ns()
        result = linear_search(values, target)
        elapsed = (time.perf_counter_ns() - start) / 1_000_000
        run_history.record_run("Búsqueda", "Linear Search",
                               f"objetivo={target}, n={len(values)}", elapsed)
        return jsonify(success=True, data={
            "found": result["found"], "index": result["index"],
            "comparisons": result["comparisons"], "steps": result["steps"],
            "time_ms": round(elapsed, 4),
            "complexity": {"best": "O(1)", "average": "O(n)", "worst": "O(n)",
                           "space": "O(1)"},
        })
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


@searching_bp.route("/api/search/binary", methods=["POST"])
def run_binary():
    """Búsqueda binaria. Exige lista ordenada (precondición verificada)."""
    try:
        payload = request.get_json(force=True)
        values, target = _validate_payload(payload)
        # Fase de preparación: si los datos no están ordenados se rechaza.
        start = time.perf_counter_ns()
        result = binary_search(values, target)
        elapsed = (time.perf_counter_ns() - start) / 1_000_000
        run_history.record_run("Búsqueda", "Binary Search",
                               f"objetivo={target}, n={len(values)}", elapsed)
        return jsonify(success=True, data={
            "found": result["found"], "index": result["index"],
            "comparisons": result["comparisons"], "steps": result["steps"],
            "search_time_ms": round(elapsed, 5),
            "prep_note": "Los datos llegaron ordenados: no se requirió preparación.",
            "complexity": {"best": "O(1)", "average": "O(log n)", "worst": "O(log n)",
                           "space": "O(1)"},
        })
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error), data={
            "requires_sorted": True,
            "prep_hint": "Ordene la lista (O(n log n)) antes de buscar; ese tiempo "
                         "de preparación es distinto del tiempo de búsqueda."
        }), 400
