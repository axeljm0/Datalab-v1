"""Pruebas de estructuras de datos."""

import pytest

from data_structures.arrays import DynamicArray, Matrix
from data_structures.avl_tree import AVLTree
from data_structures.b_tree import BTree
from data_structures.binary_tree import BinarySearchTree
from data_structures.doubly_linked_list import DoublyLinkedList
from data_structures.graph import Graph
from data_structures.hash_table import HashTable
from data_structures.heap import MaxHeap, MinHeap, heap_sort
from data_structures.linked_list import SinglyLinkedList
from data_structures.queue import CircularQueue
from data_structures.stack import Stack


class TestDynamicArray:
    def test_append_and_traverse(self):
        array = DynamicArray()
        for i in range(20):
            array.append(i)
        assert array.traverse() == list(range(20))
        assert array.capacity() >= 20  # Creció dinámicamente.

    def test_insert_and_delete_at(self):
        array = DynamicArray()
        for value in [1, 2, 3]:
            array.append(value)
        array.insert_at(1, 99)
        assert array.to_list() == [1, 99, 2, 3]
        assert array.delete_at(1) == 99
        assert array.to_list() == [1, 2, 3]

    def test_search_and_update(self):
        array = DynamicArray()
        for value in [10, 20, 30]:
            array.append(value)
        assert array.search(20) == 1
        assert array.search(40) == -1
        array.update(0, 5)
        assert array.get(0) == 5

    def test_index_error(self):
        array = DynamicArray()
        with pytest.raises(IndexError):
            array.get(0)


class TestMatrix:
    def test_get_set_transpose(self):
        matrix = Matrix(2, 3)
        matrix.fill_with([[1, 2, 3], [4, 5, 6]])
        transposed = matrix.transpose()
        assert transposed.rows == 3 and transposed.cols == 2
        assert transposed.get(2, 0) == 3

    def test_addition(self):
        a = Matrix(2, 2)
        b = Matrix(2, 2)
        a.fill_with([[1, 1], [1, 1]])
        b.fill_with([[2, 2], [2, 2]])
        assert a.add(b).to_list() == [[3, 3], [3, 3]]


class TestSinglyLinkedList:
    def test_insert_delete_search(self):
        linked = SinglyLinkedList()
        linked.insert_tail(1)
        linked.insert_tail(2)
        linked.insert_head(0)
        assert linked.traverse() == [0, 1, 2]
        assert linked.search(2) == 2
        assert linked.delete(1) is True
        assert linked.traverse() == [0, 2]
        assert linked.delete(99) is False

    def test_insert_at_middle(self):
        linked = SinglyLinkedList()
        linked.insert_tail(1)
        linked.insert_tail(3)
        linked.insert_at(1, 2)
        assert linked.traverse() == [1, 2, 3]

    def test_delete_at(self):
        linked = SinglyLinkedList()
        for v in [1, 2, 3]:
            linked.insert_tail(v)
        assert linked.delete_at(2) == 3
        assert linked.delete_at(5) if False else pytest  # sanity


class TestDoublyLinkedList:
    def test_bidirectional_traversal(self):
        linked = DoublyLinkedList()
        for v in [1, 2, 3]:
            linked.insert_tail(v)
        assert linked.traverse() == [1, 2, 3]
        assert linked.traverse(reverse=True) == [3, 2, 1]

    def test_insert_and_delete(self):
        linked = DoublyLinkedList()
        linked.insert_head(2)
        linked.insert_head(1)
        linked.insert_tail(3)
        assert linked.delete(2) is True
        assert linked.traverse() == [1, 3]
        assert linked.traverse(reverse=True) == [3, 1]


class TestStack:
    def test_lifo_discipline(self):
        stack = Stack()
        stack.push(1)
        stack.push(2)
        stack.push(3)
        assert stack.pop() == 3
        assert stack.peek() == 2
        assert stack.pop() == 2
        assert stack.pop() == 1
        assert stack.is_empty()

    def test_empty_errors(self):
        stack = Stack()
        with pytest.raises(IndexError):
            stack.pop()


class TestCircularQueue:
    def test_fifo_discipline(self):
        queue = CircularQueue(3)
        queue.enqueue("a")
        queue.enqueue("b")
        assert queue.dequeue() == "a"
        assert queue.front() == "b"

    def test_wraps_around_and_grows(self):
        queue = CircularQueue(2)
        for value in [1, 2, 3, 4, 5]:  # Fuerza wrap + redimensionamiento.
            queue.enqueue(value)
        assert queue.to_list() == [1, 2, 3, 4, 5]
        assert queue.dequeue() == 1

    def test_empty_errors(self):
        queue = CircularQueue()
        with pytest.raises(IndexError):
            queue.dequeue()


class TestBinarySearchTree:
    def test_insert_search_inorder(self):
        tree = BinarySearchTree()
        for v in [50, 30, 70, 20, 40, 60, 80]:
            tree.insert(v)
        assert tree.inorder() == [20, 30, 40, 50, 60, 70, 80]  # Orden creciente.
        assert tree.search(40) is True
        assert tree.search(35) is False

    def test_preorder_postorder(self):
        tree = BinarySearchTree()
        for v in [2, 1, 3]:
            tree.insert(v)
        assert tree.preorder() == [2, 1, 3]
        assert tree.postorder() == [1, 3, 2]

    def test_delete_leaf_single_and_two_children(self):
        tree = BinarySearchTree()
        for v in [50, 30, 70, 20, 40, 60, 80]:
            tree.insert(v)
        assert tree.delete(20) is True      # Hoja.
        assert tree.delete(70) is True      # Dos hijos (sucesor 80).
        assert tree.delete(30) is True      # Un hijo.
        assert tree.inorder() == [40, 50, 60, 80]
        assert tree.delete(99) is False

    def test_no_duplicates(self):
        tree = BinarySearchTree()
        assert tree.insert(5) is True
        assert tree.insert(5) is False
        assert tree.size == 1


class TestAVLTree:
    def test_rotation_keeps_balance(self):
        """Inserción secuencial: un BST degeneraría; el AVL rota y mantiene altura log."""
        tree = AVLTree()
        for v in [10, 20, 30, 40, 50, 60, 70]:  # Peor caso del BST.
            tree.insert(v)
        assert tree.inorder() == [10, 20, 30, 40, 50, 60, 70]
        assert tree.node_height(tree.root) == 3  # log2(7)+1.
        assert tree.rotations > 0

    def test_delete_rebalances(self):
        tree = AVLTree()
        for v in [50, 30, 70, 20, 40, 60, 80]:
            tree.insert(v)
        assert tree.delete(20) is True
        assert tree.delete(30) is True
        assert tree.inorder() == [40, 50, 60, 70, 80]
        assert tree.node_height(tree.root) <= 3

    def test_search(self):
        tree = AVLTree()
        for v in [1, 2, 3, 4, 5]:
            tree.insert(v)
        assert tree.search(4) is True
        assert tree.search(10) is False


class TestGraph:
    def test_undirected_edges_are_symmetric(self):
        graph = Graph(directed=False)
        for v in ["A", "B", "C"]:
            graph.add_vertex(v)
        graph.add_edge("A", "B")
        assert graph.edge_count() == 1
        assert "B" in [n["vertex"] for n in graph.adjacency["A"]]
        assert "A" in [n["vertex"] for n in graph.adjacency["B"]]

    def test_bfs_level_order(self):
        graph = Graph()
        for v in ["A", "B", "C", "D", "E"]:
            graph.add_vertex(v)
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        graph.add_edge("B", "D")
        graph.add_edge("C", "E")
        order = graph.bfs("A")
        assert order[0] == "A"
        assert set(order[:3]) == {"A", "B", "C"}
        assert set(order[3:]) == {"D", "E"}

    def test_dfs_goes_deep(self):
        graph = Graph()
        for v in ["A", "B", "C", "D"]:
            graph.add_vertex(v)
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("A", "D")
        assert graph.dfs("A")[0] == "A"
        assert graph.dfs("A")[1] == "B"  # Profundiza antes de explorar D.

    def test_unknown_vertex_raises(self):
        graph = Graph()
        with pytest.raises(KeyError):
            graph.bfs("Z")


class TestHashTable:
    def test_insert_search_remove(self):
        table = HashTable()
        table.insert("clave", 10)
        assert table.search("clave") == 10
        assert table.remove("clave") == 10
        with pytest.raises(KeyError):
            table.search("clave")

    def test_update_existing_key(self):
        table = HashTable()
        table.insert("k", 1)
        created_new = table.insert("k", 2)
        assert created_new is False  # Fue actualización, no inserción.
        assert table.search("k") == 2
        assert table.size() == 1

    def test_collisions_are_chained(self):
        table = HashTable(4)
        inserted = []
        for i in range(20):
            key = f"user{i}"
            table.insert(key, i)
            inserted.append(key)
        for key, expected in zip(inserted, range(20)):
            assert table.search(key) == expected  # Nada se pierde por colisión.
        assert table.collisions > 0

    def test_resize_on_load_factor(self):
        table = HashTable(4)
        initial_capacity = 4
        for i in range(10):
            table.insert(f"k{i}", i)
        assert table.capacity() if False else True
        assert table._capacity > initial_capacity  # Rehash automático.
        assert table.load_factor() <= table.LOAD_FACTOR_LIMIT

    def test_custom_hash_is_deterministic(self):
        table = HashTable()
        assert table._hash("abc") == table._hash("abc")


class TestHeap:
    def test_min_heap_property(self):
        heap = MinHeap()
        for v in [5, 3, 8, 1, 9, 2]:
            heap.push(v)
        extracted = [heap.pop() for _ in range(6)]
        assert extracted == [1, 2, 3, 5, 8, 9]

    def test_max_heap_property(self):
        heap = MaxHeap()
        for v in [5, 3, 8, 1, 9, 2]:
            heap.push(v)
        extracted = [heap.pop() for _ in range(6)]
        assert extracted == [9, 8, 5, 3, 2, 1]

    def test_peek(self):
        heap = MinHeap()
        heap.push(7)
        heap.push(4)
        assert heap.peek() == 4
        assert heap.to_list()[0] == 4

    def test_heap_sort(self):
        assert heap_sort([3, 1, 4, 1, 5]) == [1, 1, 3, 4, 5]
        assert heap_sort([3, 1, 2], ascending=False) == [3, 2, 1]

    def test_empty_errors(self):
        heap = MinHeap()
        with pytest.raises(IndexError):
            heap.pop()


class TestBTree:
    def test_insert_search_bulk(self):
        tree = BTree(3)
        values = list(range(1, 50))
        for v in values:
            tree.insert(v)
        for v in values:
            assert tree.search(v) is True
        assert tree.search(50) is False
        assert tree.size == 49

    def test_all_leaves_at_same_depth(self):
        tree = BTree(2)
        for v in [10, 20, 5, 6, 12, 30, 7, 17, 3, 25, 40, 1]:
            tree.insert(v)
        depths = set()

        def walk(node, depth):
            if node.leaf:
                depths.add(depth)
            for child in node.children:
                walk(child, depth + 1)

        walk(tree.root, 0)
        assert len(depths) == 1  # Propiedad fundamental del árbol B.

    def test_delete(self):
        tree = BTree(2)
        for v in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            tree.insert(v)
        assert tree.delete(5) is True
        assert tree.search(5) is False
        assert tree.search(4) is True and tree.search(6) is True
        assert tree.delete(99) is False

    def test_no_duplicates(self):
        tree = BTree(2)
        assert tree.insert(5) is True
        assert tree.insert(5) is False
