"""DataLab — Laboratorio interactivo de estructuras de datos y algoritmos.

Punto de entrada de la aplicación Flask. Crea la app mediante una factory,
registra los blueprints de rutas y maneja errores consistentes en JSON.
"""

import logging

from flask import Flask, jsonify

from config import resolve_config


def create_app(config_name: str | None = None) -> Flask:
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(resolve_config(config_name))

    logging.basicConfig(level=logging.INFO)
    _register_blueprints(app)
    _register_error_handlers(app)
    return app


def _register_blueprints(app: Flask) -> None:
    """Registra todos los blueprints de la aplicación."""
    from routes.dashboard import dashboard_bp
    from routes.searching import searching_bp
    from routes.sorting import sorting_bp
    from routes.structures import structures_bp
    from routes.optimization import optimization_bp
    from routes.benchmarks import benchmarks_bp
    from routes.datasets import datasets_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(searching_bp)
    app.register_blueprint(sorting_bp)
    app.register_blueprint(structures_bp)
    app.register_blueprint(optimization_bp)
    app.register_blueprint(benchmarks_bp)
    app.register_blueprint(datasets_bp)


def _register_error_handlers(app: Flask) -> None:
    """Convierte los errores HTTP en respuestas JSON consistentes."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(success=False, error=str(error.description)), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(success=False, error="Recurso no encontrado"), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify(success=False, error="Método no permitido"), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify(success=False, error="Error interno del servidor"), 500


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
