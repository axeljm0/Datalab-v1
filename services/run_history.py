"""Registro en memoria de las últimas ejecuciones (dashboard)."""

import threading
import time

from flask import current_app

_LOCK = threading.Lock()
_RUNS = []


def record_run(module: str, operation: str, details: str = "", elapsed_ms: float | None = None) -> None:
    """Guarda una entrada de ejecución para el dashboard. Hilo-seguro."""
    max_history = current_app.config.get("MAX_RUN_HISTORY", 50)
    entry = {
        "module": module,
        "operation": operation,
        "details": details,
        "elapsed_ms": round(elapsed_ms, 3) if elapsed_ms is not None else None,
        "timestamp": time.time(),
    }
    with _LOCK:
        _RUNS.append(entry)
        del _RUNS[:-max_history]


def recent_runs(limit: int = 10) -> list:
    """Devuelve las últimas ejecuciones, más recientes primero."""
    with _LOCK:
        runs = list(reversed(_RUNS[-limit:]))
    return runs


def run_count() -> int:
    with _LOCK:
        return len(_RUNS)
