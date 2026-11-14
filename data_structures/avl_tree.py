"""Árbol AVL: BST auto-balanceado por factor de equilibrio.

Tras cada inserción o eliminación se recalcula la altura de los nodos del
camino y se aplican rotaciones (LL, RR, LR, RL) para mantener la altura
en O(log n), garantizando el mejor caso del BST también en el peor caso.
"""

from __future__ import annotations

from typing import Any, Optional


class AVLNode:
    """Nodo AVL con altura cacheada."""

    __slots__ = ("value", "left", "right", "height")

    def __init__(self, value: Any) -> None:
        self.value = value
        self.left: Optional[AVLNode] = None
        self.right: Optional[AVLNode] = None
        self.height = 1


class AVLTree:
    """Árbol AVL sin duplicados.

    Complejidades garantizadas: insert O(log n), delete O(log n), search O(log n).
    """

    def __init__(self) -> None:
        self.root: Optional[AVLNode] = None
        self.size = 0
        self.rotations = 0  # Contador de rotaciones para el laboratorio.

    # ------------------------------------------------------------------
    # Utilidades de altura y equilibrio
    # ------------------------------------------------------------------
    @staticmethod
    def node_height(node: Optional[AVLNode]) -> int:
        return node.height if node is not None else 0

    def balance_factor(self, node: Optional[AVLNode]) -> int:
        """Factor de equilibrio = altura(izq) - altura(der)."""
        if node is None:
            return 0
        return self.node_height(node.left) - self.node_height(node.right)

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(self.node_height(node.left), self.node_height(node.right))

    # ------------------------------------------------------------------
    # Rotaciones
    # ------------------------------------------------------------------
    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """Rotación derecha (desbalance LL: factor > 1 e hijo izq >= 0)."""
        x = y.left
        transfer = x.right
        x.right = y
        y.left = transfer
        self._update_height(y)
        self._update_height(x)
        self.rotations += 1
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """Rotación izquierda (desbalance RR: factor < -1 e hijo der >= 0)."""
        y = x.right
        transfer = y.left
        y.left = x
        x.right = transfer
        self._update_height(x)
        self._update_height(y)
        self.rotations += 1
        return y

    def _rebalance(self, node: AVLNode) -> AVLNode:
        """Restaura el equilibrio del nodo aplicando la rotación correcta."""
        self._update_height(node)
        factor = self.balance_factor(node)
        if factor > 1:  # Subárbol izquierdo más alto.
            if self.balance_factor(node.left) < 0:      # Caso LR.
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)             # Caso LL.
        if factor < -1:  # Subárbol derecho más alto.
            if self.balance_factor(node.right) > 0:     # Caso RL.
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)              # Caso RR.
        return node

    # ------------------------------------------------------------------
    # Inserción
    # ------------------------------------------------------------------
    def insert(self, value: Any) -> bool:
        """Inserta un valor y rebalancea el camino. O(log n)."""
        inserted = []

        def do_insert(node, value):
            if node is None:
                inserted.append(True)
                return AVLNode(value)
            if value == node.value:
                inserted.append(False)
                return node
            if value < node.value:
                node.left = do_insert(node.left, value)
            else:
                node.right = do_insert(node.right, value)
            return self._rebalance(node)

        self.root = do_insert(self.root, value)
        if inserted and inserted[0]:
            self.size += 1
        return bool(inserted and inserted[0])

    # ------------------------------------------------------------------
    # Búsqueda
    # ------------------------------------------------------------------
    def search(self, value: Any) -> bool:
        current = self.root
        while current is not None:
            if value == current.value:
                return True
            current = current.left if value < current.value else current.right
        return False

    # ------------------------------------------------------------------
    # Eliminación
    # ------------------------------------------------------------------
    def delete(self, value: Any) -> bool:
        """Elimina un valor y rebalancea el camino. O(log n)."""
        deleted = []

        def successor(node):
            while node.left is not None:
                node = node.left
            return node

        def do_delete(node, value):
            if node is None:
                deleted.append(False)
                return None
            if value < node.value:
                node.left = do_delete(node.left, value)
            elif value > node.value:
                node.right = do_delete(node.right, value)
            else:
                deleted.append(True)
                if node.left is None:
                    return node.right
                if node.right is None:
                    return node.left
                succ = successor(node.right)
                node.value = succ.value
                node.right = do_delete(node.right, succ.value)
            return self._rebalance(node)

        self.root = do_delete(self.root, value)
        if deleted and deleted[0]:
            self.size -= 1
        return bool(deleted and deleted[0])

    # ------------------------------------------------------------------
    # Recorridos y serialización
    # ------------------------------------------------------------------
    def inorder(self):
        result = []

        def walk(node):
            if node is not None:
                walk(node.left)
                result.append(node.value)
                walk(node.right)

        walk(self.root)
        return result

    def preorder(self):
        result = []

        def walk(node):
            if node is not None:
                result.append(node.value)
                walk(node.left)
                walk(node.right)

        walk(self.root)
        return result

    def postorder(self):
        result = []

        def walk(node):
            if node is not None:
                walk(node.left)
                walk(node.right)
                result.append(node.value)

        walk(self.root)
        return result

    def snapshot(self) -> dict:
        """Nodos con valor, altura y factor de equilibrio para el frontend."""
        nodes, edges = [], []

        def walk(node, node_id, depth):
            if node is None:
                return
            nodes.append({
                "id": node_id, "value": node.value, "depth": depth,
                "height": node.height, "balance": self.balance_factor(node),
            })
            for side, child in (("L", node.left), ("R", node.right)):
                if child is not None:
                    child_id = node_id * 2 + (1 if side == "L" else 2)
                    edges.append({"source": node_id, "target": child_id, "side": side})
                    walk(child, child_id, depth + 1)

        walk(self.root, 0, 0)
        return {"kind": "tree", "variant": "avl", "nodes": nodes, "edges": edges,
                "size": self.size, "rotations": self.rotations,
                "height": self.node_height(self.root),
                "traversals": {"inorder": self.inorder(), "preorder": self.preorder(),
                               "postorder": self.postorder()}}
