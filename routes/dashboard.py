"""Blueprint del dashboard: página principal y estadísticas globales."""

from flask import Blueprint, jsonify, render_template

from services import run_history

dashboard_bp = Blueprint("dashboard", __name__)

# Metadatos de los laboratorios (fuente única para sidebar y dashboard).
LABORATORIES = [
    {"slug": "lists", "name": "Listas y Vectores", "module": "B",
     "description": "Arreglos dinámicos, matrices y listas enlazadas"},
    {"slug": "stack-queue", "name": "Pilas y Colas", "module": "C",
     "description": "LIFO y FIFO con ejemplos de aplicación"},
    {"slug": "trees", "name": "Árboles y Grafos", "module": "D",
     "description": "BST, AVL, grafos dirigidos, BFS y DFS"},
    {"slug": "search-sort", "name": "Búsqueda y Ordenamiento", "module": "E",
     "description": "Linear/Binary Search, Bubble/Selection/Quick Sort"},
    {"slug": "hash", "name": "Tablas Hash", "module": "F",
     "description": "Función hash, chaining, factor de carga"},
    {"slug": "dynamic", "name": "Programación Dinámica", "module": "G",
     "description": "Fibonacci, mochila 0/1, coin change"},
    {"slug": "greedy", "name": "Algoritmos Greedy", "module": "H",
     "description": "Actividades, monedas, intervalos"},
    {"slug": "advanced", "name": "Estructuras Avanzadas", "module": "I",
     "description": "Min/Max Heap, AVL, árbol B"},
    {"slug": "data", "name": "Ciencia de Datos", "module": "J",
     "description": "Datasets, filtros, estadísticas"},
    {"slug": "ethics", "name": "Ética y Seguridad", "module": "K",
     "description": "Privacidad, sesgos, transparencia"},
    {"slug": "projects", "name": "Proyectos y Análisis", "module": "L",
     "description": "Benchmarks escalables y conclusiones"},
]


@dashboard_bp.route("/")
def index():
    """Página principal del dashboard."""
    return render_template("dashboard.html", labs=LABORATORIES)


@dashboard_bp.route("/laboratories/ethics")
def ethics():
    """Página educativa de ética y seguridad (Módulo K)."""
    return render_template("laboratories/ethics.html")


@dashboard_bp.route("/api/dashboard/stats")
def stats():
    """Estadísticas agregadas para las tarjetas del dashboard."""
    return jsonify(success=True, data={
        "laboratories": len(LABORATORIES),
        "structures": 11,
        "algorithms": 17,
        "runs_recorded": run_history.run_count(),
        "recent_runs": run_history.recent_runs(8),
        "labs": LABORATORIES,
    })
