"""Blueprint de benchmarks: experimentos escalables (Módulo L)."""

from flask import Blueprint, jsonify, render_template, request

from services import benchmark_service, run_history

benchmarks_bp = Blueprint("benchmarks", __name__)


@benchmarks_bp.route("/laboratories/projects")
def projects_lab():
    return render_template("laboratories/projects.html")


@benchmarks_bp.route("/api/benchmarks/sort", methods=["POST"])
def sort_benchmark():
    """Ejecuta el experimento de ordenamiento por tamaños seleccionados."""
    try:
        payload = request.get_json(force=True) or {}
        algorithms = payload.get("algorithms", ["bubble", "selection", "quick"])
        sizes = [int(s) for s in payload.get("sizes", benchmark_service.EXPERIMENT_SIZES)]
        if not algorithms or any(a not in ("bubble", "selection", "quick") for a in algorithms):
            raise ValueError("Algoritmos válidos: bubble, selection, quick")
        if not sizes or any(s < 1 for s in sizes):
            raise ValueError("Los tamaños deben ser positivos")
        result = benchmark_service.run_sort_benchmark(algorithms, sizes)
        viable_count = sum(1 for r in result["results"] if r.get("viable"))
        run_history.record_run("Benchmark", "Ordenamiento",
                               f"{viable_count} ejecuciones viables")
        return jsonify(success=True, data=result)
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


@benchmarks_bp.route("/api/benchmarks/search", methods=["POST"])
def search_benchmark():
    """Compara linear vs binary con separación de tiempos de preparación."""
    try:
        payload = request.get_json(force=True) or {}
        sizes = [int(s) for s in payload.get("sizes", benchmark_service.EXPERIMENT_SIZES)]
        if not sizes or any(s < 1 for s in sizes):
            raise ValueError("Los tamaños deben ser positivos")
        result = benchmark_service.run_search_benchmark(sizes)
        run_history.record_run("Benchmark", "Búsqueda", f"{len(sizes)} tamaños")
        return jsonify(success=True, data=result)
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400
