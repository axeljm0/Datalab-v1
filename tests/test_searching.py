"""Pruebas de algoritmos de búsqueda."""

import pytest

from algorithms.searching import binary_search, is_sorted, linear_search


class TestLinearSearch:
    def test_finds_existing_element(self):
        result = linear_search([4, 8, 15, 16, 23], 15)
        assert result["found"] is True
        assert result["index"] == 2

    def test_element_not_found(self):
        result = linear_search([1, 2, 3], 99)
        assert result["found"] is False
        assert result["index"] == -1
        assert result["comparisons"] == 3  # Recorrió toda la lista.

    def test_first_element_is_best_case(self):
        result = linear_search([7, 1, 2, 3], 7)
        assert result["comparisons"] == 1  # Mejor caso O(1).

    def test_empty_list(self):
        result = linear_search([], 5)
        assert result["found"] is False
        assert result["comparisons"] == 0

    def test_works_with_strings(self):
        result = linear_search(["a", "b", "c"], "b")
        assert result["index"] == 1


class TestBinarySearch:
    def test_finds_existing_element(self):
        result = binary_search([1, 3, 5, 7, 9, 11], 7)
        assert result["found"] is True
        assert result["index"] == 3

    def test_finds_first_and_last(self):
        data = list(range(0, 100, 2))
        assert binary_search(data, 0)["found"] is True
        assert binary_search(data, 98)["found"] is True

    def test_element_not_found(self):
        result = binary_search([1, 3, 5], 4)
        assert result["found"] is False
        assert result["comparisons"] <= 2  # log2(3) redondeado.

    def test_rejects_unsorted_data(self):
        """Binary search debe negarse con datos desordenados (precondición)."""
        with pytest.raises(ValueError):
            binary_search([3, 1, 2], 2)

    def test_comparisons_grow_logarithmically(self):
        for size in (100, 1000, 10000):
            data = list(range(size))
            result = binary_search(data, size - 1)
            assert result["comparisons"] <= 17  # log2(10000) ≈ 13.3.

    def test_empty_list(self):
        result = binary_search([], 1)
        assert result["found"] is False


class TestIsSorted:
    def test_sorted_detection(self):
        assert is_sorted([1, 2, 3]) is True
        assert is_sorted([1, 3, 2]) is False
        assert is_sorted([]) is True
        assert is_sorted([5]) is True
