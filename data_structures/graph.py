"""Grafos dirigidos y no dirigidos con listas de adyacencia propias.

Los recorridos BFS y DFS están implementados sobre la pila y la cola
propias del proyecto, para evidenciar la relación entre estructuras
lineales y algoritmos sobre grafos.
"""

from __future__ import annotations

from typing import Any, Dict, List

from data_structures.queue import CircularQueue
from data_structures.stack import Stack


class GraphError(KeyError):
    """Operación sobre un vértice inexistente."""


class Graph:
    """Grafo con listas de adyacencia y pesos opcionales. O(V+E) de almacenamiento."""

    def __init__(self, directed: bool = False) -> None:
        self.directed = directed
        self.adjacency: Dict[Any, List[dict]] = {}

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------
    def add_vertex(self, vertex: Any) -> bool:
        """Agrega un vértice aislado. O(1)."""
        if vertex in self.adjacency:
            return False
        self.adjacency[vertex] = []
        return True

    def add_edge(self, source, target, weight: float = 1) -> bool:
        """Agrega una arista; crea los vértices si no existen. O(1)."""
        if source not in self.adjacency or target not in self.adjacency:
            raise GraphError("Los vértices de la arista deben existir en el grafo")
        if any(n["vertex"] == target for n in self.adjacency[source]):
            return False  # Arista duplicada.
        self.adjacency[source].append({"vertex": target, "weight": weight})
        if not self.directed:
            self.adjacency[target].append({"vertex": source, "weight": weight})
        return True

    def remove_edge(self, source, target) -> bool:
        if source not in self.adjacency:
            raise GraphError(f"Vértice {source} no existe")
        before = len(self.adjacency[source])
        self.adjacency[source] = [n for n in self.adjacency[source] if n["vertex"] != target]
        removed = len(self.adjacency[source]) != before
        if not self.directed and removed:
            self.adjacency[target] = [n for n in self.adjacency[target] if n["vertex"] != source]
        return removed

    def remove_vertex(self, vertex) -> bool:
        """Elimina un vértice y todas sus aristas incidentes. O(V+E)."""
        if vertex not in self.adjacency:
            return False
        for other in self.adjacency:
            self.adjacency[other] = [n for n in self.adjacency[other] if n["vertex"] != vertex]
        del self.adjacency[vertex]
        return True

    def order(self) -> int:
        return len(self.adjacency)

    def edge_count(self) -> int:
        total = sum(len(n) for n in self.adjacency.values())
        return total if self.directed else total // 2

    # ------------------------------------------------------------------
    # Recorridos
    # ------------------------------------------------------------------
    def bfs(self, start) -> list:
        """Recorrido por niveles usando la cola propia. O(V+E)."""
        if start not in self.adjacency:
            raise GraphError(f"Vértice {start} no existe")
        visited, order, frontier = {start}, [start], CircularQueue()
        frontier.enqueue(start)
        while not frontier.is_empty():
            vertex = frontier.dequeue()
            for neighbor in self.adjacency[vertex]:
                if neighbor["vertex"] not in visited:
                    visited.add(neighbor["vertex"])
                    order.append(neighbor["vertex"])
                    frontier.enqueue(neighbor["vertex"])
        return order

    def dfs(self, start) -> list:
        """Recorrido en profundidad usando la pila propia. O(V+E)."""
        if start not in self.adjacency:
            raise GraphError(f"Vértice {start} no existe")
        visited, order, pending = set(), [], Stack()
        pending.push(start)
        while not pending.is_empty():
            vertex = pending.pop()
            if vertex in visited:
                continue
            visited.add(vertex)
            order.append(vertex)
            # Empujar vecinos en orden inverso para visitar alfabéticamente.
            neighbors = [n["vertex"] for n in self.adjacency[vertex]]
            for neighbor in reversed(neighbors):
                if neighbor not in visited:
                    pending.push(neighbor)
        return order

    # ------------------------------------------------------------------
    # Serialización
    # ------------------------------------------------------------------
    def snapshot(self) -> dict:
        """Estado serializable para el frontend (grafo en disposición circular)."""
        vertices = list(self.adjacency.keys())
        edges = []
        seen = set()
        for source, neighbors in self.adjacency.items():
            for neighbor in neighbors:
                target = neighbor["vertex"]
                key = (target, source) if not self.directed else (source, target)
                if key in seen:
                    continue
                seen.add((source, target))
                edges.append({"source": source, "target": target,
                              "weight": neighbor["weight"]})
        return {"kind": "graph", "directed": self.directed, "vertices": vertices,
                "edges": edges, "adjacency": {str(v): [n["vertex"] for n in ns]
                                              for v, ns in self.adjacency.items()}}
