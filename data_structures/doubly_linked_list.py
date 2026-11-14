"""Lista doblemente enlazada implementada desde cero.

Cada nodo mantiene referencias `prev` y `next`, lo que permite recorridos
en ambos sentidos y eliminación O(1) cuando ya se tiene el nodo.
"""

from __future__ import annotations

from typing import Any, Optional


class DoublyNode:
    """Nodo con punteros prev y next."""

    __slots__ = ("value", "prev", "next")

    def __init__(self, value: Any) -> None:
        self.value = value
        self.prev: Optional[DoublyNode] = None
        self.next: Optional[DoublyNode] = None


class DoublyLinkedList:
    """Lista doblemente enlazada con cabeza y cola.

    Complejidades:
        - insert_head / insert_tail: O(1)
        - insert_at / delete / search / traverse: O(n)
    """

    def __init__(self) -> None:
        self.head: Optional[DoublyNode] = None
        self.tail: Optional[DoublyNode] = None
        self.size = 0

    def is_empty(self) -> bool:
        return self.head is None

    def insert_head(self, value: Any) -> DoublyNode:
        node = DoublyNode(value)
        if self.head is None:
            self.head = self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        self.size += 1
        return node

    def insert_tail(self, value: Any) -> DoublyNode:
        node = DoublyNode(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.size += 1
        return node

    def insert_at(self, index: int, value: Any) -> DoublyNode:
        """Inserta en la posición index (0-based). O(n)."""
        if index < 0 or index > self.size:
            raise IndexError(f"Índice {index} fuera de rango (tamaño {self.size})")
        if index == 0:
            return self.insert_head(value)
        if index == self.size:
            return self.insert_tail(value)
        node = DoublyNode(value)
        successor = self._node_at(index)
        predecessor = successor.prev
        node.prev, node.next = predecessor, successor
        predecessor.next = node
        successor.prev = node
        self.size += 1
        return node

    def _node_at(self, index: int) -> DoublyNode:
        """Nodo en index; recorre desde el extremo más cercano. O(n)."""
        if index < self.size // 2:
            current = self.head
            for _ in range(index):
                current = current.next
        else:
            current = self.tail
            for _ in range(self.size - 1 - index):
                current = current.prev
        return current

    def delete(self, value: Any) -> bool:
        """Elimina la primera aparición de value. O(n)."""
        current = self.head
        while current is not None:
            if current.value == value:
                self._unlink(current)
                return True
            current = current.next
        return False

    def delete_at(self, index: int) -> Any:
        """Elimina el nodo en index. O(n)."""
        if index < 0 or index >= self.size:
            raise IndexError(f"Índice {index} fuera de rango (tamaño {self.size})")
        node = self._node_at(index)
        self._unlink(node)
        return node.value

    def _unlink(self, node: DoublyNode) -> None:
        """Desconecta un nodo existente de la lista. O(1)."""
        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next
        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev
        node.prev = node.next = None
        self.size -= 1

    def search(self, value: Any) -> int:
        """Posición de la primera aparición o -1. O(n)."""
        current, position = self.head, 0
        while current is not None:
            if current.value == value:
                return position
            current, position = current.next, position + 1
        return -1

    def update(self, index: int, value: Any) -> None:
        self._node_at(index).value = value

    def traverse(self, reverse: bool = False):
        """Recorrido hacia adelante o hacia atrás. O(n)."""
        result, current = [], (self.tail if reverse else self.head)
        while current is not None:
            result.append(current.value)
            current = (current.prev if reverse else current.next)
        return result

    def to_list(self):
        return self.traverse()

    def snapshot(self) -> dict:
        forward = self.traverse()
        return {
            "kind": "doubly_list",
            "nodes": [{"value": v} for v in forward],
            "reverse": self.traverse(reverse=True),
            "size": self.size,
        }
