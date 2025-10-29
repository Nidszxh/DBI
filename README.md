# B+ Tree Data Structure for Efficient Database Indexing

This library implements a widely used data structure in database systems to efficiently index and retrieve data: the **B+ Tree**. It provides a Python-specific, modular implementation that is easy to understand, making it perfect as a learning exercise or for further development.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Features

### Core Operations
- **Insertion** - Adds new elements into the tree, preserving its balanced structure
- **Search** - Quickly locates elements with minimal I/O operations, ensuring fast data access
- **Deletion** - Removes elements while maintaining tree balance through merging and borrowing
- **Range Queries** - Efficiently retrieves all keys within a specified range using leaf node linking
- **Tree Structure** - Implements leaf and non-leaf nodes, providing an efficient hierarchical layout

### Advanced Features
-  **Persistent Storage** - Automatic disk persistence with crash recovery
-  **Tree Validation** - Built-in validation for B+ tree properties
-  **Statistics** - Tree height, node count, and performance metrics
-  **Backup & Restore** - CSV and JSON export/import capabilities
-  **Batch Operations** - Efficient bulk insertions
-  **Dictionary Interface** - Pythonic `db[key]` syntax

## Project Structure

```
DBI/
├── node.py           # B+ tree node implementation
├── bplustree.py      # Core B+ tree logic
├── database.py       # Database wrapper with utilities
├── persistence.py    # Persistent storage implementation
├── util.py           # Helper functions (logging, I/O, statistics)
├── main.py           # Comprehensive test suite
└── README.md         # This file
```

## How It Works

The B+ Tree is a self-balancing tree data structure that maintains sorted data and allows search, sequential access, insertion, and deletion operations in logarithmic time. It is frequently used in database systems for indexing due to its ability to store multiple keys in a single node, reducing disk I/O.

### Key Properties

1. **Balanced Tree** - All leaf nodes are at the same level
2. **High Fanout** - Each node can store multiple keys (reduces tree height)
3. **Sorted Keys** - Keys are maintained in sorted order within nodes
4. **Leaf Linking** - Leaf nodes are linked for efficient sequential access
5. **Separation of Data** - Internal nodes guide searches, leaves store actual data

## Get Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Nidszxh/DBI.git
   cd DBI
   ```

2. Run the test suite:
   ```bash
   python main.py
   ```

No external dependencies required - uses Python standard library only!

### Basic Usage

```python
from database import Database

# Create a database with order 4 (max 4 keys per node)
db = Database(order=4)

# Insert key-value pairs
db.insert(10, "value_10")
db.insert(20, "value_20")
db.insert(5, "value_5")

# Search for a key
result = db.search(10)  # Returns: "value_10"

# Dictionary-like interface
db[15] = "value_15"
print(db[15])  # "value_15"
print(15 in db)  # True

# Delete a key
db.delete(10)

# Range queries
results = db.range_search(5, 20)  # Returns all keys in [5, 20]

# Get all data (sorted)
all_data = db.get_all()
```

### Persistent Storage

```python
from persistence import PersistentDatabase

# Data automatically saved to disk
with PersistentDatabase("mydata.db", order=4) as db:
    db.insert(1, "persistent_value")
    db.insert(2, "another_value")
    # Automatically saved on exit

# Data survives program restarts
with PersistentDatabase("mydata.db", order=4) as db:
    print(db[1])  # "persistent_value"
```

### Backup & Restore

```python
# Backup to CSV
db.backup("backup.csv")

# Restore from CSV
new_db = Database(order=4)
new_db.restore("backup.csv")

# Export to JSON
db.export_json("data.json")

# Import from JSON
db.import_json("data.json")
```

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Insert    | O(log n)       | O(1)            |
| Search    | O(log n)       | O(1)            |
| Delete    | O(log n)       | O(1)            |
| Range Query | O(log n + k) | O(k)            |
| Traversal | O(n)           | O(1)            |

Where:
- `n` = number of keys in the tree
- `k` = number of keys in the range query result

## Applications

### Database Indexing
Efficiently handles database queries by serving as an indexing mechanism. The B+ Tree structure minimizes disk I/O operations, making it ideal for large datasets that don't fit in memory.

### Storage Systems
Optimizes data retrieval processes in file systems and key-value stores. Used in production systems like:
- PostgreSQL (primary index structure)
- MySQL InnoDB (clustered indexes)
- SQLite (index tables)
- File systems (HFS+, Btrfs)

### Educational Use
Serves as a practical example for understanding tree-based data structures in academic settings. The modular implementation makes it easy to:
- Visualize tree operations
- Understand balancing algorithms
- Study database indexing concepts
- Experiment with different node orders

## API Reference

### Database Class

#### Constructor
```python
Database(order: int)
```
Creates a new database with specified order (minimum 3).

#### Methods

**Insert/Update/Delete**
- `insert(key, value)` - Insert or update a key-value pair
- `delete(key)` - Delete a key from the database
- `batch_insert(entries)` - Insert multiple entries at once

**Search**
- `search(key)` - Search for a single key
- `range_search(lower, upper)` - Search within a range
- `get_all()` - Get all entries in sorted order

**I/O Operations**
- `backup(filename)` - Backup to CSV file
- `restore(filename)` - Restore from CSV file
- `export_json(filename)` - Export to JSON
- `import_json(filename)` - Import from JSON

**Utility**
- `clear()` - Remove all entries
- `__len__()` - Get number of entries
- `__contains__(key)` - Check if key exists
- `__getitem__(key)` - Get value by key
- `__setitem__(key, value)` - Set value by key
- `__delitem__(key)` - Delete by key

##  Logging

All operations are automatically logged to `app.log`:

```python
2025-10-19 22:44:01 [INFO] Initialized B+ Tree with order: 4
2025-10-19 22:44:01 [INFO] Inserted: 10
2025-10-19 22:44:01 [INFO] Deleted: 20
2025-10-19 22:44:01 [INFO] Backup successful: backup.csv, 15 entries
```

## 📚 References

- [B+ Tree - Wikipedia](https://en.wikipedia.org/wiki/B%2B_tree)
- Database System Concepts by Silberschatz, Korth, and Sudarshan
- Modern Database Management by Hoffer, Ramesh, and Topi
