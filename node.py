import itertools
import bisect

class Node:
    id_iter = itertools.count()

    def __init__(self, order, leaf=False, parent=None):
        # Initialize a node with order, leaf status, and parent reference
        self.id = next(Node.id_iter)  # Unique ID for the node
        self.order = order  # Max keys per node
        self.leaf = leaf  # True if it's a leaf node
        self.parent = parent  # Reference to the parent node
        self.keys = []  # Keys in the node
        self.values = []  # Values for leaf or child pointers for internal nodes
        self.next = None  # Link to the next leaf node
        self.children = [] if not leaf else None  # Child nodes for internal nodes

    def is_full(self):
        # Check if node is at max capacity
        return len(self.keys) >= self.order

    def split(self):
        # Split a full node and return the new node and middle key
        mid_index = self.order // 2  # Dynamically calculate midpoint
        mid_key = self.keys[mid_index]

        # Create the new node with the same order and type
        new_node = Node(self.order, self.leaf, parent=self.parent)
        new_node.keys = self.keys[mid_index + 1:]
        new_node.values = self.values[mid_index + 1:]

        # Keep only the left half in the current node
        self.keys = self.keys[:mid_index]
        self.values = self.values[:mid_index + 1]

        if not self.leaf:
            # Split children for internal nodes
            new_node.children = self.children[mid_index + 1:]
            self.children = self.children[:mid_index + 1]

            # Update parent references for new children
            for child in new_node.children:
                child.parent = new_node
        else:
            # Link the new node in the leaf chain
            new_node.next = self.next
            self.next = new_node

        # Update parent references or create a new root
        if self.parent is None:
            new_root = Node(self.order, leaf=False) 
            new_root.keys = [mid_key]
            new_root.values = [self, new_node]
            self.parent = new_root
            new_node.parent = new_root
            return new_node, mid_key, new_root  # Return new root for tree updates

        return new_node, mid_key, None  # No new root needed if not splitting root

    def insert_in_leaf(self, key, value):
        # Insert a key-value pair in a sorted way for leaf nodes
        idx = bisect.bisect_left(self.keys, key)
        self.keys.insert(idx, key)
        self.values.insert(idx, value)

    def insert_in_internal(self, key, right_child):
        # Insert a key and right child pointer in an internal node
        idx = bisect.bisect_left(self.keys, key)
        self.keys.insert(idx, key)
        self.values.insert(idx + 1, right_child)

    def remove_key(self, key):
        # Remove a key and its corresponding value or child pointer
        if key in self.keys:
            index = self.keys.index(key)
            self.keys.pop(index)
            self.values.pop(index)
        else:
            raise KeyError(f"Key {key} not found in node {self.id}.")
        
        # Rebalance the tree if the node underflows
        if not self.leaf and len(self.keys) < self.order // 2:
            self.rebalance()

    def rebalance(self):
        # Handle rebalancing when a node underflows
        if len(self.keys) < self.order // 2 and self.parent:
            parent = self.parent
            idx = parent.values.index(self)

            # Borrow from a sibling or merge if needed
            if idx > 0 and len(parent.values[idx - 1].keys) > self.order // 2:
                self.borrow_from_sibling(parent.values[idx - 1], parent.keys[idx - 1], is_left_sibling=True)
            elif idx < len(parent.values) - 1 and len(parent.values[idx + 1].keys) > self.order // 2:
                self.borrow_from_sibling(parent.values[idx + 1], parent.keys[idx], is_left_sibling=False)
            else:
                sibling = parent.values[idx - 1] if idx > 0 else parent.values[idx + 1]
                parent_key = parent.keys[idx - 1] if idx > 0 else parent.keys[idx]
                self.merge(sibling, parent_key)
                parent.remove_key(parent_key)

    def borrow_from_sibling(self, sibling, parent_key, is_left_sibling):
        # Borrow a key from a sibling
        if is_left_sibling:
            self.keys.insert(0, parent_key)
            self.values.insert(0, sibling.values.pop(-1))
            sibling_key = sibling.keys.pop(-1)
        else:
            self.keys.append(parent_key)
            self.values.append(sibling.values.pop(0))
            sibling_key = sibling.keys.pop(0)

        # Update the parent's key
        sibling.parent.keys[sibling.parent.keys.index(parent_key)] = sibling_key

    def merge(self, sibling, parent_key):
        # Merge this node with a sibling node
        if self.leaf:
            # Merge leaves
            self.keys.extend(sibling.keys)
            self.values.extend(sibling.values)
            self.next = sibling.next  # Update leaf link
        else:
            # Merge internal nodes with the parent key
            self.keys.append(parent_key)
            self.keys.extend(sibling.keys)
            self.values.extend(sibling.values)
            for child in sibling.children:
                child.parent = self

    def search(self, key):
        # Search for a key in the node and return its value or pointer
        if self.leaf:
            idx = bisect.bisect_left(self.keys, key)
            if idx < len(self.keys) and self.keys[idx] == key:
                return self.values[idx]
            return None
        else:
            for i, k in enumerate(self.keys):
                if key < k:
                    return self.children[i].search(key)
            return self.children[-1].search(key)

    def range_query(self, start_key, end_key):
        # Return all key-value pairs within the range [start_key, end_key]
        result = []
        if self.leaf:
            current = self
            while current:
                for k, v in zip(current.keys, current.values):
                    if start_key <= k <= end_key:
                        result.append((k, v))
                current = current.next  # Traverse leaf links
            return result
        else:
            for i, k in enumerate(self.keys):
                if start_key < k:
                    result.extend(self.children[i].range_query(start_key, end_key))
            result.extend(self.children[-1].range_query(start_key, end_key))
            return result

    def __repr__(self):
        # Return a concise string representation of the node
        return f"Node(ID: {self.id}, Keys: {self.keys}, Leaf: {self.leaf})"
