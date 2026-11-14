"""Servicio de gestión de datasets para el laboratorio de ciencia de datos.

Los datasets viven en memoria durante la ejecución. Se pueden generar
conjuntos reproducibles (semilla fija), cargar CSV y aplicar operaciones
de filtrado, ordenamiento, transformación, eliminación de duplicados y
estadísticas. El ordenamiento usa el Quick Sort propio del proyecto.
"""

from __future__ import annotations

import csv
import io
import random
import statistics
from typing import Any, List

from algorithms.sorting import quick_sort

_DATASETS: dict[str, dict] = {}
_NEXT_ID = [1]

OPERATORS = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
}

TRANSFORMS = {
    "square": lambda v: v * v,
    "double": lambda v: v * 2,
    "abs": lambda v: abs(v),
    "sqrt": lambda v: v ** 0.5,
    "increment": lambda v: v + 1,
}


# ----------------------------------------------------------------------
# Almacenamiento en memoria
# ----------------------------------------------------------------------
def create_dataset(name: str, columns: List[str], rows: List[List[Any]],
                   source: str = "generated") -> dict:
    """Registra un dataset y devuelve su metadato. Filas = listas de valores."""
    from flask import current_app

    if len(_DATASETS) >= current_app.config.get("MAX_DATASETS", 32) and name not in _DATASETS:
        raise ValueError("Límite de datasets en memoria alcanzado")
    for row in rows:
        if len(row) != len(columns):
            raise ValueError("Todas las filas deben tener el mismo número de columnas")
    _DATASETS[name] = {"name": name, "columns": columns,
                       "rows": [list(row) for row in rows], "source": source}
    return {"name": name, "columns": columns, "count": len(rows), "source": source}


def get_dataset(name: str) -> dict:
    if name not in _DATASETS:
        raise ValueError(f"Dataset '{name}' no existe")
    return _DATASETS[name]


def list_datasets() -> list:
    return [{"name": d["name"], "columns": d["columns"], "count": len(d["rows"]),
             "source": d["source"]} for d in _DATASETS.values()]


def delete_dataset(name: str) -> bool:
    return _DATASETS.pop(name, None) is not None


# ----------------------------------------------------------------------
# Generación y carga
# ----------------------------------------------------------------------
def generate_random_dataset(name: str, count: int, seed: int | None = None) -> dict:
    """Dataset demostrativo reproducible: edad, salario y puntuación.

    Semilla fija por defecto para que la demostración en vivo sea estable.
    """
    if count < 1 or count > 10_000:
        raise ValueError("El tamaño del dataset debe estar entre 1 y 10.000")
    rng = random.Random(seed if seed is not None else 7)
    rows = []
    for i in range(count):
        age = rng.randint(18, 65)
        salary = rng.randint(12_000, 90_000)
        score = round(rng.uniform(0, 100), 2)
        city = rng.choice(["Lima", "Quito", "Bogotá", "Cusco", "Arequipa"])
        rows.append([i, age, salary, score, city])
    return create_dataset(name, ["id", "age", "salary", "score", "city"], rows, "generated")


def parse_csv(content: str, name: str) -> dict:
    """Convierte texto CSV en un dataset; los valores numéricos se tipan."""
    reader = csv.reader(io.StringIO(content))
    try:
        header = next(reader)
    except StopIteration:
        raise ValueError("El archivo CSV está vacío")
    if not header:
        raise ValueError("El CSV no tiene encabezados")
    rows = []
    for raw in reader:
        if not raw:
            continue
        rows.append([_typed(value) for value in raw])
    return create_dataset(name, [h.strip() for h in header], rows, "csv")


def _typed(value: str) -> Any:
    """Tipado ligero: int, float o cadena."""
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


# ----------------------------------------------------------------------
# Operaciones sobre columnas
# ----------------------------------------------------------------------
def filter_rows(name: str, column: str, operator: str, value: str) -> dict:
    """Filtra filas por condición columna-operador-valor. O(n)."""
    dataset = get_dataset(name)
    if column not in dataset["columns"]:
        raise ValueError(f"Columna '{column}' no existe")
    if operator not in OPERATORS:
        raise ValueError(f"Operador no soportado: {operator}")
    column_index = dataset["columns"].index(column)
    typed_value = _typed(str(value))
    predicate = OPERATORS[operator]
    kept = []
    comparisons = 0
    for row in dataset["rows"]:
        comparisons += 1
        try:
            if predicate(row[column_index], typed_value):
                kept.append(list(row))
        except TypeError:
            continue  # Tipos incomparables: la fila no pasa el filtro.
    return {"rows": kept, "kept": len(kept), "total": len(dataset["rows"]),
            "comparisons": comparisons}


def sort_rows(name: str, column: str, ascending: bool = True) -> dict:
    """Ordena filas por columna usando el Quick Sort propio. O(n log n)."""
    dataset = get_dataset(name)
    if column not in dataset["columns"]:
        raise ValueError(f"Columna '{column}' no existe")
    column_index = dataset["columns"].index(column)
    # Claves comparables con índice de desempate estable.
    keys = [row[column_index] for row in dataset["rows"]]
    order = list(range(len(dataset["rows"])))
    result = quick_sort([(key, i) for i, key in zip(order, keys)])
    permutation = [index for _, index in result["sorted"]]
    if not ascending:
        permutation.reverse()
    sorted_rows = [list(dataset["rows"][i]) for i in permutation]
    return {"rows": sorted_rows, "comparisons": result["comparisons"],
            "swaps": result["swaps"]}


def transform_column(name: str, column: str, transform: str) -> dict:
    """Aplica una transformación a una columna numérica. O(n)."""
    dataset = get_dataset(name)
    if column not in dataset["columns"]:
        raise ValueError(f"Columna '{column}' no existe")
    if transform not in TRANSFORMS:
        raise ValueError(f"Transformación no soportada: {transform}")
    column_index = dataset["columns"].index(column)
    rows = [list(row) for row in dataset["rows"]]
    changed = 0
    for row in rows:
        original = row[column_index]
        if isinstance(original, (int, float)):
            row[column_index] = TRANSFORMS[transform](original)
            changed += 1
    return {"rows": rows, "transformed": changed}


def remove_duplicates(name: str) -> dict:
    """Elimina filas duplicadas conservando la primera aparición. O(n·k)."""
    dataset = get_dataset(name)
    seen, unique = set(), []
    for row in dataset["rows"]:
        key = tuple(row)
        if key not in seen:
            seen.add(key)
            unique.append(list(row))
    removed = len(dataset["rows"]) - len(unique)
    dataset["rows"] = unique
    return {"removed": removed, "remaining": len(unique)}


def basic_stats(name: str, column: str | None = None) -> dict:
    """Estadísticas descriptivas calculadas manualmente (sin numpy)."""
    dataset = get_dataset(name)
    columns = [column] if column else dataset["columns"]
    report = {}
    for col in columns:
        if col not in dataset["columns"]:
            raise ValueError(f"Columna '{col}' no existe")
        values = [row[dataset["columns"].index(col)] for row in dataset["rows"]]
        numeric = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
        info: dict = {"type": "numeric" if numeric else "categorical",
                      "count": len(values)}
        if numeric:
            info.update({
                "min": min(numeric), "max": max(numeric),
                "mean": round(statistics.fmean(numeric), 4),
                "median": round(statistics.median(numeric), 4),
                "std_dev": round(statistics.pstdev(numeric), 4) if len(numeric) > 1 else 0.0,
            })
        else:
            counts: dict = {}
            for value in values:
                counts[str(value)] = counts.get(str(value), 0) + 1
            info["frequencies"] = counts
        report[col] = info
    return {"stats": report}
