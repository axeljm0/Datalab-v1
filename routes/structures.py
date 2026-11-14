"""Blueprint de estructuras de datos: crea instancias y despacha operaciones.

Cada estructura vive en un registro en memoria identificado por `id`.
Las operaciones son atómicas por solicitud y devuelven siempre el
snapshot completo (o una traza) para que el frontend redibuje el estado.
"""

from flask import Blueprint, jsonify, render_template, request

from data_structures.arrays import DynamicArray, Matrix
from data_structures.avl_tree import AVLTree
from data_structures.b_tree import BTree
from data_structures.binary_tree import BinarySearchTree
from data_structures.doubly_linked_list import DoublyLinkedList
from data_structures.graph import Graph, GraphError
from data_structures.hash_table import HashTable
from data_structures.heap import MaxHeap, MinHeap
from data_structures.linked_list import SinglyLinkedList
from data_structures.queue import CircularQueue
from data_structures.stack import Stack
from services import run_history

structures_bp = Blueprint("structures", __name__)

# Registro de instancias: {"<id>": {"object": ..., "type": ...}}
_INSTANCES: dict = {}
_NEXT_ID = [1]

TREE_TYPES = {"bst": BinarySearchTree, "avl": AVLTree}
HEAP_TYPES = {"min_heap": MinHeap, "max_heap": MaxHeap}


# ----------------------------------------------------------------------
# Registro de instancias
# ----------------------------------------------------------------------
def _create_instance(structure_type: str, options: dict):
    """Instancia la estructura solicitada con sus opciones."""
    if structure_type == "array":
        return DynamicArray(int(options.get("capacity", 8)))
    if structure_type == "matrix":
        return Matrix(int(options.get("rows", 3)), int(options.get("cols", 3)))
    if structure_type in ("singly_list",):
        return SinglyLinkedList()
    if structure_type == "doubly_list":
        return DoublyLinkedList()
    if structure_type == "stack":
        return Stack()
    if structure_type == "queue":
        return CircularQueue(int(options.get("capacity", 8)))
    if structure_type in TREE_TYPES:
        return TREE_TYPES[structure_type]()
    if structure_type == "graph":
        return Graph(directed=bool(options.get("directed", False)))
    if structure_type == "hash_table":
        return HashTable(int(options.get("capacity", 8)))
    if structure_type in HEAP_TYPES:
        return HEAP_TYPES[structure_type]()
    if structure_type == "b_tree":
        return BTree(int(options.get("min_degree", 2)))
    raise ValueError(f"Tipo de estructura desconocido: {structure_type}")


def _get_instance(instance_id: str):
    entry = _INSTANCES.get(instance_id)
    if entry is None:
        raise ValueError(f"Estructura '{instance_id}' no existe")
    return entry


def _snapshot(instance) -> dict:
    """Snapshot universal: los árboles añaden info de variantes."""
    state = instance.snapshot()
    if isinstance(instance, BinarySearchTree):
        state["variant"] = "bst"
    if isinstance(instance, (MinHeap, MaxHeap)):
        pass
    return state


# ----------------------------------------------------------------------
# Rutas REST
# ----------------------------------------------------------------------
@structures_bp.route("/laboratories/lists")
def lists_lab():
    return render_template("laboratories/lists.html")


@structures_bp.route("/laboratories/stack-queue")
def stack_queue_lab():
    return render_template("laboratories/stack_queue.html")


@structures_bp.route("/laboratories/trees")
def trees_lab():
    return render_template("laboratories/trees.html")


@structures_bp.route("/laboratories/hash")
def hash_lab():
    return render_template("laboratories/hash.html")


@structures_bp.route("/laboratories/advanced")
def advanced_lab():
    return render_template("laboratories/advanced.html")


@structures_bp.route("/api/structures", methods=["POST"])
def create_structure():
    """Crea una instancia de estructura: {type, options?} → {id, snapshot}."""
    try:
        payload = request.get_json(force=True)
        structure_type = payload.get("type")
        if not structure_type:
            raise ValueError("Indique el tipo de estructura")
        options = payload.get("options") or {}
        instance = _create_instance(structure_type, options)
        instance_id = f"{structure_type}-{_NEXT_ID[0]}"
        _NEXT_ID[0] += 1
        _INSTANCES[instance_id] = {"object": instance, "type": structure_type}
        run_history.record_run("Estructura", "Crear instancia", instance_id)
        return jsonify(success=True, data={"id": instance_id,
                                           "snapshot": _snapshot(instance)})
    except (ValueError, TypeError) as error:
        return jsonify(success=False, error=str(error)), 400


@structures_bp.route("/api/structures/<instance_id>", methods=["GET"])
def get_structure(instance_id: str):
    """Devuelve el snapshot actual de la estructura."""
    try:
        entry = _get_instance(instance_id)
        return jsonify(success=True, data=_snapshot(entry["object"]))
    except ValueError as error:
        return jsonify(success=False, error=str(error)), 404


@structures_bp.route("/api/structures/<instance_id>", methods=["DELETE"])
def delete_structure(instance_id: str):
    try:
        _get_instance(instance_id)
        del _INSTANCES[instance_id]
        return jsonify(success=True)
    except ValueError as error:
        return jsonify(success=False, error=str(error)), 404


@structures_bp.route("/api/structures/<instance_id>/op", methods=["POST"])
def run_operation(instance_id: str):
    """Despacha una operación sobre la estructura: {operation, ...args}."""
    try:
        entry = _get_instance(instance_id)
        instance = entry["object"]
        payload = request.get_json(force=True)
        operation = payload.get("operation")
        if not operation:
            raise ValueError("Indique la operación a ejecutar")
        result = _dispatch(instance, entry["type"], operation, payload)
        run_history.record_run("Estructura", operation, instance_id)
        return jsonify(success=True, data={
            "snapshot": _snapshot(instance),
            **({"result": result} if result is not None else {}),
        })
    except (ValueError, TypeError, IndexError, KeyError, GraphError) as error:
        return jsonify(success=False, error=str(error)), 400


def _dispatch(instance, structure_type: str, operation: str, payload: dict):
    """Tabla de despacho de operaciones por tipo de estructura."""
    value = payload.get("value")
    index = payload.get("index")

    if structure_type in ("array", "matrix", "singly_list", "doubly_list"):
        return _linear_dispatch(instance, operation, value, index, payload)
    if structure_type in ("stack", "queue"):
        return _fifo_dispatch(instance, operation, value)
    if structure_type in ("bst", "avl"):
        return _tree_dispatch(instance, operation, value, payload)
    if structure_type == "graph":
        return _graph_dispatch(instance, operation, payload)
    if structure_type == "hash_table":
        return _hash_dispatch(instance, operation, payload)
    if structure_type in ("min_heap", "max_heap"):
        return _heap_dispatch(instance, operation, value)
    if structure_type == "b_tree":
        return _btree_dispatch(instance, operation, value, payload)
    raise ValueError("Operación no soportada para esta estructura")


# --- Listas, arreglos y matrices ----------------------------------------
def _linear_dispatch(instance, operation: str, value, index, payload: dict):
    if operation == "append":
        instance.append(value)
    elif operation == "insert_at":
        instance.insert_at(int(index), value)
    elif operation == "insert_head":
        instance.insert_head(value)
    elif operation == "insert_tail":
        instance.insert_tail(value)
    elif operation == "delete_at":
        removed = instance.delete_at(int(index))
        return {"removed": removed}
    elif operation == "delete":
        deleted = instance.delete(value)
        return {"deleted": deleted}
    elif operation == "search":
        found = instance.search(value)
        return {"index": found, "found": found != -1}
    elif operation == "update":
        instance.update(int(index), value)
    elif operation == "traverse":
        return {"elements": instance.traverse()}
    elif operation == "get":
        return {"value": instance.get(int(index))}
    elif operation == "set":
        instance.set(int(payload["row"]), int(payload["col"]), value)
    elif operation == "fill":
        instance.fill_with(payload["values"])
    elif operation == "transpose":
        matrix = instance.transpose()
        # Reemplaza el contenido del registro por la matriz transpuesta.
        instance.rows, instance.cols, instance._block = (
            matrix.rows, matrix.cols, matrix._block)
        return {"rows": instance.rows, "cols": instance.cols}
    elif operation == "add":
        other = Matrix(instance.rows, instance.cols)
        other.fill_with(payload["values"])
        matrix = instance.add(other)
        instance._block = matrix._block
    else:
        raise ValueError(f"Operación desconocida: {operation}")
    return None


# --- Pila y cola ---------------------------------------------------------
def _fifo_dispatch(instance, operation: str, value):
    if operation == "push" or operation == "enqueue":
        instance.push(value) if hasattr(instance, "push") else instance.enqueue(value)
    elif operation == "pop" or operation == "dequeue":
        removed = instance.pop() if hasattr(instance, "pop") else instance.dequeue()
        return {"removed": removed}
    elif operation == "peek" or operation == "front":
        top = instance.peek() if hasattr(instance, "peek") else instance.front()
        return {"top": top}
    elif operation == "is_empty":
        return {"empty": instance.is_empty()}
    else:
        raise ValueError(f"Operación desconocida: {operation}")
    return None


# --- Árboles BST/AVL -----------------------------------------------------
def _tree_dispatch(instance, operation: str, value, payload: dict):
    if operation == "insert":
        inserted = instance.insert(value)
        return {"inserted": inserted}
    if operation == "delete":
        deleted = instance.delete(value)
        return {"deleted": deleted}
    if operation == "search":
        found = instance.search(value)
        return {"found": found}
    if operation in ("inorder", "preorder", "postorder"):
        return {"order": getattr(instance, operation)()}
    if operation == "height":
        return {"height": instance.height()}
    raise ValueError(f"Operación desconocida: {operation}")


# --- Grafos ---------------------------------------------------------------
def _graph_dispatch(instance, operation: str, payload: dict):
    source, target = payload.get("source"), payload.get("target")
    if operation == "add_vertex":
        added = instance.add_vertex(source)
        return {"added": added}
    if operation == "add_edge":
        added = instance.add_edge(source, target,
                                  float(payload.get("weight", 1)))
        return {"added": added}
    if operation == "remove_edge":
        return {"removed": instance.remove_edge(source, target)}
    if operation == "remove_vertex":
        return {"removed": instance.remove_vertex(source)}
    if operation in ("bfs", "dfs"):
        order = getattr(instance, operation)(source)
        return {"order": order}
    raise ValueError(f"Operación desconocida: {operation}")


# --- Tabla hash -----------------------------------------------------------
def _hash_dispatch(instance, operation: str, payload: dict):
    key = payload.get("key")
    if operation == "insert":
        created = instance.insert(key, payload.get("value"))
        return {"updated": not created}
    if operation == "search":
        return {"value": instance.search(key), "found": True}
    if operation == "remove":
        return {"value": instance.remove(key)}
    if operation == "contains":
        return {"found": instance.contains(key)}
    raise ValueError(f"Operación desconocida: {operation}")


# --- Heaps -----------------------------------------------------------------
def _heap_dispatch(instance, operation: str, value):
    if operation == "push":
        instance.push(value)
    elif operation == "pop":
        return {"removed": instance.pop()}
    elif operation == "peek":
        return {"top": instance.peek()}
    elif operation == "clear":
        instance._heap.clear()
        instance.swaps = instance.comparisons = 0
    else:
        raise ValueError(f"Operación desconocida: {operation}")
    return None


# --- Árbol B -----------------------------------------------------------------
def _btree_dispatch(instance, operation: str, value, payload: dict):
    if operation == "insert":
        inserted = instance.insert(value)
        return {"inserted": inserted}
    if operation == "delete":
        deleted = instance.delete(value)
        return {"deleted": deleted}
    if operation == "search":
        return {"found": instance.search(value)}
    raise ValueError(f"Operación desconocida: {operation}")
