"""Pruebas de integración de la API REST (blueprints y validaciones)."""

import pytest

from app import create_app


@pytest.fixture()
def client():
    app = create_app("testing")
    app.testing = True
    with app.test_client() as client:
        yield client


class TestSearchAPI:
    def test_linear_success(self, client):
        response = client.post("/api/search/linear",
                               json={"values": [4, 8, 15], "target": 8})
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["found"] is True and data["index"] == 1
        assert data["complexity"]["average"] == "O(n)"

    def test_binary_rejects_unsorted(self, client):
        response = client.post("/api/search/binary",
                               json={"values": [3, 1, 2], "target": 2})
        assert response.status_code == 400
        body = response.get_json()
        assert body["success"] is False
        assert body["data"]["requires_sorted"] is True

    def test_invalid_payload(self, client):
        response = client.post("/api/search/linear", json={"values": []})
        assert response.status_code == 400


class TestSortAPI:
    def test_sort_and_compare(self, client):
        response = client.post("/api/sort/quick",
                               json={"values": [3, 1, 2]})
        data = response.get_json()["data"]
        assert data["sorted"] == [1, 2, 3]
        assert data["info"]["worst"] == "O(n²)"

        response = client.post("/api/sort/compare",
                               json={"values": [5, 2, 9, 1],
                                     "algorithms": ["bubble", "quick"]})
        results = response.get_json()["data"]["results"]
        assert len(results) == 2
        assert all(r["correct"] for r in results)

    def test_unknown_algorithm(self, client):
        response = client.post("/api/sort/merge", json={"values": [1]})
        assert response.status_code == 404


class TestStructuresAPI:
    def test_stack_lifecycle(self, client):
        create = client.post("/api/structures", json={"type": "stack"})
        stack_id = create.get_json()["data"]["id"]
        client.post(f"/api/structures/{stack_id}/op",
                    json={"operation": "push", "value": 1})
        client.post(f"/api/structures/{stack_id}/op",
                    json={"operation": "push", "value": 2})
        result = client.post(f"/api/structures/{stack_id}/op",
                             json={"operation": "pop"})
        assert result.get_json()["data"]["result"]["removed"] == 2

    def test_bst_operations(self, client):
        create = client.post("/api/structures", json={"type": "bst"})
        tree_id = create.get_json()["data"]["id"]
        for value in [50, 30, 70]:
            client.post(f"/api/structures/{tree_id}/op",
                        json={"operation": "insert", "value": value})
        result = client.post(f"/api/structures/{tree_id}/op",
                             json={"operation": "inorder"})
        assert result.get_json()["data"]["result"]["order"] == [30, 50, 70]

    def test_hash_table_load_factor(self, client):
        create = client.post("/api/structures",
                             json={"type": "hash_table", "options": {"capacity": 4}})
        table_id = create.get_json()["data"]["id"]
        for i in range(10):
            client.post(f"/api/structures/{table_id}/op",
                        json={"operation": "insert", "key": f"k{i}", "value": i})
        snapshot = client.get(f"/api/structures/{table_id}").get_json()["data"]
        assert snapshot["size"] == 10
        assert snapshot["capacity"] > 4  # Redimensionó.

    def test_missing_instance_404(self, client):
        response = client.get("/api/structures/nope")
        assert response.status_code == 404


class TestOptimizationAPI:
    def test_fibonacci(self, client):
        response = client.post("/api/dp/fibonacci", json={"n": 10})
        data = response.get_json()["data"]
        assert data["dynamic"]["value"] == 55

    def test_knapsack(self, client):
        response = client.post("/api/dp/knapsack",
                               json={"weights": [2, 3, 4], "values": [3, 4, 5],
                                     "capacity": 5})
        assert response.get_json()["data"]["best_value"] == 7

    def test_greedy_coins_reports_optimality(self, client):
        response = client.post("/api/greedy/coins",
                               json={"denominations": [1, 3, 4], "amount": 6})
        data = response.get_json()["data"]
        assert data["optimal"] is False  # Sistema no canónico detectado.


class TestBenchmarksAndDatasets:
    def test_sort_benchmark_runs(self, client):
        response = client.post("/api/benchmarks/sort",
                               json={"algorithms": ["quick"], "sizes": [100]})
        results = response.get_json()["data"]["results"]
        assert results[0]["viable"] is True
        assert results[0]["time_ms"] > 0

    def test_dataset_workflow(self, client):
        response = client.post("/api/datasets/generate",
                               json={"name": "demo", "count": 50, "seed": 1})
        assert response.status_code == 200
        preview = client.get("/api/datasets/demo")
        assert preview.get_json()["data"]["total"] == 50
        stats = client.get("/api/datasets/demo/stats")
        assert stats.get_json()["success"] is True
        filtered = client.post("/api/datasets/demo/filter",
                               json={"column": "age", "operator": ">",
                                     "value": "40"})
        assert filtered.get_json()["success"] is True

    def test_dashboard_stats(self, client):
        response = client.get("/api/dashboard/stats")
        assert response.get_json()["data"]["laboratories"] == 11
