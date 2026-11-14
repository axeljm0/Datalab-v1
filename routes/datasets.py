"""Blueprint del laboratorio de ciencia de datos (Módulo J)."""

from flask import Blueprint, jsonify, render_template, request

from services import dataset_service, run_history

datasets_bp = Blueprint("datasets", __name__)


@datasets_bp.route("/laboratories/data")
def data_lab():
    return render_template("laboratories/data.html")


@datasets_bp.route("/api/datasets", methods=["GET"])
def list_all():
    return jsonify(success=True, data=dataset_service.list_datasets())


@datasets_bp.route("/api/datasets/generate", methods=["POST"])
def generate():
    """Genera un dataset demostrativo reproducible."""
    try:
        payload = request.get_json(force=True) or {}
        name = str(payload.get("name", "")).strip()
        count = int(payload.get("count", 100))
        seed = payload.get("seed")
        seed = int(seed) if seed is not None else None
        if not name:
            raise ValueError("Indique un nombre para el dataset")
        meta = dataset_service.generate_random_dataset(name, count, seed)
        run_history.record_run("Ciencia de datos", "Generar dataset", name)
        return jsonify(success=True, data=meta)
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


@datasets_bp.route("/api/datasets/upload", methods=["POST"])
def upload_csv():
    """Carga un CSV pegado en texto o enviado como archivo."""
    try:
        name = request.form.get("name", "").strip() or "csv-upload"
        content = request.form.get("content", "")
        if not content and "file" in request.files:
            file = request.files["file"]
            name = name if name != "csv-upload" else (file.filename or "csv-upload")
            content = file.read().decode("utf-8", errors="replace")
        if not content:
            raise ValueError("No se recibió contenido CSV")
        meta = dataset_service.parse_csv(content, name)
        run_history.record_run("Ciencia de datos", "Cargar CSV", name)
        return jsonify(success=True, data=meta)
    except (ValueError, UnicodeDecodeError) as error:
        return jsonify(success=False, error=str(error)), 400


@datasets_bp.route("/api/datasets/<name>", methods=["GET"])
def preview(name: str):
    """Devuelve columnas y las primeras filas del dataset."""
    try:
        dataset = dataset_service.get_dataset(name)
        return jsonify(success=True, data={
            "name": name, "columns": dataset["columns"],
            "rows": dataset["rows"][:50], "total": len(dataset["rows"]),
        })
    except ValueError as error:
        return jsonify(success=False, error=str(error)), 404


@datasets_bp.route("/api/datasets/<name>", methods=["DELETE"])
def delete(name: str):
    deleted = dataset_service.delete_dataset(name)
    if not deleted:
        return jsonify(success=False, error="Dataset no encontrado"), 404
    return jsonify(success=True)


@datasets_bp.route("/api/datasets/<name>/filter", methods=["POST"])
def filter_rows(name: str):
    try:
        payload = request.get_json(force=True) or {}
        result = dataset_service.filter_rows(name, payload["column"],
                                             payload["operator"], payload["value"])
        run_history.record_run("Ciencia de datos", "Filtrar", name)
        return jsonify(success=True, data=result)
    except (ValueError, KeyError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


@datasets_bp.route("/api/datasets/<name>/sort", methods=["POST"])
def sort_rows(name: str):
    try:
        payload = request.get_json(force=True) or {}
        result = dataset_service.sort_rows(name, payload["column"],
                                           bool(payload.get("ascending", True)))
        run_history.record_run("Ciencia de datos", "Ordenar", name)
        return jsonify(success=True, data=result)
    except (ValueError, KeyError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


@datasets_bp.route("/api/datasets/<name>/transform", methods=["POST"])
def transform(name: str):
    try:
        payload = request.get_json(force=True) or {}
        result = dataset_service.transform_column(name, payload["column"],
                                                  payload["transform"])
        run_history.record_run("Ciencia de datos", "Transformar", name)
        return jsonify(success=True, data=result)
    except (ValueError, KeyError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


@datasets_bp.route("/api/datasets/<name>/dedupe", methods=["POST"])
def dedupe(name: str):
    try:
        result = dataset_service.remove_duplicates(name)
        run_history.record_run("Ciencia de datos", "Eliminar duplicados", name)
        return jsonify(success=True, data=result)
    except ValueError as error:
        return jsonify(success=False, error=str(error)), 400


@datasets_bp.route("/api/datasets/<name>/stats", methods=["GET"])
def stats(name: str):
    try:
        column = request.args.get("column")
        result = dataset_service.basic_stats(name, column)
        run_history.record_run("Ciencia de datos", "Estadísticas", name)
        return jsonify(success=True, data=result)
    except ValueError as error:
        return jsonify(success=False, error=str(error)), 400
