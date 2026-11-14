"""Pruebas de algoritmos de ordenamiento."""

import random

import pytest

from algorithms.sorting import ALGORITHMS, bubble_sort, quick_sort, selection_sort


def reference_sorted(values):
    """Orden de referencia con la librería estándar (solo para verificar)."""
    return sorted(values)


@pytest.mark.parametrize("sorter_name", ALGORITHMS.keys())
class TestSortingCorrectness:
    def _check(self, name, values):
        result = ALGORITHMS[name](values)
        assert result["sorted"] == reference_sorted(values)
        assert result["is_sorted_check"] is True

    def test_random_arrays(self, sorter_name):
        rng = random.Random(123)
        self._check(sorter_name, [rng.randint(-50, 50) for _ in range(50)])

    def test_empty(self, sorter_name):
        self._check(sorter_name, [])

    def test_single_element(self, sorter_name):
        self._check(sorter_name, [42])

    def test_duplicates(self, sorter_name):
        self._check(sorter_name, [5, 1, 5, 1, 5])

    def test_already_sorted(self, sorter_name):
        self._check(sorter_name, list(range(20)))

    def test_reverse_sorted(self, sorter_name):
        self._check(sorter_name, list(range(20, 0, -1)))

    def test_negative_numbers(self, sorter_name):
        self._check(sorter_name, [-3, 10, -7, 0, 2])


class TestOperationCounters:
    def test_bubble_best_case_uses_early_stop(self):
        """Lista ordenada: una pasada, cero intercambios (mejor caso O(n))."""
        result = bubble_sort([1, 2, 3, 4, 5])
        assert result["comparisons"] == 4
        assert result["swaps"] == 0

    def test_bubble_worst_case_comparisons(self):
        n = 20
        result = bubble_sort(list(range(n, 0, -1)))
        assert result["comparisons"] == n * (n - 1) // 2  # O(n²) exacto.

    def test_selection_always_quadratic_comparisons(self):
        n = 20
        for data in (list(range(n)), list(range(n, 0, -1))):
            result = selection_sort(data)
            assert result["comparisons"] == n * (n - 1) // 2

    def test_quick_average_beats_bubble(self):
        rng = random.Random(9)
        data = [rng.randint(0, 1000) for _ in range(500)]
        quick = quick_sort(data)["comparisons"]
        bubble = bubble_sort(data)["comparisons"]
        assert quick < bubble  # O(n log n) << O(n²) en promedio.

    def test_quick_worst_case_with_last_pivot(self):
        """Pivote último + datos ordenados degradan a O(n²)."""
        n = 30
        result = quick_sort(list(range(n)))
        assert result["comparisons"] == n * (n - 1) // 2
        assert result["max_recursion_depth"] == n - 2  # Recursión lineal profunda.

    def test_result_does_not_mutate_input(self):
        original = [3, 1, 2]
        bubble_sort(original)
        assert original == [3, 1, 2]  # El algoritmo trabaja sobre una copia.
