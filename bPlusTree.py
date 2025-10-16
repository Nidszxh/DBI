from node import Node
from util import validate_entry, log_action


class BPlusTree:
    """B+ Tree implementation for database indexing"""
    
    def __init__(self, order):
        if order < 3:
            raise ValueError("Order must be at least 3")
        
        self.order = order
        self.root = Node(order, leaf=True)
        self._size = 0
        log_action("Initialized B+ Tree with order", order)

    def insert(self, key, value):
        """Insert a key-value pair into the B+ Tree"""
        is_valid, message = validate_entry(key, value)
        if not is_valid:
            raise ValueError(f"Invalid entry: {message}")

        leaf = self.root.find_leaf(key)
        old_size = len(leaf.keys)
        leaf.insert_in_leaf(key, value)
        
        if len(leaf.keys) > old_size:
            self._size += 1
            log_action("Inserted", key)
        else:
            log_action("Updated", key)
        
        if leaf.is_full():
            self._handle_overflow(leaf)

    def _handle_overflow(self, node):
        """Handle node overflow by splitting"""
        new_node, mid_key, new_root = node.split()
        
        if new_root:
            self.root = new_root
            return
        
        parent = node.parent
        parent.insert_in_internal(mid_key, new_node)
        
        if parent.is_full():
            self._handle_overflow(parent)

    def search(self, key):
        """Search for a key in the tree"""
        return self.root.search(key)

    def delete(self, key):
        """Delete a key from the tree"""
        leaf = self.root.find_leaf(key)
        
        if key not in leaf.keys:
            log_action("Delete failed; key not found", key, level="WARNING")
            return False
        
        idx = leaf.keys.index(key)
        leaf.keys.pop(idx)
        leaf.values.pop(idx)
        self._size -= 1
        log_action("Deleted", key)
        
        if leaf != self.root and leaf.is_underflow():
            self._handle_underflow(leaf)
        
        if not self.root.keys and not self.root.leaf and self.root.values:
            self.root = self.root.values[0]
            self.root.parent = None
        
        return True

    def _handle_underflow(self, node):
        """Handle node underflow by borrowing or merging"""
        parent = node.parent
        node_idx = parent.values.index(node)
        min_keys = (self.order + 1) // 2 - 1
        
        # Try borrowing from left sibling
        if node_idx > 0:
            left_sibling = parent.values[node_idx - 1]
            if len(left_sibling.keys) > min_keys:
                node.borrow_from_left(left_sibling, node_idx - 1)
                return
        
        # Try borrowing from right sibling
        if node_idx < len(parent.values) - 1:
            right_sibling = parent.values[node_idx + 1]
            if len(right_sibling.keys) > min_keys:
                node.borrow_from_right(right_sibling, node_idx)
                return
        
        # Merge with sibling
        if node_idx > 0:
            left_sibling = parent.values[node_idx - 1]
            self._merge(left_sibling, node, node_idx - 1)
        else:
            right_sibling = parent.values[node_idx + 1]
            self._merge(node, right_sibling, node_idx)

    def _merge(self, left_node, right_node, parent_key_idx):
        """Merge right node into left node"""
        parent = left_node.parent
        left_node.merge_with_right(right_node, parent_key_idx)
        
        parent.keys.pop(parent_key_idx)
        parent.values.pop(parent_key_idx + 1)
        
        if parent != self.root and parent.is_underflow():
            self._handle_underflow(parent)

    def range_query(self, start_key, end_key):
        """Return all key-value pairs in range [start_key, end_key]"""
        return self.root.range_query(start_key, end_key)

    def get_all(self):
        """Return all key-value pairs in sorted order"""
        result = []
        current = self._get_leftmost_leaf()
        
        while current:
            result.extend(zip(current.keys, current.values))
            current = current.next
        
        return result

    def _get_leftmost_leaf(self):
        """Get the leftmost leaf node"""
        node = self.root
        while not node.leaf:
            node = node.values[0]
        return node

    def clear(self):
        """Clear all data from the tree"""
        self.root = Node(self.order, leaf=True)
        self._size = 0
        log_action("Cleared B+ Tree")

    def get_height(self):
        """Calculate and return the height of the tree"""
        if self.root is None:
            return 0
        
        height = 1
        node = self.root
        while not node.leaf:
            node = node.values[0]
            height += 1
        
        return height

    def validate(self):
        """Validate B+ Tree properties"""
        if self.root is None:
            return True
        
        is_valid = self._validate_node(self.root, None, None)
        log_action("Tree validation", "passed" if is_valid else "failed", 
                   level="INFO" if is_valid else "ERROR")
        return is_valid

    def _validate_node(self, node, min_key, max_key):
        """Recursively validate node properties"""
        if node != self.root:
            min_keys = (self.order + 1) // 2 - 1
            if len(node.keys) < min_keys or len(node.keys) > self.order:
                return False
        
        # Check key ordering
        for i in range(len(node.keys) - 1):
            if node.keys[i] >= node.keys[i + 1]:
                return False
        
        # Check bounds
        if min_key is not None and node.keys and node.keys[0] < min_key:
            return False
        if max_key is not None and node.keys and node.keys[-1] > max_key:
            return False
        
        # Validate children
        if not node.leaf:
            if len(node.values) != len(node.keys) + 1:
                return False
            
            for i, child in enumerate(node.values):
                if child.parent != node:
                    return False
                
                child_min = node.keys[i - 1] if i > 0 else min_key
                child_max = node.keys[i] if i < len(node.keys) else max_key
                
                if not self._validate_node(child, child_min, child_max):
                    return False
        
        return True

    def __len__(self):
        return self._size

    def __contains__(self, key):
        return self.search(key) is not None

    def __getitem__(self, key):
        value = self.search(key)
        if value is None:
            raise KeyError(f"Key {key} not found")
        return value

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __delitem__(self, key):
        if not self.delete(key):
            raise KeyError(f"Key {key} not found")

    def __repr__(self):
        return f"BPlusTree(order={self.order}, size={self._size}, height={self.get_height()})"