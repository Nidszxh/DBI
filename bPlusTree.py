import logging
from node import Node
from util import compare_keys, validate_entry, log_action

class BplusTree:
    def __init__(self, order):
        # Initialize the B+ Tree
        self.root = Node(True, order)  # Root node is initially a leaf
        self.order = order  # Max number of children per node
        self.height = 1  # Initial tree height
        logging.basicConfig(level=logging.INFO)  # Configure logging
        log_action("Initialized B+ Tree with order", order)

    def insert(self, key, value):
        # Insert a key-value pair into the B+ Tree
        is_valid, message = validate_entry(key, value)
        if not is_valid:
            logging.error(f"Invalid key-value pair: {message}")
            raise ValueError("Invalid key-value pair.")

        if len(self.root.keys) == (2 * self.order) - 1:  # Root is full
            new_root = Node(False, self.order)
            new_root.children.insert(0, self.root)
            self.split_child(new_root, 0)
            self.root = new_root
            self.height += 1
            log_action("Root node split; tree height increased.")

        self._insert_non_full(self.root, key, value)

    def _insert_non_full(self, node, key, value):
        # Helper function to insert into a non-full node
        i = len(node.keys) - 1
        if node.leaf:
            while i >= 0 and compare_keys(key, node.keys[i][0]) < 0:
                i -= 1
            if i >= 0 and compare_keys(key, node.keys[i][0]) == 0:
                # Handle duplicates or equal keys if necessary (optional behavior)
                logging.warning(f"Key {key} already exists. Overwriting value.")
                node.keys[i] = (key, value)
            else:
                node.keys.insert(i + 1, (key, value))
        else:
            while i >= 0 and compare_keys(key, node.keys[i]) < 0:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.order) - 1:
                self.split_child(node, i)
                if compare_keys(key, node.keys[i]) > 0:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def split_child(self, parent, index):
        # Split a child node of a given parent at a specified index
        full_child = parent.children[index]
        new_node = Node(full_child.leaf, self.order)
        mid = self.order - 1

        parent.keys.insert(index, full_child.keys[mid][0] if full_child.leaf else full_child.keys[mid])
        new_node.keys = full_child.keys[mid + 1:]
        full_child.keys = full_child.keys[:mid]

        if not full_child.leaf:
            new_node.children = full_child.children[self.order:]
            full_child.children = full_child.children[:self.order]
        else:
            new_node.next = full_child.next
            full_child.next = new_node

        parent.children.insert(index + 1, new_node)
        log_action("Split child node at index", index)

    def search(self, key):
        # Search for a key in the B+ Tree
        result = self._search(self.root, key)
        if result is None:
            log_action("Search failed; key not found", key)
        else:
            log_action("Search successful; found key", key)
        return result

    def _search(self, node, key):
        # Helper function for searching within a node
        i = 0
        while i < len(node.keys) and compare_keys(key, node.keys[i][0] if node.leaf else node.keys[i]) > 0:
            i += 1

        if node.leaf:
            return next((v for k, v in node.keys if k == key), None)
        return self._search(node.children[i], key)

    def delete(self, key):
        # Delete a key from the B+ Tree
        self._delete(self.root, key)
        if not self.root.keys and not self.root.leaf:
            self.root = self.root.children[0]
            self.height -= 1
            logging.info("Reduced tree height after root collapse.")

    def _delete(self, node, key):
        # Helper function for deletion
        i = 0
        while i < len(node.keys) and compare_keys(key, node.keys[i][0] if node.leaf else node.keys[i]) > 0:
            i += 1

        if node.leaf:
            if i < len(node.keys) and node.keys[i][0] == key:
                node.keys.pop(i)
                log_action("Deleted key", key)
            else:
                logging.warning(f"Key {key} not found in leaf.")
        else:
            if i < len(node.keys) and node.keys[i] == key:
                self._delete_internal_node(node, i)
            else:
                self._delete(node.children[i], key)

    def _delete_internal_node(self, node, index):
        # Delete a key from an internal node
        if len(node.children[index].keys) >= self.order:
            predecessor = self._get_predecessor(node, index)
            node.keys[index] = predecessor
            self._delete(node.children[index], predecessor)
        elif len(node.children[index + 1].keys) >= self.order:
            successor = self._get_successor(node, index)
            node.keys[index] = successor
            self._delete(node.children[index + 1], successor)
        else:
            self._merge_children(node, index)
            self._delete(node.children[index], node.keys[index])

    def _get_predecessor(self, node, index):
        # Get predecessor key
        curr = node.children[index]
        while not curr.leaf:
            curr = curr.children[-1]
        return curr.keys[-1][0]

    def _get_successor(self, node, index):
        # Get successor key
        curr = node.children[index + 1]
        while not curr.leaf:
            curr = curr.children[0]
        return curr.keys[0][0]

    def _merge_children(self, node, index):
        # Merge two child nodes
        left_child = node.children[index]
        right_child = node.children[index + 1]

        if not left_child.leaf:
            left_child.keys.append(node.keys[index])
        left_child.keys.extend(right_child.keys)
        left_child.children.extend(right_child.children)

        node.keys.pop(index)
        node.children.pop(index + 1)
        log_action("Merged children at index", index)

    def get_sorted_data(self):
        # Retrieve sorted data from the B+ Tree
        sorted_data = []
        self._in_order_traversal(self.root, sorted_data)
        return sorted_data

    def _in_order_traversal(self, node, sorted_data):
        # Optimized in-order traversal
        if node.leaf:
            current = node
            while current:
                sorted_data.extend(current.keys)
                current = current.next
        else:
            for i in range(len(node.children)):
                self._in_order_traversal(node.children[i], sorted_data)
                if i < len(node.keys):
                    sorted_data.append((node.keys[i], ""))

    def get_tree_structure(self):
        # Retrieve the structure of the B+ Tree
        structure = []
        self._print_tree(self.root, 0, structure)
        return "\n".join(structure)

    def _print_tree(self, node, level, structure):
        # Print the tree level by level
        if node.leaf:
            structure.append(f"Level {level}: Leaf -> {node.keys}")
        else:
            structure.append(f"Level {level}: Internal -> {node.keys}")
            for child in node.children:
                self._print_tree(child, level + 1, structure)

