"""Lista enlazada simple implementada desde cero.

Cada nodo se almacena en un objeto Node con referencia `next`, de modo
que la estructura vive dispersa en memoria (nodos + enlaces), a
diferencia del arreglo contiguo.
"""

from __future__ import annotations

from typing import Any, Optional


class LinkedListNode:
    """Nodo de la lista enlazada simple."""

    __slots__ = ("value", "next")

    def __init__(self, value: Any, next_node: Optional["LinkedListNode"] = None) -> None:
        self.value = value
        self.next = next_node


class SinglyLinkedList:
    """Lista enlazada simple con referencia a cabeza y cola.

    Complejidades:
        - insert_head: O(1) | insert_tail: O(1) | insert_at: O(n)
        - delete:      O(n) | search: O(n) | traverse: O(n)
    """

    def __init__(self) -> None:
        self.head: Optional[LinkedListNode] = None
        self.tail: Optional[LinkedListNode] = None
        self.size = 0

    def is_empty(self) -> bool:
        return self.head is None

    def insert_head(self, value: Any) -> LinkedListNode:
        """Inserta al inicio. O(1)."""
        node = LinkedListNode(value, self.head)
        self.head = node
        if self.tail is None:
            self.tail = node
        self.size += 1
        return node

    def insert_tail(self, value: Any) -> LinkedListNode:
        """Inserta al final. O(1) gracias a la referencia tail."""
        node = LinkedListNode(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1
        return node

    def insert_at(self, index: int, value: Any) -> LinkedListNode:
        """Inserta en la posición index (0-based). O(n)."""
        if index < 0 or index > self.size:
            raise IndexError(f"Índice {index} fuera de rango (tamaño {self.size})")
        if index == 0:
            return self.insert_head(value)
        if index == self.size:
            return self.insert_tail(value)
        previous = self._node_at(index - 1)
        node = LinkedListNode(value, previous.next)
        previous.next = node
        self.size += 1
        return node

    def _node_at(self, index: int) -> LinkedListNode:
        """Devuelve el nodo en index recorriendo desde la cabeza. O(n)."""
        current = self.head
        for _ in range(index):
            current = current.next
        return current

    def delete(self, value: Any) -> bool:
        """Elimina la primera aparición de value. O(n). Devuelve True si eliminó."""
        previous, current = None, self.head
        while current is not None:
            if current.value == value:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                if current is self.tail:
                    self.tail = previous
                self.size -= 1
                return True
            previous, current = current, current.next
        return False

    def delete_at(self, index: int) -> Any:
        """Elimina el nodo en index. O(n)."""
        if index < 0 or index >= self.size:
            raise IndexError(f"Índice {index} fuera de rango (tamaño {self.size})")
        if index == 0:
            node = self.head
            self.head = node.next
            if node is self.tail:
                self.tail = None
            self.size -= 1
            return node.value
        previous = self._node_at(index - 1)
        node = previous.next
        previous.next = node.next
        if node is self.tail:
            self.tail = previous
        self.size -= 1
        return node.value

    def search(self, value: Any) -> int:
        """Devuelve la posición de la primera aparición o -1. O(n)."""
        current, position = self.head, 0
        while current is not None:
            if current.value == value:
                return position
            current, position = current.next, position + 1
        return -1

    def update(self, index: int, value: Any) -> None:
        """Reemplaza el valor del nodo en index. O(n)."""
        self._node_at(index).value = value

    def traverse(self):
        """Recorrido de cabeza a cola. O(n)."""
        result, current = [], self.head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def to_list(self):
        return self.traverse()

    def snapshot(self) -> dict:
        """Estado serializable: nodos con sus enlaces para el frontend."""
        nodes, current = [], self.head
        while current is not None:
            nodes.append({"value": current.value})
            current = current.next
        return {"kind": "singly_list", "nodes": nodes, "size": self.size}
