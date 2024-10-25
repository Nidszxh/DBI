import itertools
class Node:
    # ID iterator to assign unique IDs to each node
    id_iter = itertools.count()
    
    def __init__(self, order, leaf=False, parent = None):
        self.id = next(Node.id_iter)     # Assign unique ID to each node
        self.order = order               # Maximum keys a node can hold
        self.leaf = leaf
        self.keys = []
        self.values = []                 # Holds the values (records or child nodes)
        self.next = None                 # For leaf node linkin
        self.parent = parent             # Pointer to the parent node (for easier traversal)
        self.write_id_to_file()
        self.child = []
        self.children = [] if not leaf else None
    
    def write_id_to_file(self):
        """Write the node's unique ID to 'id.txt' for tracking."""
        with open('id.txt', 'a') as id_file:
            id_file.write(f'{self.id} ')

    def is_full(self):
        """Check if the node is full (i.e., requires a split)."""
        return len(self.keys) >= self.order

    def split(self):
        """Split a full node into two and return the new node and its dividing key."""
        mid_index = len(self.keys) // 2
        mid_key = self.keys[mid_index]

        # Create a new node of the same type
        new_node = Node(self.order, self.leaf, parent=self.parent)
        new_node.keys = self.keys[mid_index + 1:]      # Right half goes to the new node
        new_node.values = self.values[mid_index + 1:]  # Corresponding values

        # Trim the current node to hold only the left half
        self.keys = self.keys[:mid_index]
        self.values = self.values[:mid_index + 1]      # One extra value for internal nodes

        # Maintain linked list in leaf nodes
        if self.leaf:
            new_node.next = self.next
            self.next = new_node

        return new_node, mid_key

    def insert_in_leaf(self, key, value):
        """Insert a key-value pair into a leaf node."""
        if not self.keys:  # If leaf is empty, insert directly
            self.keys.append(key)
            self.values.append(value)
            return
        
        # Find the correct position to insert the key
        for i, item in enumerate(self.keys):
            if key < item:
                self.keys.insert(i, key)
                self.values.insert(i, value)
                return
        
        # If key is greater than all existing keys, append to the end
        self.keys.append(key)
        self.values.append(value)

    def insert_in_internal(self, key, left_child, right_child):
        """Insert a key and child pointers into an internal node."""
        # Find the correct position to insert the key
        for i, item in enumerate(self.keys):
            if key < item:
                self.keys.insert(i, key)
                self.values.insert(i + 1, right_child)  # Insert right child after key
                return

        # If key is larger than all existing keys, append to the end
        self.keys.append(key)
        self.values.append(right_child)

    def remove_key(self, key):
        """Remove a key from the node."""
        if key in self.keys:
            index = self.keys.index(key)
            self.keys.pop(index)
            self.values.pop(index)
    
    def merge(self, sibling, parent_key):
        """Merge this node with a sibling node."""
        if self.leaf:
            self.keys.extend(sibling.keys)
            self.values.extend(sibling.values)
            self.next = sibling.next  # Maintain leaf linkage
        else:
            self.keys.append(parent_key)  # Add the dividing key from the parent
            self.keys.extend(sibling.keys)
            self.values.extend(sibling.values)
    
    def rebalance(self):
        """Handle rebalancing when necessary (e.g., after deletion)."""
        if len(self.keys) < self.order // 2:
            # Rebalancing logic will go here (based on parent/sibling relationships)
            pass

    def bulk_insert(self, key_value_pairs):
        """Insert multiple key-value pairs in one go."""
        for key, value in key_value_pairs:
            if self.leaf:
                self.insert_in_leaf(key, value)
            else:
                # Insert into internal nodes as necessary
                pass