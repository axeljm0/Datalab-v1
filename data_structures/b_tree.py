"""Árbol B de orden mínimo t implementado desde cero (algoritmo CLRS).

Mantiene todas las hojas al mismo nivel y entre t-1 y 2t-1 claves por
nodo. Optimizado para almacenamiento secundario: pocas alturas, muchas
claves por nodo.
"""

from __future__ import annotations

from bisect import bisect_left  # Solo utilidad auxiliar de índice binario sobre claves del nodo.

from typing import Any, Optional


class BTreeNode:
    """Nodo del árbol B con claves e hijos (máximo 2t claves, 2t+1 hijos)."""

    __slots__ = ("keys", "children", "leaf")

    def __init__(self, leaf: bool) -> None:
        self.keys: list = []
        self.children: list[BTreeNode] = []
        self.leaf = leaf


class BTree:
    """Árbol B con inserción por división de nodos y búsqueda estándar.

    Complejidades: insert O(log n) divisiones, search O(log n) accesos,
    delete O(log n).
    """

    def __init__(self, min_degree: int = 2) -> None:
        """min_degree = t: mínimo t-1 claves por nodo, máximo 2t-1."""
        if min_degree < 2:
            raise ValueError("El grado mínimo t debe ser al menos 2")
        self.t = min_degree
        self.root = BTreeNode(leaf=True)
        self.size = 0
        self.splits = 0  # División de nodos registradas para el laboratorio.

    # ------------------------------------------------------------------
    # Inserción
    # ------------------------------------------------------------------
    def insert(self, key) -> bool:
        """Inserta una clave; divide nodos llenos por el camino. O(log n)."""
        if self.search(key):
            return False
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(new_root, key)
        else:
            self._insert_non_full(root, key)
        self.size += 1
        return True

    def _split_child(self, parent: BTreeNode, index: int) -> None:
        """Divide el hijo lleno en la posición index. O(t)."""
        t = self.t
        child = parent.children[index]
        right = BTreeNode(leaf=child.leaf)
        middle = child.keys[t - 1]
        right.keys = child.keys[t:]              # Mitad superior al nuevo nodo.
        child.keys = child.keys[:t - 1]          # Mitad inferior se queda.
        if not child.leaf:
            right.children = child.children[t:]
            child.children = child.children[:t]
        parent.keys.insert(index, middle)
        parent.children.insert(index + 1, right)
        self.splits += 1

    def _insert_non_full(self, node: BTreeNode, key) -> None:
        """Desciende hasta una hoja, dividiendo hijos llenos en el camino."""
        position = bisect_left(node.keys, key)
        if node.leaf:
            node.keys.insert(position, key)
            return
        child = node.children[position]
        if len(child.keys) == 2 * self.t - 1:
            self._split_child(node, position)
            if key > node.keys[position]:
                position += 1
            child = node.children[position]
        self._insert_non_full(child, key)

    # ------------------------------------------------------------------
    # Búsqueda
    # ------------------------------------------------------------------
    def search(self, key) -> bool:
        """Búsqueda multinivel dentro de cada nodo. O(log n)."""
        node = self.root
        while node is not None:
            position = bisect_left(node.keys, key)
            if position < len(node.keys) and node.keys[position] == key:
                return True
            if node.leaf:
                return False
            node = node.children[position]
        return False

    # ------------------------------------------------------------------
    # Eliminación
    # ------------------------------------------------------------------
    def delete(self, key) -> bool:
        """Eliminación estándar con fusiones y préstamos entre hermanos."""
        if not self.search(key):
            return False
        self._delete(self.root, key)
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]
        self.size -= 1
        return True

    def _delete(self, node: BTreeNode, key) -> None:
        t = self.t
        position = bisect_left(node.keys, key)
        if position < len(node.keys) and node.keys[position] == key:
            if node.leaf:  # Caso 1: clave en hoja.
                node.keys.pop(position)
                return
            # Caso 2: clave en nodo interno.
            left, right = node.children[position], node.children[position + 1]
            if len(left.keys) >= t:  # 2a: predecesor.
                node.keys[position] = self._remove_max(left)
                return
            if len(right.keys) >= t:  # 2b: sucesor.
                node.keys[position] = right.keys.pop(0)
                return
            self._merge(node, position)  # 2c: fusión y recursión.
            self._delete(node.children[position], key)
            return
        if node.leaf:
            return  # La clave no existe.
        child_index = position
        child = node.children[child_index]
        if len(child.keys) < t:  # Caso 3: hijo con mínimas claves.
            sibling_index = child_index + 1 if child_index > 0 else child_index + 1
            if child_index > 0 and len(node.children[child_index - 1].keys) >= t:
                self._borrow_from_left(node, child_index)
                child_index -= 0
            elif sibling_index < len(node.children) and len(node.children[sibling_index].keys) >= t:
                self._borrow_from_right(node, child_index)
            else:
                merge_index = child_index if child_index > 0 else child_index
                if child_index > 0:
                    merge_index = child_index - 1
                self._merge(node, merge_index)
                child_index = merge_index
        self._delete(node.children[child_index], key)

    def _remove_max(self, node: BTreeNode):
        """Extrae la clave máxima del subárbol (para el predecesor)."""
        while not node.leaf:
            node = node.children[-1]
        return node.keys.pop()

    def _merge(self, node: BTreeNode, index: int) -> None:
        """Fusiona children[index], keys[index] y children[index+1]."""
        left, right = node.children[index], node.children[index + 1]
        left.keys.append(node.keys.pop(index))
        left.keys.extend(right.keys)
        left.children.extend(right.children)
        node.children.pop(index + 1)

    def _borrow_from_left(self, parent: BTreeNode, index: int) -> None:
        """Rota una clave del hermano izquierdo hacia el hijo con déficit."""
        child, sibling = parent.children[index], parent.children[index - 1]
        child.keys.insert(0, parent.keys[index - 1])
        parent.keys[index - 1] = sibling.keys.pop()
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())

    def _borrow_from_right(self, parent: BTreeNode, index: int) -> None:
        """Rota una clave del hermano derecho hacia el hijo con déficit."""
        child, sibling = parent.children[index], parent.children[index + 1]
        child.keys.append(parent.keys[index])
        parent.keys[index] = sibling.keys.pop(0)
        if not child.leaf:
            child.children.append(sibling.children.pop(0))

    # ------------------------------------------------------------------
    # Serialización
    # ------------------------------------------------------------------
    def snapshot(self) -> dict:
        """Nodos por nivel con sus claves y aristas padre-hijo."""
        nodes, edges = [], []

        def walk(node: Optional[BTreeNode], node_id: int, depth: int):
            if node is None:
                return
            nodes.append({"id": node_id, "keys": list(node.keys), "leaf": node.leaf,
                          "depth": depth})
            for i, child in enumerate(node.children):
                child_id = node_id * 100 + i
                edges.append({"source": node_id, "target": child_id})
                walk(child, child_id, depth + 1)

        walk(self.root, 0, 0)
        return {"kind": "b_tree", "min_degree": self.t, "nodes": nodes, "edges": edges,
                "size": self.size, "splits": self.splits,
                "height": self._height(self.root)}

    def _height(self, node: BTreeNode) -> int:
        height = 1
        while not node.leaf:
            node = node.children[0]
            height += 1
        return height
