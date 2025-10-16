import itertools
import bisect

class Node:
    """B+ Tree Node implementation"""
    id_iter = itertools.count()

    def __init__(self, order, leaf=False, parent=None):
        self.id = next(Node.id_iter)
        self.order = order
        self.leaf = leaf
        self.parent = parent
        self.keys = []
        self.values = []  # Values for leaves, child pointers for internal
        self.next = None  # Next leaf pointer

    def is_full(self):
        """Check if node has reached maximum capacity"""
        return len(self.keys) >= self.order

    def is_underflow(self):
        """Check if node has too few keys"""
        min_keys = (self.order + 1) // 2 - 1
        return len(self.keys) < min_keys

    def split(self):
        """Split a full node into two nodes"""
        mid_index = (self.order + 1) // 2
        new_node = Node(self.order, self.leaf, parent=self.parent)
        
        if self.leaf:
            mid_key = self.keys[mid_index]
            new_node.keys = self.keys[mid_index:]
            new_node.values = self.values[mid_index:]
            self.keys = self.keys[:mid_index]
            self.values = self.values[:mid_index]
            new_node.next = self.next
            self.next = new_node
        else:
            mid_key = self.keys[mid_index]
            new_node.keys = self.keys[mid_index + 1:]
            new_node.values = self.values[mid_index + 1:]
            self.keys = self.keys[:mid_index]
            self.values = self.values[:mid_index + 1]
            
            for child in new_node.values:
                child.parent = new_node

        if self.parent is None:
            new_root = Node(self.order, leaf=False)
            new_root.keys = [mid_key]
            new_root.values = [self, new_node]
            self.parent = new_root
            new_node.parent = new_root
            return new_node, mid_key, new_root

        return new_node, mid_key, None

    def insert_in_leaf(self, key, value):
        """Insert key-value pair in sorted order"""
        idx = bisect.bisect_left(self.keys, key)
        if idx < len(self.keys) and self.keys[idx] == key:
            self.values[idx] = value
        else:
            self.keys.insert(idx, key)
            self.values.insert(idx, value)

    def insert_in_internal(self, key, right_child):
        """Insert key and right child pointer"""
        idx = bisect.bisect_left(self.keys, key)
        self.keys.insert(idx, key)
        self.values.insert(idx + 1, right_child)
        right_child.parent = self

    def search(self, key):
        """Search for a key in the tree"""
        if self.leaf:
            idx = bisect.bisect_left(self.keys, key)
            if idx < len(self.keys) and self.keys[idx] == key:
                return self.values[idx]
            return None
        idx = bisect.bisect_right(self.keys, key)
        return self.values[idx].search(key)

    def find_leaf(self, key):
        """Find the leaf node where key should be located"""
        if self.leaf:
            return self
        idx = bisect.bisect_right(self.keys, key)
        return self.values[idx].find_leaf(key)

    def range_query(self, start_key, end_key):
        """Return all key-value pairs in range [start_key, end_key]"""
        result = []
        start_leaf = self.find_leaf(start_key) if not self.leaf else self
        
        current = start_leaf
        while current:
            for k, v in zip(current.keys, current.values):
                if k > end_key:
                    return result
                if k >= start_key:
                    result.append((k, v))
            current = current.next
        
        return result

    def get_sibling(self, left=True):
        """Get left or right sibling node"""
        if not self.parent:
            return None, None
        
        idx = self.parent.values.index(self)
        
        if left and idx > 0:
            return self.parent.values[idx - 1], idx - 1
        elif not left and idx < len(self.parent.values) - 1:
            return self.parent.values[idx + 1], idx
        
        return None, None

    def borrow_from_left(self, left_sibling, parent_key_idx):
        """Borrow a key from left sibling"""
        if self.leaf:
            self.keys.insert(0, left_sibling.keys.pop())
            self.values.insert(0, left_sibling.values.pop())
            self.parent.keys[parent_key_idx] = self.keys[0]
        else:
            self.keys.insert(0, self.parent.keys[parent_key_idx])
            self.values.insert(0, left_sibling.values.pop())
            self.values[0].parent = self
            self.parent.keys[parent_key_idx] = left_sibling.keys.pop()

    def borrow_from_right(self, right_sibling, parent_key_idx):
        """Borrow a key from right sibling"""
        if self.leaf:
            self.keys.append(right_sibling.keys.pop(0))
            self.values.append(right_sibling.values.pop(0))
            self.parent.keys[parent_key_idx] = right_sibling.keys[0]
        else:
            self.keys.append(self.parent.keys[parent_key_idx])
            self.values.append(right_sibling.values.pop(0))
            self.values[-1].parent = self
            self.parent.keys[parent_key_idx] = right_sibling.keys.pop(0)

    def merge_with_right(self, right_sibling, parent_key_idx):
        """Merge this node with right sibling"""
        if self.leaf:
            self.keys.extend(right_sibling.keys)
            self.values.extend(right_sibling.values)
            self.next = right_sibling.next
        else:
            self.keys.append(self.parent.keys[parent_key_idx])
            self.keys.extend(right_sibling.keys)
            self.values.extend(right_sibling.values)
            
            for child in right_sibling.values:
                child.parent = self

    def __repr__(self):
        return f"Node(ID:{self.id}, Keys:{self.keys}, Leaf:{self.leaf})"