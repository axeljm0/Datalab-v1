"""Blueprint de optimización: programación dinámica y greedy (Módulos G y H)."""

import time

from flask import Blueprint, jsonify, render_template, request

from algorithms.dynamic_programming import coin_change, fibonacci_dynamic, fibonacci_recursive, knapsack_01
from algorithms.greedy import activity_selection, greedy_coin_change, interval_scheduling, is_coin_system_canonical
from services import run_history

optimization_bp = Blueprint("optimization", __name__)


@optimization_bp.route("/laboratories/dynamic")
def dynamic_lab():
    return render_template("laboratories/dynamic.html")


@optimization_bp.route("/laboratories/greedy")
def greedy_lab():
    return render_template("laboratories/greedy.html")


def _json_payload() -> dict:
    payload = request.get_json(force=True)
    if not isinstance(payload, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON")
    return payload


# ----------------------------------------------------------------------
# Programación dinámica
# ----------------------------------------------------------------------
@optimization_bp.route("/api/dp/fibonacci", methods=["POST"])
def run_fibonacci():
    """Compara Fibonacci recursivo puro vs dinámico para el mismo n."""
    try:
        n = int(_json_payload().get("n"))
        if n < 0:
            raise ValueError("n debe ser no negativo")
        recursive = fibonacci_recursive(n) if n <= 25 else None
        start = time.perf_counter_ns()
        dynamic = fibonacci_dynamic(n)
        elapsed = (time.perf_counter_ns() - start) / 1_000_000
        run_history.record_run("Programación dinámica", "Fibonacci", f"n={n}", elapsed)
        data = {
            "n": n,
            "dynamic": {**dynamic, "time_ms": round(elapsed, 5)},
            "recursive": None,
            "conclusion": ("La tabulación reduce el tiempo de exponencial a lineal: "
                           "cada subproblema se resuelve una vez y se reutiliza."),
        }
        if recursive:
            data["recursive"] = recursive
        else:
            data["conclusion"] += (" El recursivo puro se omite para n > 25: "
                                   "realizaría más de 2^25 llamadas.")
        return jsonify(success=True, data=data)
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


@optimization_bp.route("/api/dp/knapsack", methods=["POST"])
def run_knapsack():
    try:
        payload = _json_payload()
        weights, values = payload.get("weights"), payload.get("values")
        capacity = int(payload.get("capacity"))
        if not isinstance(weights, list) or not isinstance(values, list):
            raise ValueError("Indique pesos y valores como listas")
        if len(weights) > 15:
            raise ValueError("Máximo 15 objetos: la tabla n·W debe caber en pantalla")
        start = time.perf_counter_ns()
        result = knapsack_01([int(w) for w in weights],
                             [int(v) for v in values], capacity)
        elapsed = (time.perf_counter_ns() - start) / 1_000_000
        run_history.record_run("Programación dinámica", "Mochila 0/1",
                               f"n={len(weights)}, W={capacity}", elapsed)
        return jsonify(success=True, data={**result, "time_ms": round(elapsed, 4)})
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


@optimization_bp.route("/api/dp/coin-change", methods=["POST"])
def run_coin_change():
    try:
        payload = _json_payload()
        coins = payload.get("coins")
        amount = int(payload.get("amount"))
        if not isinstance(coins, list) or not coins:
            raise ValueError("Indique las denominaciones como lista")
        if amount > 5_000:
            raise ValueError("Monto máximo: 5000 (la tabla debe ser visualizable)")
        start = time.perf_counter_ns()
        result = coin_change([int(c) for c in coins], amount)
        elapsed = (time.perf_counter_ns() - start) / 1_000_000
        run_history.record_run("Programación dinámica", "Coin Change",
                               f"monto={amount}", elapsed)
        return jsonify(success=True, data={**result, "time_ms": round(elapsed, 4)})
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


# ----------------------------------------------------------------------
# Greedy
# ----------------------------------------------------------------------
@optimization_bp.route("/api/greedy/activities", methods=["POST"])
def run_activities():
    try:
        payload = _json_payload()
        raw = payload.get("activities")
        if not isinstance(raw, list) or not raw:
            raise ValueError("Indique al menos una actividad")
        if len(raw) > 40:
            raise ValueError("Máximo 40 actividades para visualización")
        activities = [{"id": a.get("id", i), "start": int(a["start"]),
                       "end": int(a["end"])} for i, a in enumerate(raw)]
        start = time.perf_counter_ns()
        result = activity_selection(activities)
        elapsed = (time.perf_counter_ns() - start) / 1_000_000
        run_history.record_run("Greedy", "Selección de actividades", "", elapsed)
        return jsonify(success=True, data={**result, "time_ms": round(elapsed, 4)})
    except (ValueError, TypeError, KeyError) as error:
        return jsonify(success=False, error=str(error)), 400


@optimization_bp.route("/api/greedy/coins", methods=["POST"])
def run_greedy_coins():
    try:
        payload = _json_payload()
        denominations = payload.get("denominations")
        amount = int(payload.get("amount"))
        if not isinstance(denominations, list) or not denominations:
            raise ValueError("Indique las denominaciones")
        start = time.perf_counter_ns()
        result = greedy_coin_change([int(d) for d in denominations], amount)
        elapsed = (time.perf_counter_ns() - start) / 1_000_000
        run_history.record_run("Greedy", "Cambio de monedas", f"monto={amount}", elapsed)
        return jsonify(success=True, data={**result, "time_ms": round(elapsed, 4)})
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


@optimization_bp.route("/api/greedy/intervals", methods=["POST"])
def run_intervals():
    try:
        payload = _json_payload()
        raw = payload.get("intervals")
        if not isinstance(raw, list) or not raw:
            raise ValueError("Indique al menos un intervalo")
        intervals = [{"id": a.get("id", i), "start": int(a["start"]),
                      "end": int(a["end"])} for i, a in enumerate(raw)]
        result = interval_scheduling(intervals)
        run_history.record_run("Greedy", "Programación de intervalos", "")
        return jsonify(success=True, data=result)
    except (ValueError, TypeError, KeyError) as error:
        return jsonify(success=False, error=str(error)), 400


@optimization_bp.route("/api/greedy/canonical-check", methods=["POST"])
def run_canonical_check():
    """Verifica si un sistema de monedas es canónico (greedy óptimo)."""
    try:
        payload = _json_payload()
        denominations = payload.get("denominations")
        if not isinstance(denominations, list) or not denominations:
            raise ValueError("Indique las denominaciones")
        result = is_coin_system_canonical([int(d) for d in denominations])
        run_history.record_run("Greedy", "Verificación de canonicidad", "")
        return jsonify(success=True, data=result)
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400
