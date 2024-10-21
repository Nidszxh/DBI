from node import Node

class BplusTree:
    def __init__(self, order=3):
          #Initialize the B+ Tree with a given order.
        self.root = Node(order)
        self.order = order

    def search(self, key):
        """Search for the correct leaf node where the key should be."""
        current_node = self.root
        # Traverse down until we hit a leaf node
        while not current_node.is_leaf:
            i = 0
            # Find the correct child to go down
            while i < len(current_node.keys) and key >= current_node.keys[i]:
                i += 1
            current_node = current_node.values[i]  # Move to the child node
        return current_node  # Return the leaf node

    def insert(self, key, value):
        """Insert a key-value pair into the B+ tree."""
        leaf_node = self.search(key)
        leaf_node.insert_in_leaf(key, value)  # Insert the key-value pair in the leaf

        # Check if the leaf node is full and needs to be split
        if leaf_node.is_full():
            self.split_child(self.root, leaf_node)

    def split_child(self, parent, child):
        """Split a full child node and promote the middle key to the parent."""
        new_node, mid_key = child.split()  # Split the child node

        # If splitting the root, create a new root
        if parent == self.root and len(parent.keys) == 0:
            new_root = Node(self.order, is_leaf=False)
            new_root.keys = [mid_key]  # The middle key goes to the new root
            new_root.values = [child, new_node]  # Update children of the new root
            self.root = new_root  # Update the tree's root
        else:
            parent = self.find_parent(self.root, child)  # Find the parent of the node
            self.insert_in_parent(parent, mid_key, new_node)

    def insert_in_parent(self, parent, key, new_node):
        """Insert a key and new node into the parent after a split."""
        i = 0
        while i < len(parent.keys) and key > parent.keys[i]:
            i += 1
        parent.keys.insert(i, key)
        parent.values.insert(i + 1, new_node)

        # Check if the parent needs splitting
        if parent.is_full():
            self.split_child(self.find_parent(self.root, parent), parent)

    def delete(self, key):
        """Delete a key from the tree."""
        leaf_node = self.search(key)

        if key in leaf_node.keys:
            index = leaf_node.keys.index(key)
            leaf_node.keys.pop(index)
            leaf_node.values.pop(index)

            # After deletion, ensure the tree remains balanced
            if len(leaf_node.keys) < (self.order - 1) // 2:
                self.delete_entry(leaf_node, key)

    def delete_entry(self, node, key):
        """Handle underflow after deletion and rebalance the tree."""
        if node == self.root:
            # If the root is empty, make the first child the new root
            if len(self.root.keys) == 0 and not self.root.is_leaf:
                self.root = self.root.values[0]
            return

        # Rebalance by borrowing or merging nodes
        if len(node.keys) < (self.order - 1) // 2:
            parent = self.find_parent(self.root, node)
            idx = parent.keys.index(node)

            # Borrow from the left or right sibling
            if idx > 0:  # Left sibling
                self.borrow_from_left(node, parent, parent.keys[idx - 1], idx)
            else:  # Right sibling
                self.borrow_from_right(node, parent, parent.keys[idx + 1], idx)

    def borrow_from_left(self, node, parent, left_sibling, idx):
        """Borrow a key from the left sibling."""
        node.values.insert(0, parent.values[idx - 1])
        node.keys.insert(0, left_sibling.keys.pop(-1))
        parent.values[idx - 1] = left_sibling.values.pop(-1)

    def borrow_from_right(self, node, parent, right_sibling, idx):
        """Borrow a key from the right sibling."""
        node.values.append(parent.values[idx])
        node.keys.append(right_sibling.keys.pop(0))
        parent.values[idx] = right_sibling.values.pop(0)

    def find_parent(self, current_node, child_node):
        """Find the parent of a given node in the tree."""
        if current_node.is_leaf or current_node.keys[0].is_leaf:
            return None  # No parent for the root or direct children

        for i, key in enumerate(current_node.keys):
            if key == child_node or (key.is_leaf and key.next == child_node):
                return current_node
            elif not key.is_leaf:
                parent = self.find_parent(key, child_node)
                if parent:
                    return parent
        return None

    # Traversal Methods
    def print_tree(self):
        """Print the tree level by level for easy visualization."""
        if self.root is None:
            print("The tree is empty.")
            return
        
        current_level = [self.root]
        while current_level:
            next_level = []
            for node in current_level:
                if node.is_leaf:
                    print(f"Leaf Node: {node.keys}")
                else:
                    print(f"Internal Node: {node.keys}")
                next_level.extend(node.values)
            current_level = [child for child in next_level if child]

    def print_leaf_nodes(self):
        """Print all leaf nodes, useful for seeing the linked leaf structure."""
        current = self.root
        while not current.is_leaf:
            current = current.values[0]  # Move to the first leaf

        # Traverse through the linked list of leaves
        while current is not None:
            print(f"Leaf Node: {current.keys}")
            current = current.next

    # Debugging utility
    def traverse(self, node=None, level=0):
        """Recursively traverse the tree and print nodes at each level."""
        if node is None:
            node = self.root

        if node.is_leaf:
            print("  " * level + f"Leaf: {node.keys}")
        else:
            print("  " * level + f"Internal: {node.keys}")
            for child in node.values:
                self.traverse(child, level + 1)
