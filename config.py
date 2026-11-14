"""Configuración central de DataLab."""

import os


class BaseConfig:
    """Parámetros base de la aplicación."""

    SECRET_KEY = os.environ.get("DATALAB_SECRET_KEY", "datalab-dev-key")
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False

    # Tamaño máximo de arreglo que se visualiza paso a paso en el cliente.
    MAX_TRACE_LENGTH = 3000
    # Límite de elementos aceptados en una solicitud de búsqueda/ordenamiento.
    MAX_INPUT_ELEMENTS = 200_000
    # Número máximo de estructuras simultáneas en memoria.
    MAX_STRUCTURES = 64
    # Número máximo de datasets en memoria.
    MAX_DATASETS = 32
    # Historial de ejecuciones conservado para el dashboard.
    MAX_RUN_HISTORY = 50


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "default": BaseConfig,
}


def resolve_config(name: str | None = None):
    """Devuelve la clase de configuración solicitada."""
    return CONFIG_BY_NAME.get(name or os.environ.get("DATALAB_CONFIG", "default"), BaseConfig)
