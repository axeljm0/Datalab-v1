"""Tabla Hash propia con resolución de colisiones por encadenamiento.

La función hash es polinomial (djb2 modificada) construida manualmente;
el redimensionamiento se dispara cuando el factor de carga supera 0.75.
"""

from __future__ import annotations

from typing import Any


class HashTableError(KeyError):
    """Clave inexistente en la tabla."""


class HashTable:
    """Tabla hash con buckets encadenados y rehash automático.

    Complejidades (promedio): insert O(1), search O(1), delete O(1).
    Peor caso (todas las claves colisionan en un bucket): O(n).
    """

    LOAD_FACTOR_LIMIT = 0.75

    def __init__(self, initial_capacity: int = 8) -> None:
        if initial_capacity < 1:
            raise ValueError("La capacidad debe ser mayor que cero")
        self._capacity = initial_capacity
        # Cada bucket es una lista de pares [clave, valor] (cadenas).
        self._buckets: list = [[] for _ in range(self._capacity)]
        self._size = 0
        self.collisions = 0  # Total de colisiones registradas.
        self.resize_count = 0

    # ------------------------------------------------------------------
    # Función hash propia
    # ------------------------------------------------------------------
    def _hash(self, key) -> int:
        """Hash polinomial: h = h*31 + carácter, reducido al módulo. O(len(k))."""
        text = str(key)
        hash_value = 5381
        for character in text:
            hash_value = (hash_value * 31 + ord(character)) & 0xFFFFFFFF
        return hash_value % self._capacity

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------
    def load_factor(self) -> float:
        """Elementos / capacidad."""
        return self._size / self._capacity

    def _check_resize(self) -> None:
        """Duplica la capacidad cuando el factor de carga supera el límite."""
        if self.load_factor() > self.LOAD_FACTOR_LIMIT:
            self.resize_count += 1
            old_pairs = [pair for bucket in self._buckets for pair in bucket]
            self._capacity *= 2
            self._buckets = [[] for _ in range(self._capacity)]
            self._size = 0
            for key, value in old_pairs:
                self.insert(key, value)

    def insert(self, key, value) -> bool:
        """Inserta o actualiza una clave. O(1) promedio."""
        index = self._hash(key)
        bucket = self._buckets[index]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value  # Actualización de valor existente.
                return False
        if bucket:
            self.collisions += 1  # Clave nueva en un bucket ocupado.
        bucket.append([key, value])
        self._size += 1
        self._check_resize()
        return True

    def search(self, key):
        """Devuelve el valor asociado a la clave. O(1) promedio."""
        bucket = self._buckets[self._hash(key)]
        for pair in bucket:
            if pair[0] == key:
                return pair[1]
        raise HashTableError(f"Clave '{key}' no encontrada")

    def get(self, key, default=None):
        try:
            return self.search(key)
        except HashTableError:
            return default

    def remove(self, key):
        """Elimina una clave y devuelve su valor. O(1) promedio."""
        index = self._hash(key)
        bucket = self._buckets[index]
        for i, pair in enumerate(bucket):
            if pair[0] == key:
                value = pair[1]
                bucket.pop(i)
                self._size -= 1
                return value
        raise HashTableError(f"Clave '{key}' no encontrada")

    def contains(self, key) -> bool:
        bucket = self._buckets[self._hash(key)]
        return any(pair[0] == key for pair in bucket)

    def size(self) -> int:
        return self._size

    def keys(self):
        return [pair[0] for bucket in self._buckets for pair in bucket]

    def items(self):
        return [tuple(pair) for bucket in self._buckets for pair in bucket]

    def snapshot(self) -> dict:
        """Buckets con sus cadenas para visualizar colisiones."""
        return {
            "kind": "hash_table",
            "buckets": [
                {"index": i, "pairs": [{"key": k, "value": v} for k, v in bucket]}
                for i, bucket in enumerate(self._buckets)
            ],
            "capacity": self._capacity,
            "size": self._size,
            "load_factor": round(self.load_factor(), 3),
            "load_limit": self.LOAD_FACTOR_LIMIT,
            "collisions": self.collisions,
            "resizes": self.resize_count,
        }
