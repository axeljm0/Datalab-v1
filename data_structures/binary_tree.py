"""Árbol binario de búsqueda (BST) implementado desde cero.

Inserción, búsqueda y eliminación con las tres reglas del BST:
menores a la izquierda, mayores a la derecha, sin duplicados.
"""

from __future__ import annotations

from typing import Any, Optional


class BSTNode:
    """Nodo del árbol binario de búsqueda."""

    __slots__ = ("value", "left", "right")

    def __init__(self, value: Any) -> None:
        self.value = value
        self.left: Optional[BSTNode] = None
        self.right: Optional[BSTNode] = None


class BinarySearchTree:
    """BST sin duplicados.

    Complejidades (promedio / peor caso —árbol degenerado—):
        - insert:  O(log n) / O(n)
        - search:  O(log n) / O(n)
        - delete:  O(log n) / O(n)
        - recorrido: O(n)
    """

    def __init__(self) -> None:
        self.root: Optional[BSTNode] = None
        self.size = 0
        # Contadores de operaciones para análisis Big O empírico.
        self.comparisons = 0

    # ------------------------------------------------------------------
    # Inserción
    # ------------------------------------------------------------------
    def insert(self, value: Any) -> bool:
        """Inserta value; devuelve False si ya existía. O(h)."""
        if self.root is None:
            self.root = BSTNode(value)
            self.size += 1
            return True
        current = self.root
        while True:
            self.comparisons += 1
            if value == current.value:
                return False
            if value < current.value:
                if current.left is None:
                    current.left = BSTNode(value)
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = BSTNode(value)
                    break
                current = current.right
        self.size += 1
        return True

    # ------------------------------------------------------------------
    # Búsqueda
    # ------------------------------------------------------------------
    def search(self, value: Any) -> bool:
        """Búsqueda por comparación guiada por el orden del árbol. O(h)."""
        current = self.root
        while current is not None:
            self.comparisons += 1
            if value == current.value:
                return True
            current = current.left if value < current.value else current.right
        return False

    # ------------------------------------------------------------------
    # Eliminación
    # ------------------------------------------------------------------
    def delete(self, value: Any) -> bool:
        """Elimina un nodo considerando los tres casos. O(h)."""
        self.root, deleted = self._delete_recursive(self.root, value)
        if deleted:
            self.size -= 1
        return deleted

    def _delete_recursive(self, node: Optional[BSTNode], value):
        """Elimina recursivamente y devuelve la nueva raíz del subárbol."""
        if node is None:
            return None, False
        if value < node.value:
            node.left, deleted = self._delete_recursive(node.left, value)
            return node, deleted
        if value > node.value:
            node.right, deleted = self._delete_recursive(node.right, value)
            return node, deleted
        # Caso 1: nodo hoja. Caso 2: un solo hijo.
        if node.left is None:
            return node.right, True
        if node.right is None:
            return node.left, True
        # Caso 3: dos hijos → sucesor inorden (mínimo del subárbol derecho).
        successor = node.right
        while successor.left is not None:
            successor = successor.left
        node.value = successor.value
        node.right, _ = self._delete_recursive(node.right, successor.value)
        return node, True

    # ------------------------------------------------------------------
    # Recorridos
    # ------------------------------------------------------------------
    def inorder(self):
        """Izquierda → raíz → derecha. Produce valores en orden creciente. O(n)."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: Optional[BSTNode], result: list) -> None:
        if node is not None:
            self._inorder(node.left, result)
            result.append(node.value)
            self._inorder(node.right, result)

    def preorder(self):
        """Raíz → izquierda → derecha. Útil para reconstruir el árbol. O(n)."""
        result = []
        self._preorder(self.root, result)
        return result

    def _preorder(self, node: Optional[BSTNode], result: list) -> None:
        if node is not None:
            result.append(node.value)
            self._preorder(node.left, result)
            self._preorder(node.right, result)

    def postorder(self):
        """Izquierda → derecha → raíz. Útil para liberar memoria. O(n)."""
        result = []
        self._postorder(self.root, result)
        return result

    def _postorder(self, node: Optional[BSTNode], result: list) -> None:
        if node is not None:
            self._postorder(node.left, result)
            self._postorder(node.right, result)
            result.append(node.value)

    # ------------------------------------------------------------------
    # Serialización para el frontend
    # ------------------------------------------------------------------
    def snapshot(self) -> dict:
        """Nodos y aristas con posición lógica (para dibujar el árbol)."""
        nodes, edges = [], []

        def walk(node, node_id, depth):
            if node is None:
                return
            nodes.append({"id": node_id, "value": node.value, "depth": depth})
            if node.left is not None:
                left_id = node_id * 2 + 1
                edges.append({"source": node_id, "target": left_id, "side": "L"})
                walk(node.left, left_id, depth + 1)
            if node.right is not None:
                right_id = node_id * 2 + 2
                edges.append({"source": node_id, "target": right_id, "side": "R"})
                walk(node.right, right_id, depth + 1)

        walk(self.root, 0, 0)
        return {"kind": "tree", "nodes": nodes, "edges": edges, "size": self.size,
                "height": self.height(), "traversals": {
                    "inorder": self.inorder(), "preorder": self.preorder(),
                    "postorder": self.postorder()}}

    def height(self) -> int:
        """Altura del árbol (nodos en el camino más largo). O(n)."""
        return self._height(self.root)

    def _height(self, node) -> int:
        if node is None:
            return 0
        return 1 + max(self._height(node.left), self._height(node.right))
