"""Pruebas de programación dinámica y greedy."""

import pytest

from algorithms.dynamic_programming import coin_change, fibonacci_dynamic, fibonacci_recursive, knapsack_01
from algorithms.greedy import activity_selection, greedy_coin_change, interval_scheduling, is_coin_system_canonical


class TestFibonacci:
    def test_recursive_matches_dynamic(self):
        for n in [0, 1, 2, 10, 15]:
            assert fibonacci_recursive(n)["value"] == fibonacci_dynamic(n)["value"]

    def test_known_values(self):
        assert fibonacci_dynamic(10)["value"] == 55
        assert fibonacci_dynamic(0)["value"] == 0
        assert fibonacci_dynamic(1)["value"] == 1

    def test_dynamic_is_linear(self):
        assert fibonacci_dynamic(100)["value"] == 354224848179261915075
        # 101 celdas calculadas: cada subproblema una vez.
        assert fibonacci_dynamic(10)["calls"] == 11

    def test_recursive_call_count_is_exponential(self):
        # fib(15) recursivo puro realiza muchas más llamadas que n+1.
        assert fibonacci_recursive(15)["calls"] > 1000

    def test_recursive_limit(self):
        with pytest.raises(ValueError):
            fibonacci_recursive(31)


class TestKnapsack:
    def test_known_solution(self):
        result = knapsack_01([2, 3, 4], [3, 4, 5], 5)
        assert result["best_value"] == 7
        assert result["selected_items"] == [0, 1]

    def test_table_dimensions(self):
        result = knapsack_01([1, 2], [10, 20], 4)
        assert len(result["table"]) == 3      # n+1 filas.
        assert len(result["table"][0]) == 5   # W+1 columnas.

    def test_nothing_fits(self):
        result = knapsack_01([10], [5], 3)
        assert result["best_value"] == 0
        assert result["selected_items"] == []

    def test_validates_negative_capacity(self):
        with pytest.raises(ValueError):
            knapsack_01([1], [1], -1)


class TestCoinChangeDP:
    def test_standard_system(self):
        result = coin_change([1, 2, 5], 11)
        assert result["min_coins"] == 3
        assert result["coins_used"] == [5, 5, 1]

    def test_impossible_amount(self):
        result = coin_change([2, 4], 3)
        assert result["solvable"] is False
        assert result["min_coins"] == -1

    def test_amount_zero(self):
        result = coin_change([1, 5], 0)
        assert result["min_coins"] == 0


class TestGreedy:
    def test_activity_selection_optimal_count(self):
        activities = [{"id": 1, "start": 1, "end": 3},
                      {"id": 2, "start": 1, "end": 8},
                      {"id": 3, "start": 2, "end": 5},
                      {"id": 4, "start": 4, "end": 7},
                      {"id": 5, "start": 5, "end": 9},
                      {"id": 6, "start": 8, "end": 10}]
        result = activity_selection(activities)
        assert result["count"] == 3
        assert result["optimal"] is True
        # Las seleccionadas no se solapan entre sí.
        ends = None
        for activity in result["selected"]:
            if ends is not None:
                assert activity["start"] >= ends
            ends = activity["end"]

    def test_interval_scheduling_same_behavior(self):
        intervals = [{"id": 1, "start": 0, "end": 4},
                     {"id": 2, "start": 4, "end": 6},
                     {"id": 3, "start": 5, "end": 9},
                     {"id": 4, "start": 8, "end": 12}]
        result = interval_scheduling(intervals)
        # [0,4], [4,6] (toca pero no solapa) y [8,12] son compatibles.
        assert result["count"] == 3

    def test_greedy_optimal_for_canonical_system(self):
        """Sistema {1,5,10,25}: greedy es óptimo (sistema canónico)."""
        result = greedy_coin_change([1, 5, 10, 25], 63)
        assert result["optimal"] is True
        assert result["total_coins"] == result["dp_min_coins"] == 6

    def test_greedy_not_optimal_for_noncanonical(self):
        """Sistema {1,3,4} con monto 6: greedy da 4+1+1 (3) vs DP 3+3 (2)."""
        result = greedy_coin_change([1, 3, 4], 6)
        assert result["total_coins"] == 3
        assert result["dp_min_coins"] == 2
        assert result["optimal"] is False

    def test_canonical_check_detects_noncanonical(self):
        result = is_coin_system_canonical([1, 3, 4])
        assert result["canonical"] is False
        assert len(result["counterexamples"]) > 0

    def test_decision_trace_exists(self):
        result = greedy_coin_change([1, 2, 5], 8)
        assert len(result["decisions"]) == len([1, 2, 5])
        assert all("reason" in d for d in result["decisions"])
