"""Montículos binarios (Min Heap y Max Heap) implementados desde cero.

Comparten una base BinaryHeap parametrizada por comparador, evitando
duplicar la lógica de sift-up / sift-down. Se modela el heap sobre un
bloque de memoria crudo con la fórmula de árbol implícito:
    hijo izquierdo = 2i+1, hijo derecho = 2i+2, padre = (i-1)//2
"""

from __future__ import annotations

from typing import Callable


class HeapEmptyError(IndexError):
    """Se intentó extraer de un montículo vacío."""


class BinaryHeap:
    """Montículo binario parametrizado por comparador.

    Complejidades: push O(log n), pop O(log n), peek O(1), build O(n).
    """

    def __init__(self, comparator: Callable[[Any, Any], bool], label: str) -> None:
        """comparator(a, b) devuelve True si `a` debe ir antes que `b`."""
        self._comparator = comparator
        self.label = label
        self._heap: list = []
        self.swaps = 0      # Movimientos producidos por los sift.
        self.comparisons = 0

    # ------------------------------------------------------------------
    # Operaciones básicas
    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def peek(self):
        if self.is_empty():
            raise HeapEmptyError("El montículo está vacío")
        return self._heap[0]

    def push(self, value) -> None:
        """Inserta un valor y lo hace subir (sift-up). O(log n)."""
        self._heap.append(value)
        self._sift_up(len(self._heap) - 1)

    def pop(self):
        """Extrae la raíz (mínimo o máximo) y reorganiza (sift-down). O(log n)."""
        if self.is_empty():
            raise HeapEmptyError("El montículo está vacío")
        root = self._heap[0]
        last = self._heap.pop()
        if self._heap:
            self._heap[0] = last
            self._sift_down(0)
        return root

    @classmethod
    def build_heap(cls, values: list, comparator: Callable[[Any, Any], bool], label: str = "") -> "BinaryHeap":
        """Construcción bottom-up en O(n) aplicando sift-down desde el último padre."""
        heap = cls.__new__(cls)
        heap._comparator = comparator
        heap.label = label
        heap.swaps = 0
        heap.comparisons = 0
        heap._heap = list(values)
        heap._heapify()
        return heap

    # ------------------------------------------------------------------
    # Reorganización interna
    # ------------------------------------------------------------------
    def _sift_up(self, index: int) -> None:
        """Compara con el padre y sube mientras se incumpla el orden."""
        while index > 0:
            parent = (index - 1) // 2
            self.comparisons += 1
            if self._comparator(self._heap[index], self._heap[parent]):
                self._heap[index], self._heap[parent] = self._heap[parent], self._heap[index]
                self.swaps += 1
                index = parent
            else:
                break

    def _sift_down(self, index: int) -> None:
        """Baja el nodo comparando con el hijo preferido."""
        size = len(self._heap)
        while True:
            left, right = 2 * index + 1, 2 * index + 2
            preferred = index
            if left < size:
                self.comparisons += 1
                if self._comparator(self._heap[left], self._heap[preferred]):
                    preferred = left
            if right < size:
                self.comparisons += 1
                if self._comparator(self._heap[right], self._heap[preferred]):
                    preferred = right
            if preferred == index:
                break
            self._heap[index], self._heap[preferred] = self._heap[preferred], self._heap[index]
            self.swaps += 1
            index = preferred

    def _heapify(self) -> None:
        """Convierte el arreglo actual en un montículo válido. O(n)."""
        for start in range(len(self._heap) // 2 - 1, -1, -1):
            self._sift_down(start)

    # ------------------------------------------------------------------
    # Serialización
    # ------------------------------------------------------------------
    def levels(self):
        """Valores agrupados por nivel para dibujar el árbol implícito."""
        result, level_start, level = [], 0, 1
        while level_start < len(self._heap):
            result.append(self._heap[level_start:level_start + level])
            level_start += level
            level *= 2
        return result

    def to_list(self):
        return list(self._heap)

    def snapshot(self) -> dict:
        return {"kind": "heap", "variant": self.label, "levels": self.levels(),
                "items": self.to_list(), "size": len(self._heap),
                "swaps": self.swaps, "comparisons": self.comparisons}


def _min_first(a, b) -> bool:
    return a < b


def _max_first(a, b) -> bool:
    return a > b


class MinHeap(BinaryHeap):
    """Montículo de mínimos: la raíz es el valor más pequeño."""

    def __init__(self) -> None:
        super().__init__(_min_first, "min")


class MaxHeap(BinaryHeap):
    """Montículo de máximos: la raíz es el valor más grande."""

    def __init__(self) -> None:
        super().__init__(_max_first, "max")


def heap_sort(values: list, ascending: bool = True) -> list:
    """Ordenamiento por montículo implementado con las clases propias. O(n log n).

    Ascendente: extrae con MaxHeap (salida descendente) y invierte el orden.
    Descendente: extrae con MinHeap (salida ascendente) y invierte el orden.
    """
    source_heap = MaxHeap() if ascending else MinHeap()
    for value in values:
        source_heap.push(value)
    extracted = []
    while not source_heap.is_empty():
        extracted.append(source_heap.pop())
    extracted.reverse()
    return extracted
