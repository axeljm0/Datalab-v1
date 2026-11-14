"""Cola (Queue) circular implementada desde cero.

Se modela un buffer circular sobre un bloque de memoria crudo con índices
front y rear que rotan módulo capacidad, evitando desplazamientos O(n).
"""

from __future__ import annotations


class QueueEmptyError(IndexError):
    """Se intentó leer de una cola vacía."""


class CircularQueue:
    """Cola FIFO con buffer circular y redimensionamiento. O(1) amortizado."""

    def __init__(self, initial_capacity: int = 8) -> None:
        if initial_capacity < 1:
            raise ValueError("La capacidad debe ser mayor que cero")
        self._capacity = initial_capacity
        # Bloque de memoria crudo de casillas fijas.
        self._buffer = [None] * self._capacity
        self._front = 0
        self._size = 0
        self.resize_count = 0

    def _resize(self) -> None:
        """Duplica la capacidad reubicando los elementos en orden lógico. O(n)."""
        new_capacity = self._capacity * 2
        new_buffer = [None] * new_capacity
        for i in range(self._size):
            new_buffer[i] = self._buffer[(self._front + i) % self._capacity]
        self._buffer = new_buffer
        self._capacity = new_capacity
        self._front = 0
        self.resize_count += 1

    def enqueue(self, value) -> None:
        """Agrega un elemento al final. O(1) amortizado."""
        if self._size == self._capacity:
            self._resize()
        rear = (self._front + self._size) % self._capacity
        self._buffer[rear] = value
        self._size += 1

    def dequeue(self):
        """Retira y devuelve el elemento del frente. O(1)."""
        if self.is_empty():
            raise QueueEmptyError("La cola está vacía")
        value = self._buffer[self._front]
        self._buffer[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._size -= 1
        return value

    def front(self):
        """Devuelve el elemento del frente sin retirarlo. O(1)."""
        if self.is_empty():
            raise QueueEmptyError("La cola está vacía")
        return self._buffer[self._front]

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    def to_list(self):
        """Elementos en orden FIFO (frente primero)."""
        return [self._buffer[(self._front + i) % self._capacity] for i in range(self._size)]

    def snapshot(self) -> dict:
        return {
            "kind": "queue",
            "items": self.to_list(),
            "capacity": self._capacity,
            "resizes": self.resize_count,
        }
