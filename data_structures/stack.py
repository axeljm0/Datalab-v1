"""Pila (Stack) implementada desde cero sobre el DynamicArray propio.

Reutiliza la estructura DynamicArray como almacenamiento crudo: la lección
de este módulo es la disciplina LIFO, no la gestión de memoria.
"""

from __future__ import annotations

from data_structures.arrays import DynamicArray


class StackEmptyError(IndexError):
    """Se intentó leer de una pila vacía."""


class Stack:
    """Pila LIFO construida sobre DynamicArray.

    Complejidades: push O(1) amortizado, pop O(1), peek O(1).
    """

    def __init__(self) -> None:
        self._items = DynamicArray()

    def push(self, value) -> None:
        """Apila un elemento en la cima. O(1) amortizado."""
        self._items.append(value)

    def pop(self):
        """Retira y devuelve el elemento de la cima. O(1)."""
        if self.is_empty():
            raise StackEmptyError("La pila está vacía")
        return self._items.delete_at(len(self._items) - 1)

    def peek(self):
        """Devuelve el elemento de la cima sin retirarlo. O(1)."""
        if self.is_empty():
            raise StackEmptyError("La pila está vacía")
        return self._items.get(len(self._items) - 1)

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def size(self) -> int:
        return len(self._items)

    def to_list(self):
        """Elementos desde la base hasta la cima."""
        return self._items.traverse()

    def snapshot(self) -> dict:
        return {"kind": "stack", "items": self.to_list(), "size": self.size()}
