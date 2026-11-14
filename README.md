# DataLab — Laboratorio interactivo de estructuras de datos y algoritmos

Proyecto integrador del Módulo 12. Aplicación web Flask que expone, mediante una API REST,
estructuras de datos y algoritmos **implementados desde cero en Python** y los visualiza de
forma interactiva en un frontend ligero (HTML + CSS + JS vanilla + Chart.js). Nada está
simulado: el frontend solo dibuja los resultados reales que produce el backend.

---

## Características

- 11 laboratorios interactivos organizados por módulos (B–L).
- 11 estructuras de datos implementadas desde cero con trazas paso a paso.
- 17 algoritmos (búsqueda, ordenamiento, programación dinámica, greedy) con análisis Big O.
- Reproductor de animaciones (ejecutar / pausar / paso a paso / velocidad).
- Benchmarks medidos en vivo con gráficas Chart.js (escala lineal y logarítmica).
- Laboratorio de ciencia de datos: generación, carga, filtrado, ordenamiento y estadísticas.
- Historial de ejecuciones para el dashboard.
- Respuestas de error consistentes en JSON y suite de tests (113 tests).

---

## Requisitos

- Python 3.12+ (usa la sintaxis `str | None` de tipos unión)
- pip

## Instalación

```bash
cd datalab

# (opcional) entorno virtual
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Ejecución

```bash
python3 app.py
```

Abre `http://127.0.0.1:5000` en el navegador. Los estilos y scripts se cargan a través de
`/static/...`, por lo que **es necesario servir la app con Flask**: abrir los HTML
directamente (`file://`) no resolverá los recursos.

## Tests

```bash
python3 -m pytest -q
```

---

## Arquitectura

```
datalab/
├── app.py                     # Factory de Flask, blueprints y manejo de errores JSON
├── config.py                  # Configuración por entorno (default / development / testing)
├── requirements.txt
├── data_structures/           # Estructuras implementadas desde cero
│   ├── arrays.py              # Arreglo dinámico y matriz
│   ├── linked_list.py         # Lista enlazada simple
│   ├── doubly_linked_list.py  # Lista doblemente enlazada
│   ├── stack.py  queue.py     # LIFO / FIFO
│   ├── binary_tree.py         # BST
│   ├── avl_tree.py            # Árbol AVL con balance
│   ├── b_tree.py              # Árbol B
│   ├── graph.py               # Grafo dirigido/no dirigido, BFS y DFS
│   ├── hash_table.py          # Tabla hash con chaining
│   └── heap.py                # Min/Max heap
├── algorithms/
│   ├── searching.py           # Linear y Binary search
│   ├── sorting.py             # Bubble, Selection, Insertion, Merge, Quick
│   ├── dynamic_programming.py # Fibonacci, mochila 0/1, coin change
│   └── greedy.py              # Actividades, monedas, intervalos
├── services/                  # Lógica de aplicación sin HTTP
│   ├── run_history.py         # Historial de ejecuciones del dashboard
│   ├── benchmark_service.py   # Benchmarks de ordenamiento y búsqueda
│   └── dataset_service.py     # Datasets en memoria: filtros y estadísticas
├── routes/                    # Blueprints: una capa fina sobre los servicios
│   ├── dashboard.py  structures.py  searching.py
│   ├── sorting.py    optimization.py
│   ├── benchmarks.py datasets.py
├── templates/                 # Jinja2 (base + un HTML por laboratorio)
├── static/
│   ├── css/style.css          # Tema oscuro completo
│   ├── js/core.js             # API wrapper, reproductor, SVG de árboles/grafos
│   ├── js/labs.js             # Inicialización de cada laboratorio (por data-page)
│   └── assets/chart.umd.min.js
└── tests/                     # pytest: estructuras, optimización y API
```

Flujo: el navegador llama a `/api/...` → la ruta valida y delega en el servicio o en la
estructura → se devuelve `{success, data}` o `{success: false, error}` con el código HTTP
adecuado (400/404/405/500 manejados globalmente en `app.py`).

---

## Laboratorios

| Módulo | Ruta | Contenido |
|--------|------|-----------|
| B | `/laboratories/lists` | Arreglo dinámico, matriz, listas simple/doble |
| C | `/laboratories/stack-queue` | Pilas y colas con casos de aplicación |
| D | `/laboratories/trees` | BST, AVL, grafos, BFS/DFS con SVG |
| E | `/laboratories/search-sort` | Linear/Binary search, ordenamientos animados |
| F | `/laboratories/hash` | Función hash, chaining, factor de carga |
| G | `/laboratories/dynamic` | Fibonacci, mochila 0/1, coin change |
| H | `/laboratories/greedy` | Actividades, monedas, intervalos |
| I | `/laboratories/advanced` | Min/Max Heap, AVL, árbol B |
| J | `/laboratories/data` | Datasets: generar/cargar, filtrar, ordenar, estadísticas |
| K | `/laboratories/ethics` | Ética y seguridad en el manejo de datos |
| L | `/laboratories/projects` | Benchmarks escalables y análisis experimental |

---

## API REST

Respuesta estándar: `{"success": true, "data": ...}` o `{"success": false, "error": "..."}`.

### Dashboard
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/dashboard/stats` | Estadísticas agregadas y últimas ejecuciones |

### Estructuras de datos
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/structures` | Crea una estructura (`type`: array, matrix, singly_list, doubly_list, stack, queue, binary_tree, avl, graph, hash_table, b_tree, min_heap, max_heap) |
| GET | `/api/structures/<id>` | Snapshot actual |
| DELETE | `/api/structures/<id>` | Elimina la instancia |
| POST | `/api/structures/<id>/op` | Ejecuta una operación (append, insert_at, delete_at, insert_head, insert_tail, set, update, delete, search, traverse, transpose, push, pop, enqueue, dequeue, add_vertex, add_edge, bfs, dfs, put, remove, insert, …) |

### Búsqueda y ordenamiento
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/search/linear` | Búsqueda lineal con comparaciones y pasos |
| POST | `/api/search/binary` | Búsqueda binaria (devuelve pasos y comparaciones) |
| POST | `/api/sort/<algorithm>` | Ordena con `bubble \| selection \| insertion \| merge \| quick` y traza de pasos |
| POST | `/api/sort/compare` | Compara algoritmos sobre la misma entrada |

### Programación dinámica y greedy
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/dp/fibonacci` | Fibonacci iterativo vs. memoización vs. recursivo |
| POST | `/api/dp/knapsack` | Mochila 0/1 con tabla de DP |
| POST | `/api/dp/coin-change` | Coin change mínimo |
| POST | `/api/greedy/activities` | Selección de actividades |
| POST | `/api/greedy/coins` | Cambio greedy (+ verificación contra óptimo) |
| POST | `/api/greedy/intervals` | Cobertura de intervalos |
| POST | `/api/greedy/canonical-check` | ¿Sistema de monedas canónico? |

### Benchmarks
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/benchmarks/sort` | Tiempos y comparaciones por tamaño de entrada |
| POST | `/api/benchmarks/search` | Linear vs. binary por tamaño (escala log) |

### Datasets (ciencia de datos)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/datasets` | Lista los datasets en memoria |
| POST | `/api/datasets/generate` | Genera datos sintéticos |
| POST | `/api/datasets/upload` | Carga filas desde el cliente |
| GET/DELETE | `/api/datasets/<name>` | Obtiene / elimina un dataset |
| POST | `/api/datasets/<name>/filter` | Filtra por condición |
| POST | `/api/datasets/<name>/sort` | Ordena por columna |
| POST | `/api/datasets/<name>/transform` | Transforma una columna |
| POST | `/api/datasets/<name>/dedupe` | Elimina duplicados |
| GET | `/api/datasets/<name>/stats` | Media, mediana, moda, desviación, etc. |

### Ejemplo

```bash
# Crear una pila
curl -X POST http://127.0.0.1:5000/api/structures \
  -H "Content-Type: application/json" -d '{"type": "stack"}'
# -> {"success": true, "data": {"id": "ab12cd34", ...}}

# Apilar dos valores
curl -X POST http://127.0.0.1:5000/api/structures/ab12cd34/op \
  -H "Content-Type: application/json" -d '{"op": "push", "value": 7}'

# Ordenar con QuickSort y ver la traza
curl -X POST http://127.0.0.1:5000/api/sort/quick \
  -H "Content-Type: application/json" -d '{"values": [5, 2, 9, 1]}'
```

---

## Configuración y variables de entorno

La configuración se selecciona con `DATALAB_CONFIG` (`default` | `development` | `testing`)
en `config.py`. Todas las variables son opcionales:

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `DATALAB_CONFIG` | `default` | Perfil de configuración |
| `DATALAB_SECRET_KEY` | `datalab-dev-key` | Clave de Flask. **Define siempre una propia en despliegue** |

Límites internos ajustables en `config.py`: `MAX_TRACE_LENGTH` (3000), `MAX_INPUT_ELEMENTS`
(200 000), `MAX_STRUCTURES` (64), `MAX_DATASETS` (32), `MAX_RUN_HISTORY` (50).

---

## Notas de seguridad

- El estado (estructuras, datasets, historial) vive **en memoria**; se pierde al reiniciar.
  No es un problema para el alcance del proyecto, pero no uses esta app como almacenamiento.
- La carga de datasets es en memoria y está acotada por `MAX_DATASETS`; no se escriben
  archivos del usuario al disco.
- Nunca registres la `SECRET_KEY` real en el repositorio: declárala como variable de
  entorno y mantén `.env` fuera del control de versiones (ver `.gitignore`).
- La app escucha en `127.0.0.1`; si la expones en red, revisa los límites de entrada
  (`MAX_INPUT_ELEMENTS`) y ejecuta tras un proxy con HTTPS.

---

## Módulos académicos cubiertos

B · Listas y vectores — C · Pilas y colas — D · Árboles y grafos —
E · Búsqueda y ordenamiento — F · Tablas hash — G · Programación dinámica —
H · Algoritmos greedy — I · Estructuras avanzadas — J · Ciencia de datos —
K · Ética y seguridad — L · Proyectos y análisis experimental.
