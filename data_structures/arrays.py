"""Arreglos dinámicos y matrices implementados desde cero.

La clase DynamicArray simula un arreglo de capacidad fija sobre la cual
construye el crecimiento amortizado que caracteriza a un vector dinámico.
La lista nativa de Python solo se usa como bloque de memoria crudo
(casillas fijas), nunca para obtener comportamiento de alto nivel.
"""

from __future__ import annotations


class ArrayOverflowError(IndexError):
    """Se superó la capacidad física del arreglo subyacente."""


class DynamicArray:
    """Vector dinámico con crecimiento amortizado (factor 2).

    Complejidades:
        - append:      O(1) amortizado, O(n) cuando se redimensiona.
        - insert_at:   O(n)  (desplaza elementos a la derecha).
        - delete_at:   O(n)  (desplaza elementos a la izquierda).
        - search:      O(n)  (búsqueda lineal).
        - update:      O(1)  (acceso por índice).
    """

    def __init__(self, initial_capacity: int = 8) -> None:
        if initial_capacity < 1:
            raise ValueError("La capacidad inicial debe ser mayor que cero")
        self._capacity = initial_capacity
        self._size = 0
        # Bloque de memoria crudo: casillas fijas inicializadas en None.
        self._data: list = [None] * self._capacity
        self.resize_count = 0

    # ------------------------------------------------------------------
    # Operaciones básicas
    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def capacity(self) -> int:
        return self._capacity

    def _check_index(self, index: int, upper_inclusive: bool = False) -> None:
        upper = self._size if upper_inclusive else self._size - 1
        if index < 0 or index > upper:
            raise IndexError(f"Índice {index} fuera de rango (tamaño {self._size})")

    def _resize(self, new_capacity: int) -> None:
        """Copia los elementos a un bloque de memoria más grande. O(n)."""
        new_block = [None] * new_capacity
        for i in range(self._size):
            new_block[i] = self._data[i]
        self._data = new_block
        self._capacity = new_capacity
        self.resize_count += 1

    def append(self, value) -> None:
        """Agrega un elemento al final. O(1) amortizado."""
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._data[self._size] = value
        self._size += 1

    def insert_at(self, index: int, value) -> None:
        """Inserta un elemento en la posición index desplazando el resto. O(n)."""
        self._check_index(index, upper_inclusive=True)
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        i = self._size
        while i > index:
            self._data[i] = self._data[i - 1]
            i -= 1
        self._data[index] = value
        self._size += 1

    def delete_at(self, index: int):
        """Elimina y devuelve el elemento en index, desplazando a la izquierda. O(n)."""
        self._check_index(index)
        removed = self._data[index]
        i = index
        while i < self._size - 1:
            self._data[i] = self._data[i + 1]
            i += 1
        self._data[self._size - 1] = None
        self._size -= 1
        # Encogimiento cuando la ocupación baja de 25% de la capacidad.
        if self._size > 0 and self._size <= self._capacity // 4:
            self._resize(max(self._capacity // 2, 4))
        return removed

    def update(self, index: int, value) -> None:
        """Reemplaza el valor en index. O(1)."""
        self._check_index(index)
        self._data[index] = value

    def search(self, value) -> int:
        """Búsqueda lineal. Devuelve el índice o -1. O(n)."""
        for i in range(self._size):
            if self._data[i] == value:
                return i
        return -1

    def get(self, index: int):
        self._check_index(index)
        return self._data[index]

    def traverse(self):
        """Devuelve la secuencia de elementos en orden. O(n)."""
        return [self._data[i] for i in range(self._size)]

    def to_list(self):
        return self.traverse()

    def snapshot(self) -> dict:
        """Estado serializable para el frontend."""
        return {
            "kind": "array",
            "elements": self.traverse(),
            "size": self._size,
            "capacity": self._capacity,
            "resizes": self.resize_count,
        }


class Matrix:
    """Matriz bidimensional de dimensiones fijas. Acceso O(1).

    Se implementa sobre un bloque lineal de memoria crudo con la
    fórmula de direccionamiento fila*columnas + columna.
    """

    def __init__(self, rows: int, cols: int, fill=0) -> None:
        if rows < 1 or cols < 1:
            raise ValueError("Dimensiones de la matriz deben ser positivas")
        self.rows = rows
        self.cols = cols
        self._block = [fill] * (rows * cols)

    def _flat_index(self, r: int, c: int) -> int:
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError(f"Posición ({r},{c}) fuera de la matriz")
        return r * self.cols + c

    def get(self, r: int, c: int):
        return self._block[self._flat_index(r, c)]

    def set(self, r: int, c: int, value) -> None:
        self._block[self._flat_index(r, c)] = value

    def fill_with(self, values) -> None:
        """Rellena la matriz con una lista de listas compatible."""
        if len(values) != self.rows or any(len(row) != self.cols for row in values):
            raise ValueError("Las dimensiones de los datos no coinciden con la matriz")
        for r, row in enumerate(values):
            for c, v in enumerate(row):
                self.set(r, c, v)

    def transpose(self) -> "Matrix":
        """Devuelve la matriz transpuesta. O(rows*cols)."""
        result = Matrix(self.cols, self.rows)
        for r in range(self.rows):
            for c in range(self.cols):
                result.set(c, r, self.get(r, c))
        return result

    def add(self, other: "Matrix") -> "Matrix":
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Las matrices deben tener las mismas dimensiones")
        result = Matrix(self.rows, self.cols)
        for r in range(self.rows):
            for c in range(self.cols):
                result.set(r, c, self.get(r, c) + other.get(r, c))
        return result

    def to_list(self):
        return [[self.get(r, c) for c in range(self.cols)] for r in range(self.rows)]

    def snapshot(self) -> dict:
        return {"kind": "matrix", "rows": self.rows, "cols": self.cols, "cells": self.to_list()}
