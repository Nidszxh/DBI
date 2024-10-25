from node import Node
class BplusTree:
    def __init__(self, order):
        self.root = Node(True,order)
        self.order = order
        
    def insert(self, key, value):
        root = self.root
        if len(root.keys) == (2 * self.order) - 1:
            temp = Node(self.order)
            self.root = temp
            temp.child.insert(0, root)
            self.split_child(temp, 0)
            self.insert_non_full(temp, key, value)
        else:
            self.insert_non_full(root, key, value)

    def insert_non_full(self, x, key, value):
        i = len(x.keys) - 1
        if x.leaf:
            while i >= 0 and key < self._get_key(x.keys[i]):
                i -= 1
            x.keys.insert(i + 1, (key, value))
        else:
            while i >= 0 and key < self._get_key(x.keys[i]):
                i -= 1
            i += 1
            if len(x.child[i].keys) == (2 * self.order) - 1:
                self.split_child(x, i)
                if key > self._get_key(x.keys[i]):
                    i += 1
            self.insert_non_full(x.child[i], key, value)

    def _get_key(self, item):
        """Helper method to get key from either a tuple or a single value"""
        return item[0] if isinstance(item, tuple) else item

    def split_child(self, x, i):
        order = self.order
        y = x.child[i]
        z = Node(y.leaf,self.order)
        
        if y.leaf:
            mid = order - 1
            x.keys.insert(i, y.keys[mid])
            z.keys = y.keys[mid:]
            y.keys = y.keys[:mid]
            z.next = y.next
            y.next = z
        else:
            mid = order - 1
            x.keys.insert(i, y.keys[mid])
            z.keys = y.keys[mid + 1:]
            y.keys = y.keys[:mid]
            if len(y.child) > 0:
                z.child = y.child[order:]
                y.child = y.child[:order]
        
        x.child.insert(i + 1, z)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        i = 0
        if node.leaf:
            for k, v in node.keys:
                if k == key:
                    return v
            return None
        
        while i < len(node.keys) and key > self._get_key(node.keys[i]):
            i += 1
        if i < len(node.child):
            return self._search(node.child[i], key)
        return None

    def get_sorted_data(self):
        result = []
        node = self.root
        # Find the leftmost leaf
        while not node.leaf and node.child:
            node = node.child[0]
        
        # Traverse through all leaf nodes
        while node:
            result.extend(node.keys)
            node = node.next
            
        return sorted(result, key=lambda x: x[0])
    
    
    def to_dict(self):
        """Convert the B+ tree structure to a dictionary for visualization."""
        return self.node_to_dict(self.root)
    
    def node_to_dict(self, node):
        """Helper function to convert a node to a dictionary."""
        node_dict = {'keys': node.keys}
        if node.leaf:
            node_dict['values'] = node.values
        else:
            node_dict['children'] = [self.node_to_dict(child) for child in node.children]

        return node_dict